from json import dumps
from pathlib import Path

from jinja2 import Template
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from data.db.config import settings
from data.dto.create_order_dto import CreateOrderDTO
from data.dto.customer_service_agent_deps import CustomerServiceAgentDeps
from data.dto.order_detail_dto import OrderDetailDTO
from data.dto.search_product_by_embedding_dto import SearchProductByEmbeddingDTO
from utils.date_utils import get_friendly_timestamp


class CustomerServiceAgent:
    def __init__(self, name: str, deps: CustomerServiceAgentDeps) -> None:
        self.name = name
        self.deps = deps

    async def get_agent_response(self, user_input: str, customer_phone: str) -> str:
        """Genera una respuesta del agente de servicio al cliente basado en LLM"""

        template_path = (
            Path(__file__).parent / "prompts" / "customer_service_system_prompt.j2"
        )
        template_text = template_path.read_text(encoding="utf-8")
        available_products = await self.deps.product_service.get_all_products(
            only_available=True
        )
        embedding_result = await self.deps.product_service.embedder.embed_query(
            user_input
        )
        semantic_results = await self.deps.product_service.product_vector_search(
            SearchProductByEmbeddingDTO(
                query_embedding=embedding_result.embeddings[0],
                top_k=5,
                only_available=True,
            )
        )

        friendly_date = get_friendly_timestamp()

        system_prompt = Template(template_text).render(
            name=self.name,
            customer_message=user_input,
            semantic_context=dumps(
                [item.model_dump() for item in semantic_results],
                ensure_ascii=False,
            ),
            available_products=dumps(
                [item.model_dump() for item in available_products],
                ensure_ascii=False,
            ),
            current_datetime=friendly_date,
        )

        # Configuramos el modelo explícitamente usando la API Key de settings
        provider = GoogleProvider(api_key=settings.google_api_key)

        model = GoogleModel(
            model_name="gemini-1.5-pro",
            provider=provider,
        )

        agent: Agent[CustomerServiceAgentDeps, str] = Agent(
            model=model,
            name=self.name,
            system_prompt=system_prompt,
            deps_type=CustomerServiceAgentDeps,
            tools=[self.create_order_tool],
        )

        message_history = await self.deps.chat_service.get_history(customer_phone)

        response = await agent.run(
            user_input,
            message_history=message_history,
            deps=self.deps,
        )

        await self.deps.chat_service.save_conversation(
            customer_phone,
            message_history + response.new_messages(),
        )

        return response.output

    async def create_order_tool(
        self, ctx: RunContext[CustomerServiceAgentDeps], order_data: CreateOrderDTO
    ) -> str:
        """
        Herramienta Crítica para finalizar la venta: Registra el pedido en la base de datos.

        REGLAS DE USO:
        1. SOLO LLAMAR cuando el cliente haya dicho "SÍ" o confirmado explícitamente el resumen final.
        2. Verifica que tienes TODOS los datos: Dirección exacta, items, cantidades y método de pago.
        3. El `total_amount` debe ser la suma exacta de los precios en el inventario disponible.

        No asumas datos. Si falta la dirección o el método de pago, PREGUNTA antes de llamar.
        """
        try:
            result: OrderDetailDTO = await ctx.deps.order_service.create_order(
                order_data
            )
            return f"Pedido creado exitosamente. Detalles: {result.model_dump_json()}"
        except Exception as e:
            return f"Error al crear el pedido: {e!s}"
