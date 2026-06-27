from docsync.parser.ast_parser import FileAPI, FunctionInfo, ClassInfo, MethodInfo
from docsync.diff.api_diff import APIDiff, ChangeType


def make_func(name, args, defaults=None, returns=None):
    return FunctionInfo(
        name=name, lineno=1, args=args,
        defaults=defaults or [],
        returns=returns, docstring=None, decorators=[],
    )


def test_function_added():
    old = FileAPI(file_path="mod.py", file_hash="old", functions=[], classes=[])
    current = FileAPI(file_path="mod.py", file_hash="new", functions=[make_func("predict", ["image"])], classes=[])
    diff = APIDiff()
    changes = diff.diff_file(old, current)
    added = [c for c in changes if c.type == ChangeType.FUNCTION_ADDED]
    assert len(added) == 1
    assert added[0].symbol_name == "predict"


def test_parameter_added():
    old = FileAPI(file_path="mod.py", file_hash="old",
                  functions=[make_func("predict", ["image"])], classes=[])
    current = FileAPI(file_path="mod.py", file_hash="new",
                      functions=[make_func("predict", ["image", "threshold"], ["0.5"])], classes=[])
    diff = APIDiff()
    changes = diff.diff_file(old, current)
    param_added = [c for c in changes if c.type == ChangeType.PARAMETER_ADDED]
    assert len(param_added) == 1
    assert param_added[0].details == "Parameter `threshold = 0.5` added"


def test_parameter_removed():
    old = FileAPI(file_path="mod.py", file_hash="old",
                  functions=[make_func("predict", ["image", "threshold"], ["0.5"])], classes=[])
    current = FileAPI(file_path="mod.py", file_hash="new",
                      functions=[make_func("predict", ["image"])], classes=[])
    diff = APIDiff()
    changes = diff.diff_file(old, current)
    param_removed = [c for c in changes if c.type == ChangeType.PARAMETER_REMOVED]
    assert len(param_removed) == 1
    assert param_removed[0].symbol_name == "predict"


def test_no_changes():
    func = make_func("predict", ["image"])
    old = FileAPI(file_path="mod.py", file_hash="same", functions=[func], classes=[])
    current = FileAPI(file_path="mod.py", file_hash="same", functions=[func], classes=[])
    diff = APIDiff()
    changes = diff.diff_file(old, current)
    assert len(changes) == 0
