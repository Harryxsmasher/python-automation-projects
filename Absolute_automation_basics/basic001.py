import os, shutil
usr_path = input("Enter the path: ")
if os.path.exists(usr_path):
    print(True)
    files = os.listdir(usr_path)
    for file in files:
        full_path = os.path.join(usr_path, file)
        if os.path.isfile(full_path):
            file_name = file.split(".")[0]
            extension = file.split(".")[-1]
            print(f"{file_name} {extension}")
            new_path = os.path.join(usr_path, extension)
            source_path = full_path
            dest_path = os.path.join(new_path, file)
            if os.path.exists(new_path):
                shutil.move(source_path, dest_path)
                print("Files are moved!")
            else:
                os.mkdir(new_path)
                shutil.move(source_path, dest_path)
                print("Folders created and Files are moved!")