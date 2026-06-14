from pathlib import Path

folder = Path(input("Enter the path: "))
if folder.exists():
    for file in folder.glob("*.pptx"):
        print(file.name)
else:
    print("Folder not exists")

