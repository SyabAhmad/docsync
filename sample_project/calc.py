def hello(name: str, greeting: str = "Hello") -> str:
    """Say hello with a custom greeting."""
    return f"{greeting} {name}"


def add(a: int, b: int = 0) -> int:
    """Add two numbers."""
    return a + b


class Calculator:
    """A simple calculator."""

    def multiply(self, x: float, y: float, precision: int = 2) -> float:
        """Multiply two numbers with precision."""
        return round(x * y, precision)
