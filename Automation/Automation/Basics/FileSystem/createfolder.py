import os


usr_path = input("Enter the path: ")
new_folder = input("Enter the folder name: ")

new_path = os.path.join(usr_path, new_folder)
if os.path.exists(new_path):
    print("Path Exists!")
elif not os.path.exists(new_path):
    os.mkdir(new_path)
    print("Created!")
    print(new_path)

