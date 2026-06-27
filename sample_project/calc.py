def hello(name: str) -> str:
    """Say hello."""
    return f"Hello {name}"


def goodbye(name: str) -> str:
    """Say goodbye."""
    return f"Goodbye {name}"


class Calculator:
    """A simple calculator."""

    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers."""
        return x * y

    def divide(self, a: float, b: float, precision: int = 2) -> float:
        """Divide two numbers with precision."""
        return round(a / b, precision)
