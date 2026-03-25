from __future__ import annotations

import argparse
import keyword
import re
from dataclasses import dataclass
from pathlib import Path


DEF_START_PATTERN = re.compile(r"^(\s*)def\s+([^\s(]+)\s*\(")
CLASS_PATTERN = re.compile(r"^(\s*)class\s+([^\s(:]+)(.*)$")
SIMPLE_TARGET_PATTERN = re.compile(
    r"^(\s*)([A-Za-z_][A-Za-z0-9_]*|None|True|False)\s*([:=])(.*)$"
)
ATTRIBUTE_ANNOTATION_PATTERN = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$")
SELF_STAR_IMPORT_PATTERN = re.compile(r"^from \.\.([A-Za-z0-9_]+) import \*\s*$")
SUPPORTED_SOURCE_SUFFIXES = {".py", ".pyi"}


@dataclass
class FileStats:
    files_written: int = 0
    syntax_valid_files: int = 0
    syntax_invalid_files: int = 0
    function_headers_collapsed: int = 0
    overloads_added: int = 0
    staticmethods_added: int = 0
    properties_promoted: int = 0
    identifiers_renamed: int = 0
    annotation_rewrites: int = 0
    self_imports_removed: int = 0

    def merge(self, other: "FileStats") -> None:
        self.files_written += other.files_written
        self.syntax_valid_files += other.syntax_valid_files
        self.syntax_invalid_files += other.syntax_invalid_files
        self.function_headers_collapsed += other.function_headers_collapsed
        self.overloads_added += other.overloads_added
        self.staticmethods_added += other.staticmethods_added
        self.properties_promoted += other.properties_promoted
        self.identifiers_renamed += other.identifiers_renamed
        self.annotation_rewrites += other.annotation_rewrites
        self.self_imports_removed += other.self_imports_removed


def is_keyword_name(name: str) -> bool:
    return keyword.iskeyword(name)


def sanitize_identifier(name: str, *, keep_last_segment: bool = False) -> str:
    if keep_last_segment and "." in name:
        name = name.rsplit(".", 1)[-1]

    cleaned = re.sub(r"[^0-9A-Za-z_]", "_", name)
    if not cleaned:
        cleaned = "_"
    if cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    if is_keyword_name(cleaned):
        cleaned = f"{cleaned}_"
    return cleaned


def normalize_annotation_text(text: str) -> tuple[str, int]:
    normalized = text
    rewrite_count = 0

    normalized, count = re.subn(r"typing\.List\[\s*([A-Za-z0-9_.]+)\[\]\s*\]", r"typing.List[\1]", normalized)
    rewrite_count += count
    normalized, count = re.subn(r"(?<!\.)\bany\b", "typing.Any", normalized)
    rewrite_count += count
    return normalized, rewrite_count


def split_top_level(text: str, separator: str = ",") -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string: str | None = None
    escape = False

    for char in text:
        if in_string:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue

        if char in {"'", '"'}:
            current.append(char)
            in_string = char
            continue

        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1

        if (
            char == separator
            and paren_depth == 0
            and bracket_depth == 0
            and brace_depth == 0
        ):
            parts.append("".join(current))
            current = []
            continue

        current.append(char)

    parts.append("".join(current))
    return parts


def sanitize_parameter(segment: str) -> tuple[str, int, int]:
    stripped = segment.strip()
    if not stripped:
        return "", 0, 0
    if stripped in {"/", "*"}:
        return stripped, 0, 0

    prefix = ""
    remainder = stripped
    if remainder.startswith("**"):
        prefix = "**"
        remainder = remainder[2:]
    elif remainder.startswith("*"):
        prefix = "*"
        remainder = remainder[1:]

    match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*|None|True|False)(.*)$", remainder, re.S)
    if not match:
        normalized, rewrite_count = normalize_annotation_text(stripped)
        return normalized, 0, rewrite_count

    raw_name = match.group(1)
    tail = match.group(2)
    clean_name = sanitize_identifier(raw_name)
    rename_count = int(clean_name != raw_name)
    clean_tail, rewrite_count = normalize_annotation_text(tail)
    return f"{prefix}{clean_name}{clean_tail}", rename_count, rewrite_count


def sanitize_parameter_list(text: str) -> tuple[str, int, int]:
    parts = split_top_level(text)
    cleaned_parts: list[str] = []
    rename_count = 0
    any_count = 0
    seen_names: dict[str, int] = {}

    for part in parts:
        cleaned, renamed, fixed_any = sanitize_parameter(part)
        if cleaned:
            param_match = re.match(r"^(\*{0,2})([A-Za-z_][A-Za-z0-9_]*)(.*)$", cleaned)
            if param_match and cleaned not in {"/", "*"}:
                prefix = param_match.group(1)
                param_name = param_match.group(2)
                suffix = param_match.group(3)
                occurrence = seen_names.get(param_name, 0)
                if occurrence:
                    param_name = f"{param_name}_{occurrence + 1}"
                    cleaned = f"{prefix}{param_name}{suffix}"
                    renamed += 1
                seen_names[param_match.group(2)] = occurrence + 1
            cleaned_parts.append(cleaned)
        rename_count += renamed
        any_count += fixed_any

    return ", ".join(cleaned_parts), rename_count, any_count


def first_parameter_name(parameter_text: str) -> str | None:
    parameters = [part.strip() for part in split_top_level(parameter_text) if part.strip() and part.strip() not in {"/", "*"}]
    if not parameters:
        return None

    match = re.match(r"^\*{0,2}([A-Za-z_][A-Za-z0-9_]*)", parameters[0])
    if not match:
        return None
    return match.group(1)


def split_parameter_names(parameter_text: str) -> list[str]:
    names: list[str] = []
    for part in split_top_level(parameter_text):
        stripped = part.strip()
        if not stripped or stripped in {"/", "*"}:
            continue
        match = re.match(r"^\*{0,2}([A-Za-z_][A-Za-z0-9_]*)", stripped)
        if match:
            names.append(match.group(1))
    return names


def parse_single_line_def(line: str) -> tuple[str, str, str, str | None] | None:
    match = DEF_START_PATTERN.match(line)
    if not match:
        return None

    indent = match.group(1)
    name = match.group(2)
    open_paren = line.find("(", match.end(2) - 1)
    close_paren = line.rfind(")")
    if open_paren == -1 or close_paren == -1 or close_paren < open_paren:
        return None

    parameter_text = line[open_paren + 1 : close_paren]
    tail = line[close_paren + 1 :].strip()
    return_annotation: str | None = None
    if tail.startswith("->"):
        return_annotation = tail[2:].split(":", 1)[0].strip()

    return indent, name, parameter_text, return_annotation


def is_singleton_static_getter(current_class: str | None, name: str, parameter_text: str, return_annotation: str | None) -> bool:
    if not current_class or not return_annotation:
        return False

    parameter_names = split_parameter_names(parameter_text)
    if parameter_names != ["self"]:
        return False

    normalized_return = return_annotation.strip().strip('"')
    return name == f"Get{current_class}" and normalized_return == current_class


def signature_complete(text: str) -> bool:
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string: str | None = None
    escape = False

    for char in text:
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue

        if char in {"'", '"'}:
            in_string = char
            continue

        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        elif char == ":" and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
            return True

    return False


def find_matching_paren(text: str, start_index: int) -> int:
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string: str | None = None
    escape = False

    for index in range(start_index, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue

        if char in {"'", '"'}:
            in_string = char
            continue

        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
            if paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
                return index
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1

    raise ValueError("Could not find matching closing parenthesis for function signature")


def collect_function_block(lines: list[str], start_index: int) -> tuple[list[str], int]:
    collected: list[str] = []
    index = start_index
    combined = ""
    function_indent = indentation_width(lines[start_index])

    while index < len(lines):
        part = lines[index].rstrip("\r\n")
        collected.append(part)
        combined = f"{combined}\n{part}" if combined else part
        index += 1
        if signature_complete(combined):
            break

    while index < len(lines):
        candidate = lines[index]
        if candidate.strip() and indentation_width(candidate) <= function_indent:
            break
        if candidate.strip() and indentation_width(candidate) > function_indent:
            index += 1
            continue
        if not candidate.strip() and index + 1 < len(lines) and indentation_width(lines[index + 1]) > function_indent:
            index += 1
            continue
        break

    return collected, index


def sanitize_function_block(header_lines: list[str]) -> tuple[str, int, int, str | None]:
    header = " ".join(part.strip() for part in header_lines)
    first_line_match = DEF_START_PATTERN.match(header_lines[0])
    if not first_line_match:
        raise ValueError(f"Unrecognized function signature: {header}")

    indent = first_line_match.group(1)
    raw_name = first_line_match.group(2)
    name = sanitize_identifier(raw_name)
    rename_count = int(name != raw_name)

    open_paren = header.find("(", header.find(raw_name) + len(raw_name))
    close_paren = find_matching_paren(header, open_paren)
    parameter_text = header[open_paren + 1 : close_paren]
    clean_parameters, renamed_parameters, annotation_rewrites = sanitize_parameter_list(parameter_text)
    rename_count += renamed_parameters
    first_param = first_parameter_name(clean_parameters)

    tail = header[close_paren + 1 :].strip()
    return_text = ""
    if tail.startswith("->"):
        return_annotation = tail[2:].split(":", 1)[0].strip()
        clean_return, return_rewrites = normalize_annotation_text(return_annotation)
        return_text = f" -> {clean_return}"
        annotation_rewrites += return_rewrites

    return f"{indent}def {name}({clean_parameters}){return_text}: ...\n", rename_count, annotation_rewrites, first_param


def sanitize_class_line(line: str) -> tuple[str, int]:
    match = CLASS_PATTERN.match(line.rstrip("\r\n"))
    if not match:
        return line, 0

    indent = match.group(1)
    raw_name = match.group(2)
    remainder = match.group(3)
    clean_name = sanitize_identifier(raw_name, keep_last_segment=True)
    renamed = int(clean_name != raw_name)
    line_ending = "\n" if line.endswith("\n") else ""
    return f"{indent}class {clean_name}{remainder}{line_ending}", renamed


def sanitize_simple_target_line(line: str) -> tuple[str, int, int]:
    stripped = line.lstrip()
    if stripped.startswith(("def ", "class ", "from ", "import ", "@")):
        return line, 0, 0

    match = SIMPLE_TARGET_PATTERN.match(line.rstrip("\r\n"))
    if not match:
        return line, 0, 0

    indent = match.group(1)
    raw_name = match.group(2)
    separator = match.group(3)
    remainder = match.group(4)
    clean_name = sanitize_identifier(raw_name)
    renamed = int(clean_name != raw_name)
    fixed_any = 0
    if separator == ":":
        remainder, fixed_any = normalize_annotation_text(remainder)

    line_ending = "\n" if line.endswith("\n") else ""
    return f"{indent}{clean_name}{separator}{remainder}{line_ending}", renamed, fixed_any


def add_overload_decorators(lines: list[str], stats: FileStats) -> list[str]:
    decorated: list[str] = []
    index = 0

    while index < len(lines):
        match = DEF_START_PATTERN.match(lines[index])
        if not match:
            decorated.append(lines[index])
            index += 1
            continue

        indent = match.group(1)
        name = match.group(2)
        run_end = index + 1
        while run_end < len(lines):
            other = DEF_START_PATTERN.match(lines[run_end])
            if not other or other.group(1) != indent or other.group(2) != name:
                break
            run_end += 1

        if run_end - index > 1:
            for def_index in range(index, run_end):
                decorated.append(f"{indent}@typing.overload\n")
                decorated.append(lines[def_index])
                stats.overloads_added += 1
            index = run_end
            continue

        decorated.append(lines[index])
        index += 1

    return decorated


def add_staticmethod_decorators(lines: list[str], stats: FileStats) -> list[str]:
    decorated: list[str] = []
    class_stack: list[tuple[int, str]] = []

    for line in lines:
        class_match = CLASS_PATTERN.match(line.rstrip("\r\n"))
        if class_match:
            class_indent = indentation_width(line)
            while class_stack and class_indent <= class_stack[-1][0]:
                class_stack.pop()
            class_stack.append((class_indent, class_match.group(2)))
            decorated.append(line)
            continue

        if class_stack and line.strip():
            current_indent = indentation_width(line)
            while class_stack and current_indent <= class_stack[-1][0]:
                class_stack.pop()

        parsed = parse_single_line_def(line)
        if not parsed:
            decorated.append(line)
            continue

        indent, name, parameter_text, return_annotation = parsed
        if not indent:
            decorated.append(line)
            continue

        if decorated and decorated[-1].strip() == "@staticmethod":
            decorated.append(line)
            continue

        first_param = first_parameter_name(parameter_text)
        current_class = class_stack[-1][1] if class_stack else None
        if is_singleton_static_getter(current_class, name, parameter_text, return_annotation):
            decorated.append(f"{indent}@staticmethod\n")
            rewritten_line = line.replace("(self)", "()", 1)
            decorated.append(rewritten_line)
            stats.staticmethods_added += 1
            continue

        if first_param not in {"self", "cls"}:
            decorated.append(f"{indent}@staticmethod\n")
            stats.staticmethods_added += 1

        decorated.append(line)

    return decorated


def indentation_width(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def add_empty_class_bodies(lines: list[str]) -> list[str]:
    completed: list[str] = []

    for index, line in enumerate(lines):
        completed.append(line)
        match = CLASS_PATTERN.match(line.rstrip("\r\n"))
        if not match:
            continue

        class_indent = indentation_width(line)
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1

        if next_index >= len(lines) or indentation_width(lines[next_index]) <= class_indent:
            completed.append(f"{match.group(1)}    ...\n")

    return completed


def promote_annotated_members_to_properties(lines: list[str], stats: FileStats) -> list[str]:
    rewritten: list[str] = []
    class_stack: list[tuple[int, bool]] = []

    for line in lines:
        stripped = line.strip()
        class_match = CLASS_PATTERN.match(line.rstrip("\r\n"))
        if class_match:
            class_indent = indentation_width(line)
            while class_stack and class_indent <= class_stack[-1][0]:
                class_stack.pop()

            is_enum = "enum.Enum" in class_match.group(3)
            class_stack.append((class_indent, is_enum))
            rewritten.append(line)
            continue

        if class_stack and stripped:
            current_indent = indentation_width(line)
            while class_stack and current_indent <= class_stack[-1][0]:
                class_stack.pop()

        if not class_stack:
            rewritten.append(line)
            continue

        if not stripped:
            rewritten.append(line)
            continue

        class_indent, is_enum = class_stack[-1]
        if is_enum or indentation_width(line) != class_indent + 4:
            rewritten.append(line)
            continue

        if stripped.startswith(("def ", "class ", "@", "from ", "import ")):
            rewritten.append(line)
            continue

        attribute_match = ATTRIBUTE_ANNOTATION_PATTERN.match(line.rstrip("\r\n"))
        if not attribute_match:
            rewritten.append(line)
            continue

        name = attribute_match.group(2)
        annotation = attribute_match.group(3).strip()
        if annotation.startswith(("typing.ClassVar[", "ClassVar[")):
            rewritten.append(line)
            continue

        indent = attribute_match.group(1)
        rewritten.append(f"{indent}@property\n")
        rewritten.append(f"{indent}def {name}(self) -> {annotation}: ...\n")
        rewritten.append(f"{indent}@{name}.setter\n")
        rewritten.append(f"{indent}def {name}(self, value: {annotation}) -> None: ...\n")
        stats.properties_promoted += 1

    return rewritten


def ensure_typing_import(lines: list[str]) -> list[str]:
    needs_typing = any("typing." in line for line in lines)
    has_typing_import = any(line.startswith("import typing") for line in lines)
    if not needs_typing or has_typing_import:
        return lines

    insert_at = 0
    while insert_at < len(lines) and lines[insert_at].startswith("from __future__ import"):
        insert_at += 1
    return lines[:insert_at] + ["import typing\n"] + lines[insert_at:]


def clean_file(source_text: str, source_path: Path) -> tuple[str, FileStats]:
    stats = FileStats()
    lines = source_text.splitlines(keepends=True)
    cleaned: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        self_import = SELF_STAR_IMPORT_PATTERN.match(stripped)
        if self_import and source_path.parent.name == self_import.group(1):
            stats.self_imports_removed += 1
            index += 1
            continue

        if DEF_START_PATTERN.match(line):
            block, next_index = collect_function_block(lines, index)
            rewritten, renamed, fixed_any, _ = sanitize_function_block(block)
            cleaned.append(rewritten)
            stats.function_headers_collapsed += 1
            stats.identifiers_renamed += renamed
            stats.annotation_rewrites += fixed_any
            index = next_index
            continue

        class_line, class_renamed = sanitize_class_line(line)
        stats.identifiers_renamed += class_renamed
        target_line, target_renamed, fixed_any = sanitize_simple_target_line(class_line)
        stats.identifiers_renamed += target_renamed
        stats.annotation_rewrites += fixed_any
        cleaned.append(target_line)
        index += 1

    cleaned = add_overload_decorators(cleaned, stats)
    cleaned = add_staticmethod_decorators(cleaned, stats)
    cleaned = promote_annotated_members_to_properties(cleaned, stats)
    cleaned = add_empty_class_bodies(cleaned)
    cleaned = ensure_typing_import(cleaned)
    return "".join(cleaned), stats


def output_path_for(source_root: Path, output_root: Path, source_file: Path) -> Path:
    relative = source_file.relative_to(source_root)
    return (output_root / relative).with_suffix(".pyi")


def iter_source_files(source_root: Path) -> list[Path]:
    return sorted(path for path in source_root.rglob("*") if path.is_file() and path.suffix in SUPPORTED_SOURCE_SUFFIXES)


def clean_tree(source_root: Path, output_root: Path, *, validate: bool) -> tuple[FileStats, list[str]]:
    stats = FileStats()
    invalid_outputs: list[str] = []

    for source_file in iter_source_files(source_root):
        source_text = source_file.read_text(encoding="utf-8")
        cleaned_text, file_stats = clean_file(source_text, source_file)
        output_file = output_path_for(source_root, output_root, source_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(cleaned_text, encoding="utf-8", newline="\n")
        file_stats.files_written += 1

        if validate:
            try:
                compile(cleaned_text, str(output_file), "exec")
                file_stats.syntax_valid_files += 1
            except SyntaxError as exc:
                file_stats.syntax_invalid_files += 1
                invalid_outputs.append(f"{output_file}: {exc.lineno}:{exc.offset} {exc.msg}")

        stats.merge(file_stats)

    return stats, invalid_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert generated NXOpen Python files into sanitized .pyi stubs for Pylance."
    )
    parser.add_argument("source", type=Path, help="Root directory containing generated NXOpen .py files")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output root for cleaned .pyi files. Defaults to <source>_pyi.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip compile-based syntax validation of generated .pyi files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = args.source.resolve()
    output_root = args.output.resolve() if args.output else source_root.with_name(f"{source_root.name}_pyi")

    if not source_root.exists() or not source_root.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_root}")

    stats, invalid_outputs = clean_tree(source_root, output_root, validate=not args.no_validate)

    print(f"source={source_root}")
    print(f"output={output_root}")
    print(f"files_written={stats.files_written}")
    print(f"syntax_valid_files={stats.syntax_valid_files}")
    print(f"syntax_invalid_files={stats.syntax_invalid_files}")
    print(f"function_headers_collapsed={stats.function_headers_collapsed}")
    print(f"overloads_added={stats.overloads_added}")
    print(f"staticmethods_added={stats.staticmethods_added}")
    print(f"properties_promoted={stats.properties_promoted}")
    print(f"identifiers_renamed={stats.identifiers_renamed}")
    print(f"annotation_rewrites={stats.annotation_rewrites}")
    print(f"self_imports_removed={stats.self_imports_removed}")

    if invalid_outputs:
        print("invalid_outputs=")
        for item in invalid_outputs[:50]:
            print(item)

    return 0 if not invalid_outputs else 1


if __name__ == "__main__":
    raise SystemExit(main())