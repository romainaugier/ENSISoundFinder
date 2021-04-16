# Database #


import os, json, threading, sys

import convert

from logger import Logger


def process_database_folder(path, is_pdf, database_path):
    # process either a folder or a pdf file to initialize the database
    
    if is_pdf:
    # process a pdf file
        convert.convert_pdf_to_json(path, database_path)
    else:
    # initialize any other folder found in the root dir of the sound_lib_path
        convert.convert_folder_to_database(path, database_path)



def init_database(sound_lib_path, database_path, **kwargs):
    # initialize the database

    progress_function = kwargs.get("progress", None)
    message_function = kwargs.get("message", None)

    sound_library = os.listdir(sound_lib_path)

    files_to_convert = []

    for folder in sound_library:
        current_folder_path = os.path.join(sound_lib_path, folder)

        if os.path.isfile(current_folder_path): continue

        if folder == ".DS_Store": continue

        elif "_Sound Ideas def" in folder:
        # initialize sound_ideas_def libraries
            sound_ideas_path = os.path.join(sound_lib_path, folder)
            sound_ideas_folder = os.listdir(sound_ideas_path)

            for si_folder in sound_ideas_folder:
                if os.path.isfile(si_folder): continue
                if "DS" in si_folder or "ds" in si_folder or "Store" in si_folder: continue

                current_si_folder_path = os.path.join(sound_ideas_path, si_folder)

                for file in os.listdir(current_si_folder_path):
                    current_file_path = os.path.join(current_si_folder_path, file)

                    filename, extension = os.path.splitext(file) 

                    if extension == ".pdf" and not filename.startswith("._"):

                        new_file = filename + ".json"
                        new_file_path = os.path.join(database_path, new_file)
                        file_to_convert = {
                            "Current Path" : current_file_path,
                            "Database Path" : new_file_path,
                            "Is PDF" : True
                        }

                        files_to_convert.append(file_to_convert)

        else:
        # initialize any other folder found in the root dir of the sound_lib_path
            convert.convert_folder_to_database(current_folder_path, database_path, progress=progress_function, message=message_function)
            file_to_convert = {
                            "Current Path" : current_folder_path,
                            "Database Path" : database_path,
                            "Is PDF" : False
                        }

            files_to_convert.append(file_to_convert)

    Logger.message(files_to_convert)

    thread_list = []

    for item in files_to_convert:
        thread = threading.Thread(target=process_database_folder, args=(item["Current Path"], item["Is PDF"], item["Database Path"],))
        thread.daemon = True
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    Logger.message("Database initialized")



def load_database(database_path, **kwargs):
    # load the database in memory for a faster access

    progress_function = kwargs.get("progress", None)

    db_files = os.listdir(database_path)

    if len(db_files) == 0:
        Logger.error("Database is empty. Try to reinitalize it using the settings menu and restart ENSISoundLoader")
        return []

    progress_jump = 100.0 / len(db_files)

    progress = 0

    database = []

    for file in db_files:
        name, ext = os.path.splitext(file)

        if ext != ".json":
            continue

        else:
            file_path = os.path.join(database_path, file)

            with open(file_path, "r") as f:
                file_data = json.load(f)

            for element in file_data:
                database.append(element)

        progress += progress_jump
        progress_out = round(progress)

        if progress_function: progress_function(progress_out)

        if progress_out % 5 == 0 or progress_out == 1:
            Logger.console_progress_bar(f"Loading database : ", f" {progress_out}%", progress_out, 20)

    sys.stdout.write("\n")

    Logger.message("Database loaded successfully")
    Logger.message("ENSISoundFinder is ready to use")
    
    return database





