import os, shutil

file_type = {}
file_path = input("Enter the path: ")

with os.scandir(file_path) as entries:
    for entry in entries:
        if entry.is_file():
            filename = entry.name
            ext = entry.name.split(".")[-1]

            if ext not in file_type:
                file_type[ext] = []
            file_type[ext].append(filename)


print(file_type)

file_name = file_type

for K_file, V_names in file_name.items():
    foldername = K_file
    files = V_names


    new_directory = os.path.join(file_path, foldername)
    if file_name == new_directory:
        print("Folder already exists")
    else:
        os.makedirs(new_directory)