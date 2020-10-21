import os
import shutil


def path_exists(path):
    return os.path.exists(path)


def create_directory(dir):
    return os.makedirs(dir)

def copy_file(src, dst):
    return shutil.copyfile(src, dst)

def rename(old_path, new_path):
    return os.rename(old_path,new_path)

def get_current_directory():
    return os.getcwd()


def deletefile(path):
    return os.remove(path)


def movefile(temp_path, full_path):
    return os.rename(temp_path,full_path)

def shell_command(command):
    return os.system(command)


def make_zip(output_file_path, target_directory):
    return shutil.make_archive(output_file_path, 'zip', target_directory)