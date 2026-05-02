import re


def parse_new_lines(patch):
    changes = []
    new_line = 0
    for line in patch.split("\n"):
        if not line.strip():
            continue
        # Extract the new line number from the chunk header
        if line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            if match:
                new_line = int(match.group(1)) - 1
        # Added line
        elif line.startswith("+") and not line.startswith("+++"):
            new_line += 1
            changes.append({"line": new_line, "content": line[1:]})
        # Removed line
        elif not line.startswith("-") and not line.startswith("---"):
            continue
        # Context line
        else:
            new_line += 1
    return changes


def prepare_changed_lines_text(changed_lines):
    text = ""
    for line in changed_lines:
        text += f"{line.get('line')}: {line.get('content')}\n"
    return text


def get_new_file_line_number(file_lines, target, approx_line):
    n = len(file_lines)
    target = target.strip()
    approx_line = min(max(approx_line, 1), len(file_lines))
    for i in range(approx_line - 1, n):
        if file_lines[i].strip() == target:
            return i + 1
    for i in range(approx_line - 2, -1, -1):
        if file_lines[i].strip() == target:
            return i + 1
    return approx_line
