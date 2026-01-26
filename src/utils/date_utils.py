from datetime import datetime


def get_friendly_timestamp() -> str:
    """
    Retorna la fecha y hora actual en un formato amigable y en español.
    Ej: "Martes 02 de Febrero del 2026 - Hora 14:02"
    """

    now = datetime.now()  # Usa hora local
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    months = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    return (
        f"{days[now.weekday()]} {now.day} de {months[now.month - 1]} del {now.year} "
        f"- Hora {now.strftime('%H:%M')}"
    )
