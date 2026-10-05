import os

def parse_and_expand(command_line):
    parts = command_line.split()
    if not parts:
        return None, []

    expanded_parts = [os.path.expandvars(part) for part in parts]
    
    command = expanded_parts[0]
    args = expanded_parts[1:]
    return command, args

def act(command, args):
    if command == "exit":
        return "exit"
    elif command == "ls" or command == "cd":
        return f"{command} {' '.join(args)}"
    else:
        return f"{command}: command not found"

def repl():
    prompt = "VFS> "
    while True:
        try:
            user_input = input(prompt)
            command, args = parse_and_expand(user_input)
            
            if command is None:
                continue

            result = act(command, args)
            
            if result == "exit":
                print("Выход из эмулятора.")
                break
            else:
                print(result)

        except EOFError:
            print("\nВыход из эмулятора.")
            break

if __name__ == "__main__":
    repl()