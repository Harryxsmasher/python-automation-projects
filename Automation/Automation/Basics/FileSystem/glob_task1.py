from pathlib import Path

folder = Path(input("Enter the path: "))
extension = input("Enter the extension you want to find (type with a dot): ")

extension_variable = "*" + extension

if folder.exists():
    for file in folder.glob(extension_variable):
        print(file.name)
else:
    print("Folder not found")
