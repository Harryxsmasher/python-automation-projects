import os
filesList = []
foldersList = []



file_path = input("Enter the path: ")

if os.path.exists(file_path):
    print("Path Exists")
    files = os.listdir(file_path)

    for file in files:
        paths = os.path.join(file_path, file)
        new_variable = "New_" + file
        new_path = os.path.join(file_path, new_variable)
        if os.path.isfile(paths):
            filesList.append(file)
            os.rename(paths, new_path)    
        elif os.path.isdir(paths):
            foldersList.append(file)

else:
    print("Path does not exists")

if filesList:
    print("Files: ")
    for file in filesList:
        print(file)
else:
    print("No files exists")
if foldersList:
    print("Folders: ")
    for folder in foldersList:
        print(folder)
else:
    print("No Folder exists")


