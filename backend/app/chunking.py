import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())

LANGUAGE_MAP = {
    "py": PY_LANGUAGE,
    "js": JS_LANGUAGE,
    "jsx": JS_LANGUAGE,
}

CHUNK_NODE_TYPES = {
    "py": {"function_definition", "class_definition"},
    "js": {"function_declaration", "class_declaration", "method_definition"},
    "jsx": {"function_declaration", "class_declaration", "method_definition"},
}

def chunk_file(content: str, language: str) -> list[dict]:
    if language not in LANGUAGE_MAP:
        return []

    parser = Parser(LANGUAGE_MAP[language])
    tree = parser.parse(bytes(content, "utf-8"))

    chunks = []
    node_types = CHUNK_NODE_TYPES[language]

    def walk(node):
        if node.type in node_types:
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else None
            chunks.append({
                "content": node.text.decode("utf-8"),
                "chunk_type": node.type,
                "name": name,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
            })
        else:
            for child in node.children:
                walk(child)

    walk(tree.root_node)

    if not chunks:
        line_count = content.count("\n") + 1
        chunks.append({
            "content": content,
            "chunk_type": "module",
            "name": None,
            "start_line": 1,
            "end_line": line_count,
        })

    return chunks