import os


# Подстановка переменных
def expand(s):
    for k in os.environ:
        s = s.replace("$" + k, os.environ[k])
    return s


# Основной цикл
while True:
    raw = expand(input("vfs> "))
    parts = raw.split()
    if not parts:
        continue
    cmd, args = parts[0], parts[1:]
    # Обработка команд
    if cmd == "exit":
        break
    elif cmd == "ls":
        print(f"ls {args}")
    elif cmd == "cd":
        print(f"cd {args}")
    else:
        print(f"Ошибка: неизвестная команда '{cmd}'")
