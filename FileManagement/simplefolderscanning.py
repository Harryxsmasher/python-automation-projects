import os, shutil
# Get Files name and store it in a dictionary
file_type = {}

path_input = input("Enter the path: ")

with os.scandir(path_input) as entries:
    for entry in entries:
        if entry.is_file():
            filename = entry.name
            ext = entry.name.split(".")[-1]

            if ext not in file_type:
                file_type[ext] = []
            file_type[ext].append(filename)

# print(file_type)
# Create a new directory for each formats
file_name = file_type

for K_file, V_names in file_name.items():
    foldername = K_file
    files = V_names

    current_dir = os.getcwd()
    if file_name == current_dir:
        print("True")

    else:
        os.mkdir(foldername)
        print("Directory created!")


