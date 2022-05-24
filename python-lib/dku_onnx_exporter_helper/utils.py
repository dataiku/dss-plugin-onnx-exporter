from h5py import File
from keras.models import load_model
from tf2onnx.convert import from_keras
from io import BytesIO
from os.path import join as join_path
from os.path import isfile
from dataiku.core import doctor_constants as constants
from dataiku.core.base import get_dip_home
from distutils.version import LooseVersion
import onnx

def check_keras_version(folder, model_path):
    check_keras_version_from_path(get_model_file(folder, model_path))

def check_keras_version_from_path(model_path):
    try:
        with File(model_path) as model_h5:
            model_weights = model_h5["model_weights"]
            if "keras_version" in model_weights.attrs:
                keras_version = model_weights.attrs["keras_version"]
                # Same trick as the keras lib itself for cross-compatibility :
                # https://github.com/keras-team/keras/blob/master/keras/saving/hdf5_format.py#L215
                if hasattr(keras_version, 'decode'):
                    original_keras_version = LooseVersion(keras_version.decode('utf-8'))
                else:
                    original_keras_version = LooseVersion(keras_version)
    except Exception as e:
        raise ValueError('Could not extract the model weights from the .h5 file. : {}. Was it generated with the keras command model.save(...) ?'.format(e))

    if not(LooseVersion('2.0.6') <= original_keras_version):
        raise ValueError("The version of keras you are using  ({}) has compatibility issues with tf2onnx".format(original_keras_version))

    
        
def convert_from_keras_to_onnx(keras_model, batch_size, float_32):
    try:
        onnx_model = from_keras(keras_model)[0]
    except Exception as e:
        raise ValueError('Error while converting with tf2onnx: {}'.format(e))
    add_batch_size(onnx_model, batch_size)
    if float_32:
        force_type_to_float32(onnx_model)
    return onnx_model
    
def add_batch_size(onnx_model, batch_size):
    if batch_size != -1:
        if batch_size < 0:
            raise ValueError("Batch size can't be negative")
        for graph_input in onnx_model.graph.input:
            graph_input.type.tensor_type.shape.dim[0].ClearField('dim_param')
            graph_input.type.tensor_type.shape.dim[0].dim_value = batch_size
        print("Correctly set batch size to: {}".format(batch_size))

def force_type_to_float32(onnx_model):
    for graph_input in onnx_model.graph.input:
        graph_input.type.tensor_type.elem_type = onnx.TensorProto.DataType.FLOAT
    for graph_output in onnx_model.graph.output:
        graph_output.type.tensor_type.elem_type = onnx.TensorProto.DataType.FLOAT
    
def get_keras_model_from_folder(folder, path):
    return try_load_model(File(get_model_file(folder, path)))

def try_load_model(path):
    try:
        return load_model(path)
    except Exception as e:
        raise ValueError('The .h5 file cannot be read as a keras model. Was it generated with the keras command model.save(...) ? : {}'.format(e))

def get_keras_model_from_saved_model(project_key, model):
    model_location = get_keras_model_location_from_saved_model(project_key, model)
    check_keras_version_from_path(model_location)
    return load_model(model_location)

def get_keras_model_location_from_saved_model(project_key, model):
    active_model_version = get_active_version(model)
    dip_home = get_dip_home()
    model_folder = join_path(dip_home, "saved_models", project_key, model.get_id(), "versions",
                                active_model_version["versionId"])
    model_location = join_path(model_folder, constants.KERAS_MODEL_FILENAME)

    if not isfile(model_location):
        raise ValueError("This saved model cannot be exported to ONNX. Exporting to ONNX is only supported for models trained with the visual Deep Learning")

    return model_location

def get_model_file(folder, path):
    model_stream = folder.get_download_stream(path)
    model_file = BytesIO()
    model_file.write(model_stream.read())
    model_file.seek(0)
    return model_file

def get_active_version(model):
    filtered = [x for x in model.list_versions() if x["active"]]
    if len(filtered) == 0:
        return None
    else:
        return filtered[0]
 
