# Generates static website
import os

def get_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            files.append(os.path.join(dirpath,f))
    return files


def generate():
    root = os.getcwd()
    files = get_files(root) 

if __name__ = "__main__":
    generate(site_path)
