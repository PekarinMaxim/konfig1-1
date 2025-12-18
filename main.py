import os
import sys
import argparse
import re

def expand(s: str) -> str:
    """
    Подстановка переменных окружения: поддерживает $VAR и ${VAR}.
    """
    if not s:
        return s
    # ${VAR}
    s = re.sub(r'\$\{([^}]+)\}', lambda m: os.environ.get(m.group(1), ''), s)
    # $VAR (word chars, stop at non-word)
    s = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', lambda m: os.environ.get(m.group(1), ''), s)
    return s

def execute_vfs_command(cmd: str, args: list, vfs_root: str):
    """
    Выполнение команды эмулятора (заглушки для этапа 1).
    Возвращаем:
      True  -> команда exit (завершить работу)
      False -> успешно выполнено, продолжать
      None  -> ошибка выполнения (сообщена пользователю)
    """
    if cmd == "exit":
        print("Выход из эмулятора.")
        return True

    elif cmd == "ls":
        # Заглушка: печатаем имя команды и аргументы (строго по ТЗ этап 1)
        print(f"ls вызвана с аргументами: {args}")
        return False

    elif cmd == "cd":
        # Проверяем аргументы — если нет, то ошибка
        if not args:
            print("Ошибка: укажите путь для cd")
            return None
        print(f"cd вызвана с аргументами: {args} (эмуляция — реальная смена директории не производится)")
        return False

    else:
        print(f"Ошибка: неизвестная команда '{cmd}'")
        return None

def execute_script(script_path: str, vfs_root: str) -> bool:
    """
    Выполнить стартовый скрипт: при первой ошибке остановить выполнение (возврат False).
    Во время выполнения на экран выводится и команда (эмуляция ввода), и вывод команды.
    """
    print(f"\n=== Выполнение стартового скрипта: {script_path} ===\n")
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ОШИБКА: Скрипт не найден: {script_path}")
        return False
    except Exception as e:
        print(f"ОШИБКА при открытии скрипта: {e}")
        return False

    for line_num, raw_line in enumerate(lines, 1):
        # Убираем комментарии (после #) и пробелы
        line = raw_line.split('#', 1)[0].strip()
        if not line:
            continue
        # Эмулируем ввод пользователя (печатаем строку как ввод)
        print(f"{os.path.basename(vfs_root) if vfs_root else 'vfs'}> {line}")
        # Подстановка переменных окружения
        expanded_line = expand(line)
        parts = expanded_line.split()
        if not parts:
            continue
        cmd, args = parts[0], parts[1:]
        result = execute_vfs_command(cmd, args, vfs_root)
        # Если ошибка выполнения -> остановка и возврат False
        if result is None:
            print(f"\n!!! ОШИБКА В СКРИПТЕ (строка {line_num}): '{line}'")
            print("Выполнение скрипта остановлено.")
            return False
        if result:  # exit
            print("Завершение работы по команде exit из скрипта.")
            return True

    print(f"\n=== Скрипт {script_path} успешно выполнен ===")
    return True

def main():
    parser = argparse.ArgumentParser(description='Эмулятор виртуальной файловой системы (VFS) — минимальный прототип')
    parser.add_argument('-vfs', '--vfs-root', help='Путь к физическому расположению VFS', required=True)
    parser.add_argument('-s', '--script', help='Путь к стартовому скрипту для выполнения команд эмулятора')
    args = parser.parse_args()

    # Отладочный вывод всех заданных параметров (этап 2)
    print("=" * 60)
    print("ПАРАМЕТРЫ ЗАПУСКА ЭМУЛЯТОРА:")
    print(f"  Путь к VFS: {args.vfs_root}")
    print(f"  Стартовый скрипт: {args.script if args.script else 'не указан'}")
    print("=" * 60)

    # Проверяем существование VFS корня (этап 2)
    if not os.path.exists(args.vfs_root):
        print(f"\nОШИБКА: Указанный путь к VFS не существует: {args.vfs_root}")
        sys.exit(1)

    vfs_root = os.path.abspath(args.vfs_root)
    vfs_name = os.path.basename(vfs_root) or "vfs"

    # Если указан стартовый скрипт — выполняем и выходим (останавливается при ошибке)
    if args.script:
        ok = execute_script(args.script, vfs_root)
        if not ok:
            sys.exit(1)
        return

    # Режим интерактивного ввода команд (REPL)
    print("\nРежим интерактивного ввода команд.")
    print("Для выхода введите 'exit'")
    try:
        while True:
            try:
                raw = input(f"{vfs_name}> ")
            except EOFError:
                print("\n\nЗавершение работы (EOF).")
                break
            except KeyboardInterrupt:
                print("\n\nЗавершение работы (KeyboardInterrupt).")
                break

            if raw is None:
                continue
            raw_expanded = expand(raw).strip()
            if not raw_expanded:
                continue
            parts = raw_expanded.split()
            cmd, cmd_args = parts[0], parts[1:]
            result = execute_vfs_command(cmd, cmd_args, vfs_root)
            if result is None:
                # Сообщение об ошибке уже было выведено внутри execute_vfs_command
                # В интерактивном режиме просто продолжаем
                continue
            if result:
                # exit
                break

    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



#python konfig-1-2.py -vfs C:\Users\Home\PycharmProjects\PythonProject30
#ls
#cd test
#ls arg1 arg2
#exit


