import os
import time
from pathlib import Path
# Первая нормальная программа, ура!

conversion_type = int(input("What type of conversion?\n0 - New to old ( 1.13+ ---> 1.12 or older ) \n1 - Old to new ( 1.12 or older ---> 1.13+ ) \n"))

if conversion_type == 0:
    config_folder = "new to old"
elif conversion_type == 1:
    config_folder = "old to new"
else:
    print("Incorrect choice of conversion type.")
    exit()

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, "texture converter")
config_folder_path = os.path.join(script_dir, config_folder)
file_path = os.path.join(config_folder_path, 'names.txt')
suf_file_path = os.path.join(config_folder_path, 'suf.txt')
folder_file_path = os.path.join(config_folder_path, 'folder.txt')
dir_file_path = os.path.join(config_folder_path, 'dir.txt')


names_dict = {}
with open(file_path, 'r') as f:
    for line_number, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        if " = " not in line:
            print(f"Warning: Missing ' = ' in {file_path} on line {line_number}. Skipping this line.")
            continue
        name, replacement = line.split(' = ')
        names_dict[name] = replacement

folders_dict = {}
with open(folder_file_path, 'r') as f:
    for line in f:
        name, replacement = line.strip().split(' = ')
        folders_dict[name] = replacement


suffixes = []
with open(suf_file_path, 'r') as sf:
    for line in sf:
        suffixes.append(line.strip())


target_dirs = []
with open(dir_file_path, 'r') as df:
    for line in df:
        target_dirs.append(os.path.join(line.strip()))

def is_valid_file_name(file_basename, old_name, suffixes):
    if file_basename.startswith(old_name):
        suffix = file_basename[len(old_name):]
        for allowed_suffix in suffixes:
            if suffix == allowed_suffix:
                return True
    return False


def rename_folders(start_path, folders_dict):
    for root, dirs, _ in os.walk(start_path):
        for folder_name in dirs:
            for old_name, new_name in folders_dict.items():
                if folder_name == old_name:
                    old_folder_path = os.path.join(root, folder_name)
                    new_folder_path = os.path.join(root, new_name)
                    os.rename(old_folder_path, new_folder_path)
rename_folders(folder_path, folders_dict)                    

def get_updated_target_dirs(root_path, target_dirs):
    updated_target_dirs = []
    for path in target_dirs:
        old_path = os.path.join(root_path, path)
        if os.path.exists(old_path):
            updated_target_dirs.append(os.path.abspath(old_path))
        else:
            for old_name, new_name in folders_dict.items():
                updated_path = old_path.replace(old_name, new_name)
                if os.path.exists(updated_path):
                    updated_target_dirs.append(os.path.abspath(updated_path))
    return updated_target_dirs

def process_dirs(updated_target_dirs):
    for target_dir_path in updated_target_dirs:
        for root, dirs, files in os.walk(target_dir_path):
            for file_name in files:
                file_basename, file_ext = os.path.splitext(file_name)

                for old_name, new_name in names_dict.items():
                    if is_valid_file_name(file_basename, old_name, suffixes):
                        new_file_name = file_basename.replace(old_name, new_name) + file_ext
                        old_file_path = os.path.join(root, file_name)
                        new_file_path = os.path.join(root, new_file_name)

                        if os.path.exists(new_file_path):
                            print(f"Warning: {new_file_path} already exists. Skipping file {old_file_path}.")
                        else:
                            os.rename(old_file_path, new_file_path)


folder_renamed = True
while folder_renamed:
    folder_renamed = False
    for folder_name in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, folder_name)
        if os.path.isdir(subfolder_path):
            found_correct_folder_name = False
            for correct_folder_name in folders_dict.values():
                if folder_name == correct_folder_name:
                    found_correct_folder_name = True
                    break

            if found_correct_folder_name:
                target_dirs.append(folder_name)
            else:
                for old_name, new_name in folders_dict.items():
                    if folder_name == old_name:
                        new_folder_name = folder_name.replace(old_name, new_name)
                        old_folder_path = os.path.join(folder_path, folder_name)
                        new_folder_path = os.path.join(folder_path, new_folder_name)
                        os.rename(old_folder_path, new_folder_path)
                        folder_renamed = True
                        break

    if folder_renamed:
        target_dirs = [folder_replacement for _, folder_replacement in folders_dict.items()]

updated_target_dirs = get_updated_target_dirs(folder_path, target_dirs)
process_dirs(updated_target_dirs)
