# Эмулятор командной оболочки UNIX-подобной ОС

## Общее описание

Эмулятор командной оболочки (shell) UNIX-подобной ОС на языке Python. Работает в режиме REPL и поддерживает базовые команды. **Вариант №27.**

## Функциональность

**Этап 1:**
- Консольный интерфейс (CLI) с приглашением `VFS>`.
- Парсер командной строки с раскрытием переменных окружения (`$HOME`).
- Команды-заглушки: `ls`, `cd`.
- Команда `exit`.
- Обработка ошибок неизвестных команд.

**Этап 2:**
- Параметры командной строки: `--vfs`, `--script`, `--config`.
- Чтение конфигурационного файла в формате XML.
- Приоритет параметров командной строки над конфигурационным файлом.
- Стартовый скрипт с командами (комментарии и ошибочные строки пропускаются).
- Отладочный вывод всех параметров при запуске.

**Этап 3:**
- Загрузка VFS из ZIP-архива в память.
- Построение вложенной структуры папок и файлов (словарь Python).
- Поддержка бинарных данных через base64.
- Обработка ошибок: файл не найден, неверный формат ZIP.
- Тестовые архивы: минимальный, с несколькими файлами, с 3 уровнями вложенности.
- BAT-скрипты для запуска всех вариантов VFS.

## Требования

- Python 3.10+
- Windows / macOS / Linux

## Команды для запуска

Запуск с конфигурационным файлом по умолчанию:

    python main.py

Запуск с параметрами командной строки:

    python main.py --vfs ./my_vfs --script ./start.txt --config ./config.xml

Запуск через BAT-скрипты (Windows):

    run_with_config.bat
    run_with_args.bat

## Формат конфигурационного файла config.xml

    <?xml version="1.0" encoding="UTF-8"?>
    <config>
        <vfs_path>./vfs_data</vfs_path>
        <script_path>./start.txt</script_path>
    </config>

## Формат стартового скрипта start.txt

    # Комментарий игнорируется
    ls
    cd /home/user
    ls -l $HOME
    unknown_command
    exit

## Примеры использования

Пример 1. Работа команды `ls`:

    VFS> ls
    ls

Пример 2. Раскрытие переменной окружения:

    VFS> ls $HOME
    ls C:\Users\user

Пример 3. Обработка неизвестной команды:

    VFS> foo bar
    foo: command not found

Пример 4. Приоритет параметров командной строки над XML:

    > python main.py --vfs ./my_vfs
    VFS путь: ./my_vfs

## Структура проекта


    unix-shell-emulator/
    ├── main.py
    ├── make_vfs.py
    ├── config.xml
    ├── bad_config.xml
    ├── start.txt
    ├── vfs_minimal.zip
    ├── vfs_multi.zip
    ├── vfs_nested.zip
    ├── run_with_config.bat
    ├── run_with_args.bat
    ├── run_vfs_minimal.bat
    ├── run_vfs_multi.bat
    ├── run_vfs_nested.bat
    ├── run_vfs_error.bat
    └── readme.md   