import os

file_count = {}

usr_path = input("Enter the folder path: ")

if os.path.exists(usr_path):

    files = os.listdir(usr_path)

    for file in files:

        full_path = os.path.join(usr_path, file)

        if os.path.isfile(full_path):

            if file in file_count:
                file_count[file] = file_count[file] + 1

            else:
                file_count[file] = 1

    print("\nFile Occurrences:")
    for file, count in file_count.items():
        print(f"{file} : {count}")

else:
    print("Path does not exist")


