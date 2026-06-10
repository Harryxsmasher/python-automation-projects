from pathlib import Path

user_path = Path(input("Enter the path: "))
if user_path.exists():
    for file in user_path.iterdir():
        fullpath = user_path / file
        if fullpath.is_file():
            print(f"Filename with extension: {file.name} - Filename: {file.stem} - Extension: {file.suffix[1:]} - Parent folder: {file.parent}")
else:
    print("Path is not found!")