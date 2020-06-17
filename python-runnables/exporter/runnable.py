from dataiku.runnables import Runnable
from dataiku import Model
from dataiku import Folder
from dku_onnx_exporter_helper.utils import get_keras_model_from_saved_model
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
        self.folder = Folder(self._get_folder_id(), project_key=self.project_key)
        self.model = Model(self.config.get('saved_model_id'), project_key=self.project_key)
        self.model.list_versions()
        self.output_file_path = self._get_output_file_path()
        self.overwrite_output_model = self.config.get('overwrite_output_model')
        self.batch_size = self._get_batch_size()
        self.float_32 = self.config.get('float_32')
   
    def _get_batch_size(self):
        batch_size = int(self.config.get('batch_size'))
        if not self.config.get('show_batch_size'):
            batch_size = -1
        return batch_size
    
    def _get_folder_id(self):
        folder_id = self.config.get('folder_id', '')
        if not folder_id:
            raise ValueError('Output folder can not be blank')
        return folder_id
    
    def _get_output_file_path(self):
        output_file_path = self.config.get('output_model_path', '')
        if not output_file_path:
            raise ValueError('Output model path can not be blank')
        return output_file_path
    
    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        """
        Gets a saved model, converts it with keras2onnx, saves it back in the folder, builds a url for the download
        """
        
        keras_model = get_keras_model_from_saved_model(self.project_key, self.model)
        onnx_model = convert_from_keras_to_onnx(keras_model, self.batch_size, self.float_32)
        self._write_onnx_model_to_folder(onnx_model)
        
        return self._build_download_url()
    
    def _write_onnx_model_to_folder(self, onnx_model):
        if self.folder.get_path_details(self.output_file_path)['exists'] and not self.overwrite_output_model:
            raise ValueError('Output file already exists, check overwrite box or change output path')
        with self.folder.get_writer(self.output_file_path) as w:
            w.write(onnx_model.SerializeToString())
            
    def _build_download_url(self):
        return "/dip/api/managedfolder/download-item/?contextProjectKey={}&projectKey={}&obdId={}&path=%2F{}".format(
            self.project_key,
            self.project_key,
            self.folder.get_id(),
            self.output_file_path
        )