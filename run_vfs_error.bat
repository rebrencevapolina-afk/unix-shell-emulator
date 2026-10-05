@echo off
echo Тест: ошибка загрузки VFS (файл не найден)
python main.py --vfs ./missing.zip
pause