from textnode import *
import os
import shutil


def copy_static(src, destination):
    if os.path.exists(destination):
        shutil.rmtree(destination)

    os.mkdir(destination)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dest_path = os.path.join(destination, item)

        if os.path.isfile(src_path):
            print(f"Copying file: {src_path} to {dest_path}")
            shutil.copy(src_path, dest_path)
        elif os.path.isdir(src_path):
            print(f"Creating directory: {dest_path}")
            copy_static(src_path, dest_path)


def main():
    static_dir = "static"
    public_dir = "public"
    copy_static(static_dir, public_dir)
    print("Static files copied successfully!")

main()