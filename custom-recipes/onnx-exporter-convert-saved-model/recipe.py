from dataiku import default_project_key
from dataiku import Model
from dataiku import Folder
from dataiku.customrecipe import get_input_names_for_role
from dataiku.customrecipe import get_output_names_for_role
from dataiku.customrecipe import get_recipe_config
from dku_onnx_exporter_helper.utils import get_keras_model_from_saved_model
from dku_onnx_exporter_helper.utils import convert_from_keras_to_onnx

class Main:
    def __init__(self):
        self.folder = None
        self.output_file_path = None
        self.batch_size = None
        self.overwrite_output_model = None
        self.model = None
        self.keras_model = None
        self.onnx_model = None
        self.float_32 = None

    def get_inputs(self):
        self.folder = Folder(get_output_names_for_role("folder_id")[0])
        self.output_file_path = get_recipe_config()['output_model_path']
        self.overwrite_output_model = get_recipe_config()['overwrite_output_model']
        self.batch_size = int(get_recipe_config()['batch_size'])
        if not get_recipe_config()['show_batch_size']:
            self.batch_size = -1
        self.model = Model(get_input_names_for_role("saved_model_id")[0])
        self.float_32 = get_recipe_config()["float_32"]

    def validation(self):
        if self.folder.get_path_details(self.output_file_path)['exists'] and not self.overwrite_output_model:
            raise ValueError('Output file already exists, check overwrite box or change output path')
        if not self.output_file_path:
            raise ValueError('Output model path can not be blank')

    def write_output(self):        
        with self.folder.get_writer(self.output_file_path) as w:
            w.write(self.onnx_model.SerializeToString())
    
    def run(self):
        self.get_inputs()
        self.validation()
        self.keras_model = get_keras_model_from_saved_model(default_project_key(), self.model)
        self.onnx_model = convert_from_keras_to_onnx(self.keras_model, self.batch_size, self.float_32)
        self.write_output()

main = Main()
main.run()
    
