def print_tree(node, indent=0):
    if isinstance(node, tuple):
        print('  ' * indent + node[0])
        for item in node[1:]:
            print_tree(item, indent + 1)
    elif isinstance(node, list):
        for item in node:
            print_tree(item, indent)
    elif isinstance(node, str):
        print('  ' * indent + node)
    elif isinstance(node, tuple) and len(node) == 5:
        print('  ' * indent + f'{node[0]}: {node[2]} {node[3]} = {node[4]}')
    elif isinstance(node, tuple) and len(node) == 3:
        print('  ' * indent + f'{node[0]}: {node[1]} {node[2]}')
    elif isinstance(node, tuple) and len(node) == 4:
        print('  ' * indent + f'{node[0]}: {node[2]} {node[3]} {node[1]}')
    elif isinstance(node, tuple) and len(node) == 2:
        print('  ' * indent + f'{node[0]}: {node[1]}')
    elif isinstance(node, tuple) and len(node) == 1:
        print('  ' * indent + f'{node[0]}')
    else:
        print('  ' * indent + str(node))

def display_tree(input_data):
    for item in input_data:
        print_tree(item)