# Dataiku DSS ONNX exporter Plugin

With this Dataiku DSS plugin one can export `Visual Deep Learning` and `Keras .h5 models` to ONNX format

## When to use this plugin ?

This plugin aims at offering an easy way to deploy Deep learning models to various machines and environment with the onnx runtime. 
You can learn about all the languages, architectures and hardware accelaration available [here](https://microsoft.github.io/onnxruntime/)

## What is ONNX ?

ONNX is an open format built to represent machine learning models. ONNX defines a common set of operators - the building blocks of machine learning and deep learning models - and a common file format 
to enable AI developers to use models with a variety of frameworks, tools, runtimes, and compilers. [More info here](https://onnx.ai/about.html)

## Description

This DSS plugin offers the conversion of two kinds of models:
* Visual Deep Learning models trained with DSS 
* Keras `.h5 models`. 

This plugin contains one recipe and one macro for each conversion type.

## How to use the Macros ?

### Saved model to onnx macro

1. Create (if you don't already have it) a DSS python3 code env 
with the following packages (ie packages needed for Visual Deep Learning with keras == 2.1.6):
```tensorflow==1.8.0
keras==2.1.6
scikit-learn>=0.20,<0.21
scipy>=1.1,<1.2
statsmodels>=0.9,<0.10
jinja2>=2.10,<2.11
flask>=1.0,<1.1
h5py==2.7.1
pillow==5.1.0
```

2. Train a Visual Deep learning model in DSS with this code env
3. Install this plugin
4. Go the DSS Flow
5. Click on the saved model
6. In the right panel in the other actions section, click on `export to ONNX` #TODO add image 
7. Fill in the parameters #TODO add image 
8. Click on `RUN MACRO`
9. Click on `Download onnx model` #TODO add image 

#### Available parameters

- `Saved model` (DSS saved model): Visual Deep Learning model trained in DSS to convert
- `Output Folder` (DSS managed folder): Folder where the onnx model will be added
- `Output model path` (String): Path where the onnx model will be stored
- `Overwrite if exists` (boolean): Whether the model should overwrite the existing file at same path (if it already exists)
- `Fixed batch size` (boolean): Some runtimes do not support dynamic batch size and thereefore the size should be specified during export.
- `Batch size` (int) [optional]: Batch size of the model's input
- `Force input/output to Float (32 bits)` (int): Some runtimes do not support `Double`. Uncheck if your runtime supports `Double`
