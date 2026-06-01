import os

usr_path = input("Enter the path: ")

files = os.listdir(usr_path)

count = 1

for file in files:
    full_path = os.path.join(usr_path, file)
    if os.path.isfile(full_path):
        file_name = file.split(".")[0]
        extension = file.split(".")[-1]

        new_file_name = "Vacation_" + str(count) + "." + extension
        
        old_path = full_path
        new_path = os.path.join(usr_path, new_file_name)

        os.rename(old_path, new_path)
        count = count + 1
print(new_path)