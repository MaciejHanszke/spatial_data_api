import os
import sys
PROJECT_PATH = os.getcwd()
PROJECT_PATH = "\\".join(PROJECT_PATH.split("\\")[:-1])
SOURCE_PATH = os.path.join(
    PROJECT_PATH,"code"
)
sys.path.append(SOURCE_PATH)