
PLUGIN_VERSION=1.0.0
PLUGIN_ID=onnx-exporter

plugin:
	cat plugin.json|json_pp > /dev/null
	rm -rf dist
	mkdir dist
	zip --exclude "*.pyc" -x "resource/doc/*" -r dist/dss-plugin-${PLUGIN_ID}-${PLUGIN_VERSION}.zip code-env custom-recipes js python-lib python-runnables resource plugin.json
