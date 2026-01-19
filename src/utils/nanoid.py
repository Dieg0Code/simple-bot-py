from nanoid import generate


def generate_order_code(size: int = 6) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    return generate(alphabet=alphabet, size=size)