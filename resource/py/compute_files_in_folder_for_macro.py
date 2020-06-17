from dataiku import Folder
import os

def do(payload, config, plugin_config, inputs):
    if config.get('input_folder_id'):
        folder = Folder(config.get('input_folder_id'))
        paths = folder.list_paths_in_partition()
        choices = []
        for file_name in paths:
            extension = os.path.splitext(file_name)[1]
            if  extension == '.h5':
                choices.append({"value": file_name, "label": file_name})
        return {"choices": choices}
    return {}