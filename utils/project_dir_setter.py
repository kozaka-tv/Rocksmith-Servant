import os
import sys


def set_project_directory():
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
