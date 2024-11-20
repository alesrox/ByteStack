from syntax_tree import ASTNode

def pretty_print(data, indent=0):
    spaces = ' ' * indent
    if isinstance(data, dict):
        if data == '{}':
            print('{}')
        else:
            print("{")
            for key, value in data.items():
                print(f"{spaces}    {key}: ", end="")
                if isinstance(value, ASTNode):
                    pretty_print(value.to_dict(), indent + 4)
                else:
                    pretty_print(value, indent + 4)
            print(f"{spaces}}}")
    elif isinstance(data, list):
        if data != []:
            print("[")
            for item in data:
                print(f"{spaces}    ", end="")
                if isinstance(item, ASTNode):
                    pretty_print(item.to_dict(), indent + 4)
                else:
                    pretty_print(item, indent + 4)
            print(f"{spaces}]")
        else:
            print("[]")
    else:
        print(data)

def get_key(obj_dict: dict, element):
    for key, value in obj_dict.items():
        if value == element:
            return key
    
    return None

def string_to_list(string: str) -> list:
    list_from_string = []
    string = string.replace('\\n', '\n')
    string = string.replace('\\t', '\t')

    string += '\0' * (-len(string) % 4)

    for i in range(0, len(string), 4):
        block = string[i:i + 4]
        packed = 0
        for j, char in enumerate(block):
            packed |= ord(char) << (24 - j * 8)
        list_from_string.append(packed)

    return list_from_string