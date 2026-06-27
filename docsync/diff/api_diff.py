from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path

from docsync.parser.ast_parser import FileAPI, FunctionInfo, ClassInfo


class ChangeType(Enum):
    FUNCTION_ADDED = "function_added"
    FUNCTION_REMOVED = "function_removed"
    FUNCTION_MODIFIED = "function_modified"
    CLASS_ADDED = "class_added"
    CLASS_REMOVED = "class_removed"
    CLASS_MODIFIED = "class_modified"
    METHOD_ADDED = "method_added"
    METHOD_REMOVED = "method_removed"
    METHOD_MODIFIED = "method_modified"
    PARAMETER_ADDED = "parameter_added"
    PARAMETER_REMOVED = "parameter_removed"
    PARAMETER_MODIFIED = "parameter_modified"
    FILE_ADDED = "file_added"
    FILE_REMOVED = "file_removed"
    FILE_MODIFIED = "file_modified"


@dataclass
class Change:
    type: ChangeType
    file_path: str
    symbol_name: str
    details: str = ""
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "file_path": self.file_path,
            "symbol_name": self.symbol_name,
            "details": self.details,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }

    def __str__(self) -> str:
        symbol = f" :: {self.symbol_name}" if self.symbol_name else ""
        return f"[{self.type.value}] {self.file_path}{symbol} - {self.details}"


@dataclass
class DiffResult:
    changes: List[Change] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def group_by_file(self) -> Dict[str, List[Change]]:
        grouped = {}
        for c in self.changes:
            grouped.setdefault(c.file_path, []).append(c)
        return grouped

    def to_text(self) -> str:
        if not self.changes:
            return "No API changes detected."
        lines = ["## API Changes Detected", ""]
        for file_path, file_changes in self.group_by_file().items():
            lines.append(f"### {file_path}")
            for c in file_changes:
                lines.append(f"  {c}")
            lines.append("")
        return "\n".join(lines)


class APIDiff:
    def diff_file(self, old: Optional[FileAPI], current: FileAPI) -> List[Change]:
        changes = []
        if old is None:
            changes.append(Change(
                type=ChangeType.FILE_ADDED,
                file_path=current.file_path,
                symbol_name="",
                details="File added",
            ))
            for f in current.functions:
                if not f.name.startswith("_"):
                    changes.append(self._function_added(current.file_path, f))
            for c in current.classes:
                if not c.name.startswith("_"):
                    changes.extend(self._class_added(current.file_path, c))
            return changes

        if old.file_hash != current.file_hash:
            changes.append(Change(
                type=ChangeType.FILE_MODIFIED,
                file_path=current.file_path,
                symbol_name="",
                details="File modified",
            ))

        old_funcs = {f.name: f for f in old.functions}
        cur_funcs = {f.name: f for f in current.functions}

        for name, func in cur_funcs.items():
            if name.startswith("_"):
                continue
            if name not in old_funcs:
                changes.append(self._function_added(current.file_path, func))
            else:
                changes.extend(self._diff_functions(current.file_path, old_funcs[name], func))

        for name, func in old_funcs.items():
            if name.startswith("_"):
                continue
            if name not in cur_funcs:
                changes.append(Change(
                    type=ChangeType.FUNCTION_REMOVED,
                    file_path=current.file_path,
                    symbol_name=name,
                    details="Function removed",
                ))

        old_classes = {c.name: c for c in old.classes}
        cur_classes = {c.name: c for c in current.classes}

        for name, cls in cur_classes.items():
            if name.startswith("_"):
                continue
            if name not in old_classes:
                changes.extend(self._class_added(current.file_path, cls))
            else:
                changes.extend(self._diff_classes(current.file_path, old_classes[name], cls))

        for name, cls in old_classes.items():
            if name.startswith("_"):
                continue
            if name not in cur_classes:
                changes.append(Change(
                    type=ChangeType.CLASS_REMOVED,
                    file_path=current.file_path,
                    symbol_name=name,
                    details="Class removed",
                ))

        return changes

    def _function_added(self, file_path: str, func: FunctionInfo) -> Change:
        args_str = ", ".join(func.args)
        default_count = len(func.defaults)
        details = f"Added `{func.name}({args_str})`"
        if default_count:
            details += f" ({default_count} default(s))"
        return Change(
            type=ChangeType.FUNCTION_ADDED,
            file_path=file_path,
            symbol_name=func.name,
            details=details,
        )

    def _class_added(self, file_path: str, cls: ClassInfo) -> List[Change]:
        changes = [Change(
            type=ChangeType.CLASS_ADDED,
            file_path=file_path,
            symbol_name=cls.name,
            details=f"Added class `{cls.name}`",
        )]
        for m in cls.methods:
            if not m.name.startswith("_"):
                args_str = ", ".join(m.args)
                changes.append(Change(
                    type=ChangeType.METHOD_ADDED,
                    file_path=file_path,
                    symbol_name=f"{cls.name}.{m.name}",
                    details=f"Added method `{m.name}({args_str})`",
                ))
        return changes

    def _diff_functions(self, file_path: str, old: FunctionInfo, cur: FunctionInfo) -> List[Change]:
        changes = []
        old_padded = [None] * (len(old.args) - len(old.defaults)) + list(old.defaults)
        cur_padded = [None] * (len(cur.args) - len(cur.defaults)) + list(cur.defaults)
        old_args = dict(zip(old.args, old_padded))
        cur_args = dict(zip(cur.args, cur_padded))

        for name, default in cur_args.items():
            if name not in old_args:
                default_str = f" = {default}" if default else ""
                changes.append(Change(
                    type=ChangeType.PARAMETER_ADDED,
                    file_path=file_path,
                    symbol_name=cur.name,
                    details=f"Parameter `{name}{default_str}` added",
                    new_value=default,
                ))

        for name, default in old_args.items():
            if name not in cur_args:
                changes.append(Change(
                    type=ChangeType.PARAMETER_REMOVED,
                    file_path=file_path,
                    symbol_name=cur.name,
                    details=f"Parameter `{name}` removed",
                    old_value=default,
                ))

        for name in old_args:
            if name in cur_args and old_args[name] != cur_args[name]:
                changes.append(Change(
                    type=ChangeType.PARAMETER_MODIFIED,
                    file_path=file_path,
                    symbol_name=cur.name,
                    details=f"Parameter `{name}` default changed",
                    old_value=old_args[name],
                    new_value=cur_args[name],
                ))

        if old.returns != cur.returns:
            changes.append(Change(
                type=ChangeType.FUNCTION_MODIFIED,
                file_path=file_path,
                symbol_name=cur.name,
                details=f"Return type changed: `{old.returns}` → `{cur.returns}`",
                old_value=old.returns,
                new_value=cur.returns,
            ))

        return changes

    def _diff_classes(self, file_path: str, old: ClassInfo, cur: ClassInfo) -> List[Change]:
        changes = []
        if old.bases != cur.bases:
            changes.append(Change(
                type=ChangeType.CLASS_MODIFIED,
                file_path=file_path,
                symbol_name=cur.name,
                details=f"Bases changed: {old.bases} → {cur.bases}",
                old_value=str(old.bases),
                new_value=str(cur.bases),
            ))

        old_methods = {m.name: m for m in old.methods}
        cur_methods = {m.name: m for m in cur.methods}

        for name, method in cur_methods.items():
            if name.startswith("_"):
                continue
            if name not in old_methods:
                args_str = ", ".join(method.args)
                changes.append(Change(
                    type=ChangeType.METHOD_ADDED,
                    file_path=file_path,
                    symbol_name=f"{cur.name}.{name}",
                    details=f"Added method `{name}({args_str})`",
                ))
            else:
                changes.extend(self._diff_functions_method(file_path, cur.name, old_methods[name], method))

        for name, method in old_methods.items():
            if name.startswith("_"):
                continue
            if name not in cur_methods:
                changes.append(Change(
                    type=ChangeType.METHOD_REMOVED,
                    file_path=file_path,
                    symbol_name=f"{cur.name}.{name}",
                    details=f"Method `{name}` removed",
                ))

        return changes

    def _diff_functions_method(self, file_path: str, class_name: str, old: FunctionInfo, cur: FunctionInfo) -> List[Change]:
        changes = []
        old_padded = [None] * (len(old.args) - len(old.defaults)) + list(old.defaults)
        cur_padded = [None] * (len(cur.args) - len(cur.defaults)) + list(cur.defaults)
        old_args = dict(zip(old.args, old_padded))
        cur_args = dict(zip(cur.args, cur_padded))

        for name, default in cur_args.items():
            if name not in old_args:
                default_str = f" = {default}" if default else ""
                changes.append(Change(
                    type=ChangeType.PARAMETER_ADDED,
                    file_path=file_path,
                    symbol_name=f"{class_name}.{cur.name}",
                    details=f"Parameter `{name}{default_str}` added to `{cur.name}`",
                    new_value=default,
                ))

        for name, default in old_args.items():
            if name not in cur_args:
                changes.append(Change(
                    type=ChangeType.PARAMETER_REMOVED,
                    file_path=file_path,
                    symbol_name=f"{class_name}.{cur.name}",
                    details=f"Parameter `{name}` removed from `{cur.name}`",
                    old_value=default,
                ))

        return changes
