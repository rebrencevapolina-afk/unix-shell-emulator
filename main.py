import os
import sys
import argparse
import xml.etree.ElementTree as ET


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
        return None
    elif command == "ls" or command == "cd":
        return f"{command} {' '.join(args)}"
    else:
        return f"{command}: command not found"


def run_script(script_path):
    if not os.path.isfile(script_path):
        print(f"Ошибка: стартовый скрипт '{script_path}' не найден.")
        return

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Ошибка чтения стартового скрипта: {e}")
        return

    print(f"Стартовый скрипт: {script_path}")
    for line in lines:
        line = line.strip()
        # Пропуск пустых строк и комментариев
        if not line or line.startswith('#'):
            continue

        print(f"VFS> {line}")

        command, args = parse_and_expand(line)
        if command is None:
            continue

        try:
            result = act(command, args)
            if result is None:
                print("Выход из эмулятора.")
                return
            else:
                print(result)
        except Exception as e:
            # Обработка ошибок выполнения команды
            print(f"Ошибка выполнения команды '{command}': {e}")
    print("Стартовый скрипт завершён")


def parse_config(config_path):
    if not os.path.isfile(config_path):
        print(f"Ошибка: конфигурационный файл '{config_path}' не найден.")
        return {}

    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Ошибка чтения конфигурационного файла: некорректный XML ({e})")
        return {}
    except Exception as e:
        print(f"Ошибка чтения конфигурационного файла: {e}")
        return {}

    config = {}
    vfs_elem = root.find('vfs_path')
    if vfs_elem is not None:
        config['vfs_path'] = vfs_elem.text

    script_elem = root.find('script_path')
    if script_elem is not None:
        config['script_path'] = script_elem.text

    return config


def repl(vfs_path=None):
    prompt = "VFS> "
    while True:
        try:
            user_input = input(prompt)
            command, args = parse_and_expand(user_input)

            if command is None:
                continue

            result = act(command, args)

            if result is None:
                print("Выход из эмулятора.")
                break
            else:
                print(result)

        except EOFError:
            print("\nВыход из эмулятора.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")


def main():
    parser = argparse.ArgumentParser(description="Эмулятор командной оболочки UNIX-подобной ОС")
    parser.add_argument('--vfs', type=str, help='Путь к физическому расположению VFS')
    parser.add_argument('--script', type=str, help='Путь к стартовому скрипту')
    parser.add_argument('--config', type=str, default='config.xml', help='Путь к конфигурационному файлу')
    args = parser.parse_args()

    print(f"VFS путь (из командной строки): {args.vfs}")
    print(f"Стартовый скрипт (из командной строки): {args.script}")
    print(f"Конфигурационный файл: {args.config}")

    config = parse_config(args.config)

    vfs_path = args.vfs if args.vfs else config.get('vfs_path')
    script_path = args.script if args.script else config.get('script_path')

    print(f"VFS путь: {vfs_path}")
    print(f"Стартовый скрипт: {script_path}")
    if script_path:
        run_script(script_path)

    # Запускаем REPL
    repl(vfs_path)


if __name__ == "__main__":
    main()