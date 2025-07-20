import os
from constants import DATA_DIRECTORY

def pulizia():
    if os.path.exists(DATA_DIRECTORY):
        for filename in os.listdir(DATA_DIRECTORY):
            file_path = os.path.join(DATA_DIRECTORY, filename)
            for subdir, _, files in os.walk(file_path):
                for file in files:
                    file_to_remove = os.path.join(subdir, file)
                    if os.path.isfile(file_to_remove):
                        os.remove(file_to_remove)
    else:
        os.makedirs(DATA_DIRECTORY)
