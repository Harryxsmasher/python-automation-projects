import os, shutil

folder_path = input("Enter the folder path: ")
filename = input("Enter the file name: ")
dest_folder = input("Enter the destination folder path: ")

source_path = os.path.join(folder_path, filename)
dest_path = os.path.join(dest_folder, filename)

shutil.move(source_path, dest_path)

print("Moved!")