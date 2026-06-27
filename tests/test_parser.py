import tempfile
from pathlib import Path
from docsync.parser.ast_parser import ASTParser, FunctionInfo, ClassInfo, FileAPI


SAMPLE_CODE = '''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello {name}"


def add(a: int, b: int = 0) -> int:
    """Add two numbers."""
    return a + b


class Calculator:
    """A simple calculator."""

    def __init__(self, precision: int = 2):
        self.precision = precision

    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers."""
        return round(x * y, self.precision)
'''


def test_parse_functions():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        file_path = root / "calc.py"
        file_path.write_text(SAMPLE_CODE)

        parser = ASTParser(root)
        api = parser.parse_file(Path("calc.py"))

        assert api is not None
        assert api.file_path == "calc.py"
        assert len(api.functions) == 2
        assert len(api.classes) == 1

        func_names = {f.name for f in api.functions}
        assert "hello" in func_names
        assert "add" in func_names

        hello = next(f for f in api.functions if f.name == "hello")
        assert hello.args == ["name"]
        assert hello.returns == "str"
        assert hello.docstring == "Say hello."

        add = next(f for f in api.functions if f.name == "add")
        assert add.args == ["a", "b"]
        assert add.defaults == [None, "0"]

        calc = api.classes[0]
        assert calc.name == "Calculator"
        assert calc.docstring == "A simple calculator."
        assert len(calc.methods) == 2  # __init__ and multiply

        multiply = next(m for m in calc.methods if m.name == "multiply")
        assert multiply.args == ["x", "y"]
        assert multiply.returns == "float"


def test_parse_private_skipped():
    code = '''
def _private():
    pass

class _Hidden:
    pass
'''
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        file_path = root / "private.py"
        file_path.write_text(code)

        parser = ASTParser(root)
        api = parser.parse_file(Path("private.py"))
        assert api is not None
        assert len(api.functions) == 1
        assert len(api.classes) == 1
