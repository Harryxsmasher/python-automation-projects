from pathlib import Path
folder = Path(input("Enter a path: "))
file = "basics.py"

fullpath = folder / file

if fullpath.exists():
    print("file exists")

if fullpath.is_file():
    print("Its a file")
elif fullpath.is_dir():
    print("Its a Directory")