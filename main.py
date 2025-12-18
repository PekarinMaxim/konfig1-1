import argparse
import base64
import csv
import os
import sys
from io import StringIO

class VFSNode:
    def __init__(self, name, node_type, content=None):
        self.name = name
        self.type = node_type  # "dir" or "file"
        self.content = content
        self.children = {}

class VFS:
    def __init__(self):
        self.init_default()

    def init_default(self):
        self.root = VFSNode("/", "dir")
        self.cwd = self.root

    def load_from_csv(self, csv_path: str):
        if not os.path.exists(csv_path):
            raise FileNotFoundError("CSV-файл VFS не найден")

        # читаем файл как текст
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            raw = f.read()

        # определяем разделитель
        delimiter = ";" if ";" in raw.splitlines()[0] else ","

        reader = csv.DictReader(StringIO(raw), delimiter=delimiter)
        if reader.fieldnames != ["path", "type", "content"]:
            raise ValueError("Неверный формат CSV (ожидается: path,type,content)")

        self.init_default()

        for row in reader:
            path = row["path"]
            node_type = row["type"]
            content = row["content"]

            if node_type not in ("dir", "file"):
                raise ValueError(f"Неизвестный тип: {node_type}")

            self._add_node(path, node_type, content)

    def _add_node(self, path, node_type, content):
        parts = [p for p in path.split("/") if p]
        current = self.root

        for i, part in enumerate(parts):
            if part not in current.children:
                if i == len(parts) - 1:
                    if node_type == "file":
                        data = base64.b64decode(content).decode("utf-8") if content else ""
                        current.children[part] = VFSNode(part, "file", data)
                    else:
                        current.children[part] = VFSNode(part, "dir")
                else:
                    current.children[part] = VFSNode(part, "dir")
            current = current.children[part]

    def ls(self):
        for name in sorted(self.cwd.children):
            print(name)

    def cd(self, path):
        if path == "/":
            self.cwd = self.root
            return

        if path == "..":
            return  # упрощённо

        if path not in self.cwd.children:
            print("Ошибка: путь не существует")
            return

        node = self.cwd.children[path]
        if node.type != "dir":
            print("Ошибка: это не каталог")
            return

        self.cwd = node


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vfs-csv", required=True, help="CSV-файл VFS")
    args = parser.parse_args()

    vfs = VFS()

    try:
        vfs.load_from_csv(args.vfs_csv)
    except Exception as e:
        print(f"ОШИБКА: Ошибка загрузки VFS: {e}")
        sys.exit(1)

    while True:
        try:
            cmd = input("VFS:/> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        if cmd == "exit":
            break

        if cmd == "ls":
            vfs.ls()
        elif cmd.startswith("cd "):
            vfs.cd(cmd.split(maxsplit=1)[1])
        elif cmd == "vfs-init":
            vfs.init_default()
            print("VFS сброшена к состоянию по умолчанию")
        else:
            print("Ошибка: неизвестная команда")

if __name__ == "__main__":
    main()
#cd C:\Users\Home\PycharmProjects\PythonProject31 python konfig-1-3.py --vfs-csv vfs_test.csv
#ls
#cd docs
#ls
#cd /
#cd bin
#ls
#vfs-init
#ls
#exit
