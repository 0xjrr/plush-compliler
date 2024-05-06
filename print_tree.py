import ast_nodes

def pretty_print(node, indent=0):
    """
    Pretty prints the parsed AST node with proper indentation.
    """
    if isinstance(node, ast_nodes.Program):
        print("Program(")
        pretty_print(node.declarations, indent + 1)
        print(")")
    elif isinstance(node, list):
        for item in node:
            pretty_print(item, indent)
    elif hasattr(node, "__dict__"):
        node_name = type(node).__name__
        print("  " * indent + node_name + "(")
        for key, value in node.__dict__.items():
            print("  " * (indent + 1) + f"{key} =", end=" ")
            pretty_print(value, indent + 1)
        print("  " * indent + ")")
    else:
        print("  " * indent + repr(node))