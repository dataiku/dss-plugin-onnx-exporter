from dataiku import Folder
from dataiku.customrecipe import get_input_names_for_role
from dataiku.customrecipe import get_output_names_for_role
from dataiku.customrecipe import get_recipe_config
from dku_onnx_exporter_helper.utils import check_keras_version
from dku_onnx_exporter_helper.utils import get_keras_model_from_folder
from dku_onnx_exporter_helper.utils import convert_from_keras_to_onnx
from os.path import splitext as os_splitext
from os.path import split as os_split


class Main:
    def __init__(self):
        self.input_folder = None
        self.output_folder = None
        self.output_file_path = None
        self.batch_size = None
        self.overwrite_output_model = None
        self.model_path = None
        self.model_name = None
        self.keras_model = None
        self.onnx_model = None
        
    def get_inputs(self):
        self.input_folder = Folder(get_input_names_for_role("input_folder_id")[0])
        output_folder_id = get_output_names_for_role("output_folder_id")[0]
        self.output_folder = Folder(output_folder_id)
        self.output_file_path = get_recipe_config()['output_model_path']
        self.batch_size = int(get_recipe_config()['batch_size'])
        if not get_recipe_config()['show_batch_size']:
            self.batch_size = -1
        self.overwrite_output_model = get_recipe_config()['overwrite_output_model']
        self.model_path = get_recipe_config()['model_path']
        self.model_name = os_splitext(os_split(self.model_path)[1])[0]
        self.float_32 = get_recipe_config()["float_32"]
    
    def validate(self):
        if self.output_folder.get_path_details(self.output_file_path)['exists'] and not self.overwrite_output_model:
            raise ValueError('Output file already exists, check overwrite box or change output path')
        if not self.output_file_path:
            raise ValueError('Output model path can not be blank')     
        check_keras_version(self.input_folder, self.model_path)

    def load_h5_to_keras(self):
        self.keras_model = get_keras_model_from_folder(self.input_folder, self.model_path)
        
    def write_output(self):
        with self.output_folder.get_writer(self.output_file_path) as w:
            w.write(self.onnx_model.SerializeToString())
    
    def run(self):
        self.get_inputs()
        self.validate()
        self.load_h5_to_keras()
        self.onnx_model = convert_from_keras_to_onnx(self.keras_model, self.batch_size, self.float_32)
        self.write_output()

main = Main()
main.run()