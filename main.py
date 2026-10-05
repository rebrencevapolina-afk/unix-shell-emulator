import os
import sys
import argparse
import xml.etree.ElementTree as ET
import zipfile


def load_vfs(vfs_path):
    if not vfs_path:
        print("VFS не указана. Работаем без виртуальной файловой системы.")
        return None

    if not os.path.isfile(vfs_path):
        print(f"Ошибка загрузки VFS: файл '{vfs_path}' не найден.")
        return None

    if not zipfile.is_zipfile(vfs_path):
        print(f"Ошибка загрузки VFS: файл '{vfs_path}' не является ZIP-архивом.")
        return None

    vfs = {}
    try:
        with zipfile.ZipFile(vfs_path, 'r') as zf:
            for name in zf.namelist():
                if name.endswith('/'):
                    continue
                content = zf.read(name).decode('utf-8')
                parts = name.split('/')
                current = vfs
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = content
    except Exception as e:
        print(f"Ошибка загрузки VFS: {e}")
        return None

    print(f"VFS успешно загружена из '{vfs_path}'.")
    return vfs



def parse_and_expand(command_line):
    parts = command_line.split()
    if not parts:
        return None, []
    expanded_parts = [os.path.expandvars(part) for part in parts]
    return expanded_parts[0], expanded_parts[1:]


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

    print(f"Выполнение стартового скрипта: {script_path}")
    for line in lines:
        line = line.strip()
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
            print(result)
        except Exception as e:
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
    if vfs_elem is not None and vfs_elem.text:
        config['vfs_path'] = vfs_elem.text
    script_elem = root.find('script_path')
    if script_elem is not None and script_elem.text:
        config['script_path'] = script_elem.text
    return config


def repl(vfs):
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
            print(result)
        except EOFError:
            print("\nВыход из эмулятора.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")



def main():
    parser = argparse.ArgumentParser(description="Эмулятор командной оболочки")
    parser.add_argument('--vfs', type=str, help='Путь к физическому расположению VFS')
    parser.add_argument('--script', type=str, help='Путь к стартовому скрипту')
    parser.add_argument('--config', type=str, default='config.xml', help='Путь к конфигурационному файлу')
    args = parser.parse_args()

    print("Параметры запуска")
    print(f"VFS путь (из командной строки): {args.vfs}")
    print(f"Стартовый скрипт (из командной строки): {args.script}")
    print(f"Конфигурационный файл: {args.config}")

    config = parse_config(args.config)

    vfs_path = args.vfs if args.vfs else config.get('vfs_path')
    script_path = args.script if args.script else config.get('script_path')

    print("=== Итоговые параметры ===")
    print(f"VFS путь: {vfs_path}")
    print(f"Стартовый скрипт: {script_path}")

    vfs = load_vfs(vfs_path)

    if script_path:
        run_script(script_path)

    # Запускаем REPL
    repl(vfs)


if __name__ == "__main__":
    main()