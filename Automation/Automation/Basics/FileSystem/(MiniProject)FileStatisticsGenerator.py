from pathlib import Path
import json


files_stat = {}
folder = Path(input("Enter the path: "))

if folder.exists():
    for file in folder.rglob("*.*"):
        extension = file.suffix
        if extension in files_stat:
            files_stat[extension] += 1
        else:
            files_stat[extension] = 1
else:
    print("Folder not found!")

for extension, count in files_stat.items():
    print(extension, count)

json_file = folder / "file_stats.json"

with open(json_file, "w") as f:
    json.dump(files_stat, f, indent = 4)
print("Data saved into JSON file")