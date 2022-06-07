from dataiku.runnables import Runnable
from dataiku import Folder
from os.path import splitext as os_splitext
from os.path import split as os_split
from dku_onnx_exporter_helper.utils import get_keras_model_from_folder
from dku_onnx_exporter_helper.utils import check_keras_version
from dku_onnx_exporter_helper.utils import convert_from_keras_to_onnx

class MyRunnable(Runnable):
    """The base interface for a Python runnable"""

    def __init__(self, project_key, config, plugin_config):
        """
        :param project_key: the project in which the runnable executes
        :param config: the dict of the configuration of the object
        :param plugin_config: contains the plugin settings
        """
        self.project_key = project_key
        self.config = config
        self.plugin_config = plugin_config
        
        self.input_folder = self._get_input_folder()
        self.output_folder = self._get_output_folder()
            
        self.model_path, self.model_name = self._get_model_path_and_name()
        
        self.overwrite_output_model = self.config.get('overwrite_output_model')
        self.output_file_path = self._get_ouput_file_path()
        self.batch_size = self._get_batch_size()
        self.float_32 = self.config.get('float_32')
        
    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        """
        Loads a h5 file, converts it with tf2onnx, saves it back in the folder, builds a url for the download
        """
        check_keras_version(self.input_folder, self.model_path)
        keras_model = get_keras_model_from_folder(self.input_folder, self.model_path)
        onnx_model = convert_from_keras_to_onnx(keras_model, self.batch_size, self.float_32)
        self._write_onnx_model_to_folder(onnx_model)
        
        return self._build_download_url()
    
    def _get_batch_size(self):
        batch_size = int(self.config.get('batch_size'))
        if not self.config.get('show_batch_size'):
            batch_size = -1
        return batch_size
    
    def _get_model_path_and_name(self):
        model_path = self.config.get('model_path', '')
        if not model_path:
            raise ValueError('Model path should not be empty')
        model_name, extension = os_splitext(os_split(model_path)[1])
        if  extension!= '.h5':
            raise ValueError("This macro requires a .h5 file, {} given".format(extension))
        return model_path, model_name
    
    def _get_input_folder(self):
        input_folder_id = self.config.get('input_folder_id', '')
        if not input_folder_id:
            raise ValueError('Input folder has to be selected')
        return Folder(input_folder_id, project_key=self.project_key)
    
    def _get_output_folder(self):
        output_folder_id = self.config.get('output_folder_id', None)
        if output_folder_id and output_folder_id != '?':
            return Folder(output_folder_id, project_key=self.project_key)
        else:
            return self.input_folder
    
    def _get_ouput_file_path(self):
        output_file_path = self.config.get('output_model_path', '')
        if not output_file_path:
            raise ValueError('Output model path can not be blank')
        return output_file_path
    
    def _write_onnx_model_to_folder(self, onnx_model):
        if self.output_folder.get_path_details(self.output_file_path)['exists'] and not self.overwrite_output_model:
            raise ValueError('Output file already exists, check overwrite box or change output path')
        with self.output_folder.get_writer(self.output_file_path) as w:
            w.write(onnx_model.SerializeToString())
            
    def _build_download_url(self):
        return "/dip/api/managedfolder/download-item/?contextProjectKey={}&projectKey={}&obdId={}&path=%2F{}".format(
            self.project_key,
            self.project_key,
            self.output_folder.get_id(),
            self.output_file_path
        )
        