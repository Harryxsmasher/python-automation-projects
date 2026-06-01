import os

usr_path = input("Enter the path: ")

if os.path.exists(usr_path):
    print(True)
    files = os.listdir(usr_path)
    for file in files:
        full_path = os.path.join(usr_path, file)
        if os.path.isdir(full_path):
            print(file)

else:
    print(False)