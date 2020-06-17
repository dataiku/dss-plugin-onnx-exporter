from dataiku import Folder
import os

def do(payload, config, plugin_config, inputs):
    for recipe_input in inputs:
        if recipe_input["role"] == "input_folder_id":
            folder = Folder(recipe_input["fullName"])
    paths = folder.list_paths_in_partition()
    choices = []
    for file_name in paths:
        extension = os.path.splitext(file_name)[1]
        if  extension == '.h5':
            choices.append({"value": file_name, "label": file_name})
    return {"choices": choices}