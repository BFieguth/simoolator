import termcolor
import random

def get_unique_color(index):
    COLORS = ['red', 'green', 'yellow', 'magenta', 'cyan', 'white', 'blue']
    return COLORS[index % len(COLORS)]


def print_nested_dict_tree(data, indent=0, prefix="", input_mapping=None, current_path=""):
    """
    Recursively print a nested dictionary with a tree-like structure and optional color coding.

    Args:
        data (dict): The dictionary to print.
        indent (int): The current indentation level.
        prefix (str): The current prefix for tree branches.
        input_mapping (tuple or dict): Optional. A tuple where the first value is a model name and the second value is an input mapping dictionary, or just a dictionary of input mappings.
        current_path (str): The current path being traversed.
    """
    color_map = {}
    
    # If input_mapping is a tuple, extract model name and mapping dictionary
    if isinstance(input_mapping, tuple):
        model_name, mapping_dict = input_mapping
        print(f"Input Mapping for {model_name}")
        input_mapping = mapping_dict
    elif input_mapping is None:
        input_mapping = {}

    # Assign colors to each argument in input_mapping
    for index, (arg, path) in enumerate(input_mapping.items()):
        color = get_unique_color(index)
        color_map[path] = color

    def print_tree(data, indent, prefix, current_path):
        for i, (key, value) in enumerate(data.items()):
            branch = "├── " if i < len(data) - 1 else "└── "
            new_prefix = "│   " if i < len(data) - 1 else "    "
            full_path = f"{current_path}.{key}" if current_path else key

            if full_path in color_map:
                display_key = termcolor.colored(key, color_map[full_path])
            else:
                display_key = key

            if isinstance(value, dict):
                print(f"{prefix}{branch}{display_key}:")
                print_tree(value, indent + 4, prefix + new_prefix, full_path)
            else:
                if full_path in color_map:
                    display_key = termcolor.colored(key, color_map[full_path])
                else:
                    display_key = key
                print(f"{prefix}{branch}{display_key}: {type(value).__name__}")

    # Print the tree structure
    print_tree(data, indent, prefix, current_path)

    # Print the legend
    print("\nLegend:")
    for index, (arg, path) in enumerate(input_mapping.items()):
        color = get_unique_color(index)
        print(termcolor.colored(f"{arg} ({path})", color))


