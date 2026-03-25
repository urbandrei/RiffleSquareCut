"""ASCII table formatting for Discord code blocks."""


def ascii_table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a fixed-width ASCII table wrapped in a code block."""
    if not rows:
        return "```\nNo data.\n```"

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Build header
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_row = "|" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(headers)) + "|"

    lines = [sep, header_row, sep]
    for row in rows:
        data_row = "|" + "|".join(
            f" {str(cell):<{widths[i]}} " for i, cell in enumerate(row)
        ) + "|"
        lines.append(data_row)
    lines.append(sep)

    return "```\n" + "\n".join(lines) + "\n```"
