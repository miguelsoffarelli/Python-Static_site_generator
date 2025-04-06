from textnode import *
from htmlnode import *
from blockfunctions import markdown_to_html_node, extract_title
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

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    try:
        with open(from_path, "r") as md_file:
            md_content = md_file.read()

        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        html_content = markdown_to_html_node(md_content).to_html()
        title = extract_title(md_content)
        result = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        with open(dest_path, "w") as output_file:
            output_file.write(result)

        print((f"Page generated successfully from {from_path} to {dest_path} using {template_path}."))

    except FileNotFoundError as e:
        print(f"Error: One of the files was not found—{e.filename}. Please check the file paths.")
        raise
    except PermissionError as e:
        print(f"Error: Permission denied when accessing '{e.filename}'.")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    content_dir = os.listdir(dir_path_content)

    for item in content_dir:
        item_content_path = os.path.join(dir_path_content, item)
        
        if os.path.isfile(item_content_path) and item.endswith(".md"):
            item_dest = item.replace(".md", ".html")
            item_dest_path = os.path.join(dest_dir_path, item_dest)
            
            os.makedirs(os.path.dirname(item_dest_path), exist_ok=True)
            
            generate_page(item_content_path, template_path, item_dest_path)
        elif os.path.isdir(item_content_path):
            new_dest_dir = os.path.join(dest_dir_path, item)
            os.makedirs(new_dest_dir, exist_ok=True)
            
            generate_pages_recursive(item_content_path, template_path, new_dest_dir)




def main():
    static_dir = "static"
    public_dir = "public"
    copy_static(static_dir, public_dir)
    print("Static files copied successfully!")
    generate_pages_recursive("content", "template.html", "public")

main()