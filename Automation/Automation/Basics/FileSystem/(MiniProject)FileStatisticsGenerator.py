from pathlib import Path
import json

history = []
files_stat = {}


user_choice = int(input("Enter how many times: "))

while user_choice <= 4:
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

    # for extension, count in files_stat.items():
        # print(extension, count)

    json_file = folder / "file_stats.json"

    with open(json_file, "w") as f:
        json.dump(files_stat, f, indent = 4)
    print("Data saved into JSON file")

    with open(json_file, 'r') as f:
        python_obj = json.load(f)
    print(type(python_obj))
    # print(python_obj)

    for extension, count in python_obj.items():
        print(extension, count)


    history.append(python_obj)
    user_choice = user_choice + 1
print(history)
