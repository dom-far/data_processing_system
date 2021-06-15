import os

filename = "requirements.txt"

if not os.system(f"pip3 install -r {filename}"):
    input("\nУстановка модулей успешно завершена!\n\nНажмите любую клавишу, чтобы выйти...")
else:
    input(f"\nПроизошла ошибка при установке модулей!\nПроверьте содержимое файла {filename}\n\nНажмите любую клавишу, чтобы выйти...")