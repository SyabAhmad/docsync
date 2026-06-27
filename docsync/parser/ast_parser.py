import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any


class FunctionInfo:
    def __init__(self, name: str, lineno: int, args: List[str], defaults: List[Optional[str]],
                 returns: Optional[str], docstring: Optional[str], decorators: List[str]):
        self.name = name
        self.lineno = lineno
        self.args = args
        self.defaults = defaults
        self.returns = returns
        self.docstring = docstring
        self.decorators = decorators

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "args": self.args,
            "defaults": self.defaults,
            "returns": self.returns,
            "docstring": self.docstring,
            "decorators": self.decorators,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FunctionInfo":
        return cls(**data)


class MethodInfo(FunctionInfo):
    pass


class ClassInfo:
    def __init__(self, name: str, lineno: int, docstring: Optional[str],
                 bases: List[str], methods: List[MethodInfo]):
        self.name = name
        self.lineno = lineno
        self.docstring = docstring
        self.bases = bases
        self.methods = methods

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "docstring": self.docstring,
            "bases": self.bases,
            "methods": [m.to_dict() for m in self.methods],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClassInfo":
        methods = [MethodInfo(**m) if isinstance(m, dict) else MethodInfo.from_dict(m) for m in data.get("methods", [])]
        data["methods"] = methods
        return cls(**data)


class FileAPI:
    def __init__(self, file_path: str, file_hash: str,
                 functions: List[FunctionInfo], classes: List[ClassInfo]):
        self.file_path = file_path
        self.file_hash = file_hash
        self.functions = functions
        self.classes = classes

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FileAPI":
        functions = [FunctionInfo(**f) if isinstance(f, dict) else FunctionInfo.from_dict(f) for f in data.get("functions", [])]
        classes_raw = data.get("classes", [])
        classes = []
        for c in classes_raw:
            if isinstance(c, dict):
                methods = [MethodInfo(**m) if isinstance(m, dict) else MethodInfo.from_dict(m) for m in c.get("methods", [])]
                c["methods"] = methods
                classes.append(ClassInfo(**c))
            else:
                classes.append(ClassInfo.from_dict(c))
        data["functions"] = functions
        data["classes"] = classes
        return cls(**data)

    def get_all_public_names(self) -> List[str]:
        names = []
        for f in self.functions:
            if not f.name.startswith("_"):
                names.append(f"function:{f.name}")
        for c in self.classes:
            if not c.name.startswith("_"):
                names.append(f"class:{c.name}")
                for m in c.methods:
                    if not m.name.startswith("_"):
                        names.append(f"method:{c.name}.{m.name}")
        return names


class ASTParser:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def parse_file(self, rel_path: Path) -> Optional[FileAPI]:
        full_path = self.repo_root / rel_path
        if not full_path.exists():
            return None
        try:
            source = full_path.read_text(encoding="utf-8")
        except Exception:
            return None
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None
        file_hash = hashlib.sha256(source.encode()).hexdigest()
        functions = []
        classes = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                info = self._extract_function(node)
                if info:
                    functions.append(info)
            elif isinstance(node, ast.ClassDef):
                info = self._extract_class(node)
                if info:
                    classes.append(info)
        return FileAPI(
            file_path=rel_path.as_posix(),
            file_hash=file_hash,
            functions=functions,
            classes=classes,
        )

    def _extract_function(self, node) -> Optional[FunctionInfo]:
        args = self._get_args(node.args)
        defaults = self._get_defaults(node.args)
        returns = ast.unparse(node.returns) if node.returns else None
        docstring = ast.get_docstring(node)
        decorators = [ast.unparse(d) for d in node.decorator_list]
        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            args=args,
            defaults=defaults,
            returns=returns,
            docstring=docstring,
            decorators=decorators,
        )

    def _extract_class(self, node: ast.ClassDef) -> Optional[ClassInfo]:
        docstring = ast.get_docstring(node)
        bases = [ast.unparse(b) for b in node.bases]
        methods = []
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._extract_function(child)
                if method:
                    m = MethodInfo(
                        name=method.name,
                        lineno=method.lineno,
                        args=method.args,
                        defaults=method.defaults,
                        returns=method.returns,
                        docstring=method.docstring,
                        decorators=method.decorators,
                    )
                    methods.append(m)
        return ClassInfo(
            name=node.name,
            lineno=node.lineno,
            docstring=docstring,
            bases=bases,
            methods=methods,
        )

    def _get_args(self, args: ast.arguments) -> List[str]:
        result = []
        for arg in args.args:
            if arg.arg == "self" or arg.arg == "cls":
                continue
            result.append(arg.arg)
        return result

    def _get_defaults(self, args: ast.arguments) -> List[Optional[str]]:
        defaults = [ast.unparse(d) for d in args.defaults]
        pos_defaults = [None] * (len(args.args) - len(defaults)) + defaults
        result = []
        for arg in args.args:
            if arg.arg == "self" or arg.arg == "cls":
                continue
            idx = len(result)
            if idx < len(pos_defaults) and pos_defaults[idx] is not None:
                result.append(pos_defaults[idx])
            else:
                result.append(None)
        return result
