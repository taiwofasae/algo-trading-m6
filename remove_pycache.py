import os
import shutil

def remove_pycache(path):
    for root, dirs, files in os.walk(path):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
            
remove_pycache('.')