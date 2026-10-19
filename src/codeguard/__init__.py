"""Code Guard: detect and repair security vulnerabilities in LLM-generated Python code."""

__version__ = "0.0.1"

#: The five vulnerability classes plus ``safe``. This order is the canonical label order
#: used everywhere (static mapping, classifier head, fusion, reports).
CLASSES: tuple[str, ...] = (
    "sql_injection",
    "xss",
    "command_injection",
    "path_traversal",
    "code_execution",
    "safe",
)
