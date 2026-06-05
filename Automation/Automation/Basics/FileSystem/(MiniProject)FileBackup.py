import os, shutil


usr_path = input("Enter the path: ")
backup_folder_name = "Backup"

if os.path.exists(usr_path):
    backup_folder_path = os.path.join(usr_path, backup_folder_name)
    if not os.path.exists(backup_folder_path):
        os.mkdir(backup_folder_path)
        print("Backup Folder created!")
    if os.path.exists(backup_folder_path):
        files = os.listdir(usr_path)
        for file in files:
            full_path = os.path.join(usr_path, file)
            if os.path.isfile(full_path):
                source_path = full_path
                destination_path = backup_folder_path

                shutil.copy(source_path, destination_path)
        print("Files copied to backup folder!")
    