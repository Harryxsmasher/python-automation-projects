import os

folder_path = input("Enter the folder path: ")
file_name = input("Enter the file name: ")
newFile_name = input("Enter the new filename: ")
old_path = os.path.join(folder_path, file_name)
new_path = os.path.join(folder_path, newFile_name)

os.rename(old_path, new_path)

print(new_path)