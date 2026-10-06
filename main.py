import os
import sys
import argparse
import xml.etree.ElementTree as ET
import zipfile
import base64
import getpass


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
                raw = zf.read(name)
                try:
                    content = raw.decode('utf-8')
                except UnicodeDecodeError:
                    content = {'__binary__': base64.b64encode(raw).decode('ascii')}

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



class VFSState:
    def __init__(self, vfs):
        self.root = vfs if vfs is not None else {}
        self.path = []  

    def current(self):
        node = self.root
        for name in self.path:
            if isinstance(node, dict) and name in node:
                node = node[name]
            else:
                return {}
        return node

    def resolve(self, target):
        if not target:
            return list(self.path)

        if target.startswith('/'):
            parts = target.strip('/').split('/')
        else:
            parts = self.path + target.split('/')

        result = []
        for part in parts:
            if part == '' or part == '.':
                continue
            if part == '..':
                if result:
                    result.pop()
            else:
                result.append(part)
        return result

    def get_node(self, path_parts):
        node = self.root
        for name in path_parts:
            if isinstance(node, dict) and name in node:
                node = node[name]
            else:
                return None
        return node

    def cd(self, target):
        if not target:
            self.path = []
            return True

        new_path = self.resolve(target)
        node = self.get_node(new_path)
        if node is None:
            return False
        if not isinstance(node, dict):
            return False 
        self.path = new_path
        return True

    def pwd(self):
        """Возвращает текущий путь в виде строки."""
        if not self.path:
            return '/'
        return '/' + '/'.join(self.path) + '/'



def parse_and_expand(command_line):
    parts = command_line.split()
    if not parts:
        return None, []
    expanded_parts = [os.path.expandvars(part) for part in parts]
    return expanded_parts[0], expanded_parts[1:]


def cmd_ls(state, args):
    node = state.current()
    if not isinstance(node, dict):
        return "ls: не папка"
    if not node:
        return "(пусто)"
    return '  '.join(sorted(node.keys()))


def cmd_cd(state, args):
    if len(args) > 1:
        return "cd: слишком много аргументов"
    target = args[0] if args else None
    if state.cd(target):
        return None  
    return f"cd: '{target}': нет такой папки"


def cmd_cat(state, args):
    if not args:
        return "cat: не указан файл"
    results = []
    for arg in args:
        path_parts = state.resolve(arg)
        node = state.get_node(path_parts)
        if node is None:
            results.append(f"cat: '{arg}': файл не найден")
        elif isinstance(node, dict):
            if '__binary__' in node:
                results.append(f"cat: '{arg}': бинарный файл (base64, {len(node['__binary__'])} символов)")
            else:
                results.append(f"cat: '{arg}': это папка")
        else:
            results.append(node)
    return '\n'.join(results)


def cmd_whoami(state, args):
    if args:
        return "whoami: аргументы не поддерживаются"
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


def act(command, args, state):
    if command == "exit":
        return None
    elif command == "ls":
        return cmd_ls(state, args)
    elif command == "cd":
        return cmd_cd(state, args)
    elif command == "cat":
        return cmd_cat(state, args)
    elif command == "whoami":
        return cmd_whoami(state, args)
    else:
        return f"{command}: command not found"



def run_script(script_path, state):
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
            result = act(command, args, state)
            if result is None:
                if command == "exit":
                    print("Выход из эмулятора.")
                    return

                continue
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



def repl(state):
    while True:
        try:
            prompt = f"VFS:{state.pwd()}> "
            user_input = input(prompt)
            command, args = parse_and_expand(user_input)
            if command is None:
                continue
            result = act(command, args, state)
            if result is None:
                if command == "exit":
                    print("Выход из эмулятора.")
                    break
                continue  # cd без вывода
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

    print("    Итоговые параметры ")
    print(f"VFS путь: {vfs_path}")
    print(f"Стартовый скрипт: {script_path}")

    vfs = load_vfs(vfs_path)
    state = VFSState(vfs)

    if script_path:
        run_script(script_path, state)

    repl(state)


if __name__ == "__main__":
    main()