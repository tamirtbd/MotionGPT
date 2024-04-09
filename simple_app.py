from flask import Flask, request, jsonify, json, send_file
import subprocess
from os import environ
from pathlib import Path
# from flasgger import Swagger

context = environ.get('CONTEXT')

if context == 'LOCAL':
    localconf = Path('./configs/local.config')

    if not localconf.exists():
        print("Local configuration doesn't exist, create one using the ./config/docker.json template")
        raise FileExistsError()

    with open(localconf.absolute()) as fh:
        config = json.load(fh)
else:
    with open('./configs/docker.config') as fh:
        config = json.load(fh)

outputdir  = config.get('output_dir')
pythonpath = config.get('python_path')
repopath   = config.get('repo_path')
blender_bin_path = config.get('blender_bin')
blender_script_path = Path(repopath).joinpath('scripts/blender_npy2usd.py')
blender_scene_path  = Path(repopath).joinpath('assets/smplx_rest_pose.blend')

app = Flask(__name__)
# swagger = Swagger(app)

@app.route("/run", methods=["POST"])
def run_script():
  """
  This route receives a POST request with the prompt for the MotionGPT repo as an argument.
  It then runs the script with those arguments and returns the output.
  """
  try:
    # Get arguments from the request body
    data = request.get_json()
    prompt = data.get("prompt")

    # Ensure both arguments are present
    if prompt is None:
      return jsonify({"error": "Missing prompt"}), 400

    command = f'{pythonpath} {repopath}/bare.py --prompt "{prompt}" --output_dir "{outputdir}"'

    # Run the script using subprocess and capture the output
    output = subprocess.run(command.split(), capture_output=True, text=True).stdout.strip()

    p1 = jsonify({"output": output})
    npyfile_path = p1.json['output']
    start = npyfile_path.find('[')+1
    end   = npyfile_path.find(']')
    npyfile_path = npyfile_path[start:end]

    # Blender script
    nicename = prompt.replace(" ", "_")
    usd_export_path = Path(outputdir).joinpath(f'{nicename}.usd')
    command = f"{blender_bin_path} {blender_scene_path} -b -P {blender_script_path} --npy_pose_file_path {npyfile_path} --export_path {usd_export_path}"

    output = subprocess.run(command.split(), capture_output=True, text=True).stdout.strip()
    p2 = jsonify({"output": output})

    debug_data = {'mGPT': p1.json, 'USD': p2.json}
    usdpath = Path(usd_export_path)
    if not usdpath.exists():
        return jsonify({"error": "File not found"}), 404

    return send_file(usd_export_path)

  # TODO: Delete npy and usd file as post process

  except Exception as e:
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
  app.run(host=config['host'], debug=False, port=8089)