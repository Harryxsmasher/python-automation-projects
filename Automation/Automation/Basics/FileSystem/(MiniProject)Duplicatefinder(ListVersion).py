import os

seen_files = []

usr_path = input("Enter the path: ")
files = os.listdir(usr_path)

for file in files:
    full_path = os.path.join(usr_path, file)
    if os.path.isfile(full_path):
        if file in seen_files:
            print(f"Duplicate file found: {file}")
        elif file not in seen_files:
            seen_files.append(file)

for efile in seen_files:
    print(efile)       