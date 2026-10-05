import zipfile
import os

def create_minimal_vfs(path):
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('readme.txt', 'Welcome to the minimal VFS!')
    print(f'Создан: {path}')

def create_multi_file_vfs(path):
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('readme.txt', 'This is readme.')
        zf.writestr('notes.txt', 'Some notes here.')
        zf.writestr('data.txt', 'Data file content.')
        zf.writestr('config.ini', '[section]\nkey=value')
    print(f'Создан: {path}')

def create_nested_vfs(path):
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('readme.txt', 'Root readme.')
        zf.writestr('docs/guide.md', '# Guide\nSome documentation.')
        zf.writestr('docs/api/reference.md', '# API Reference')
        zf.writestr('src/main.py', 'print("hello")')
        zf.writestr('src/utils/helper.py', 'def helper(): pass')
        zf.writestr('src/utils/data/values.txt', '1\n2\n3')
    print(f'Создан: {path}')


if __name__ == '__main__':
    create_minimal_vfs('vfs_minimal.zip')
    create_multi_file_vfs('vfs_multi.zip')
    create_nested_vfs('vfs_nested.zip')