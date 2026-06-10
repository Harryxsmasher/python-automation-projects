from pathlib import Path

folder = Path(input("Enter the path: "))
folder_count = 0
file_count = 0
if folder.exists():
    for file in folder.iterdir():
        if file.is_file():
            file_count += 1
        elif file.is_dir():
            folder_count += 1
    print(f"Files count: {file_count} - Folder count: {folder_count}")
else:
    print("Path doesnt exist!")
