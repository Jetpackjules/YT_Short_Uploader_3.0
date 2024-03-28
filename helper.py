import subprocess
import os

def run(command):
    # Attempted fix for multiple conda locs:
    output = subprocess.run("where conda", text=True, capture_output=True).stdout
    conda_path = output.strip().split('\n')[0]
    env_name = os.environ["CONDA_PREFIX"].split(os.path.sep)[-1]
    # try:
    #     # Run your command and capture output and errors
    #     result = subprocess.run(f'{command}', check=True, capture_output=True, text=True, shell=True)
    # except subprocess.CalledProcessError as e:
    # print(e)
    # print("TRYING OTHER COMMAND!")

    # This almost always works:
    RESULT = subprocess.run(f'{conda_path} run -n {env_name} {command}', check=True, capture_output=True, text=True, shell=True)
    # print(RESULT)
    # print("Command RUN!")
