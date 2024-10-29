from git import Repo
from pathlib import Path
import shutil
import subprocess
import sys

import toml

# The name of the folder that is to be created to store all the modules
SETUP_FOLDER_NAME = "cvep_speller_env"
BRANCH_NAME = SETUP_FOLDER_NAME  # used within each module

CONTROL_ROOM_URL = "git@github.com:bsdlab/dp-control-room.git"
DECODER_URL = "git@github.com:thijor/dp-cvep-decoder.git"
SPELLER_URL = "git@github.com:thijor/dp-cvep-speller.git"
LSL_URL = "git@github.com:bsdlab/dp-lsl-recording.git"

EEG_LSL_STREAM_NAME = "BioSemi"
MARKER_LSL_STREAM_NAME = "cvep-speller-stream"
DECODER_OUTPUT_LSL_STREAM_NAME = "cvep-decoder-stream"

# ----------------------------------------------------------------------------
# Install requirements
# ----------------------------------------------------------------------------

requ_modules = ["GitPython"]

for mod in requ_modules:
    try:
        __import__(mod)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", mod])

# ----------------------------------------------------------------------------
# Grab the git repositories
# ----------------------------------------------------------------------------

root_dir = Path(SETUP_FOLDER_NAME)
try:
    root_dir.mkdir(exist_ok=False)
except FileExistsError:
    print(f"Directory `{root_dir}` already exists. Exiting.")
    q = input("Do you want to overwrite it? [y/N] ")
    if q == "y":
        shutil.rmtree(root_dir)
        root_dir.mkdir()
    else:
        exit(1)

# SSH ide via the Repo.clone_from did not work -> use manual subprocess calls
repos = []
repo_dirs = ["dp-control-room", "dp-cvep-decoder", "dp-cvep-speller", "dp-lsl-recording"]
for url, repo_dir in zip([CONTROL_ROOM_URL, DECODER_URL, SPELLER_URL, LSL_URL], repo_dirs):
    cmd = f'git clone -v -- {url} {SETUP_FOLDER_NAME}/{repo_dir}'
    subprocess.run(cmd, shell=True)
    repos.append(Repo(root_dir / repo_dir))

# for each repo -> create a branch for the experiment
# Keep a branch for the local setup to separate local specific changes
# from general bugfixes and features (which would then be merged back to `main`)
for repo in repos:
    branch = repo.create_head(BRANCH_NAME)
    branch.checkout()

# ----------------------------------------------------------------------------
# Derived paths
# ----------------------------------------------------------------------------

# Data directory relative to SETUP_FOLDER_NAME
DATA_DIR = root_dir.joinpath("./data").resolve()
CODES_FILE = root_dir.joinpath("dp-cvep-speller/cvep_speller/codes/mgold_61_6521.npz")
CAP_FILE = root_dir.joinpath("dp-cvep-decoder/cvep_decoder/caps/thielen7.loc")

# ----------------------------------------------------------------------------
# Create configs
# ----------------------------------------------------------------------------

#
# >>> for dp-control-room
#

control_room_cfg = f"""

[python]
modules_root = '../'                                                            


# -------------------- Cvep Decoder  ----------------------------------------
[python.modules.dp-cvep-decoder]                                        
    type = 'decoding'
    port = 8083
    ip = '127.0.0.1'

# -------------------- Controller  ----------------------------------------- 
[python.modules.dp-cvep-speller]                                     
    type = 'paradigm'
    port = 8084
    ip = '127.0.0.1'
    retry_connection_after_s = 5  # Module start-up is very slow due to psychopy

# -------------------- LSL recording -----------------------------------------
[python.modules.dp-lsl-recording]                                      
    type = 'recording'
    port = 8082                                                                 
    ip = '127.0.0.1'


[macros]

[macros.run_training]
    name = 'RUN TRAINING'
    description = 'Run the paradigm offline to collect calibration data'
[macros.run_training.default_json]
    fname = 'sub-P001_ses-S001_run-001_task-training'
    data_root = '{str(DATA_DIR.resolve())}'
    delay_s = 0.5                  # delay inbetween commands -> time for LSL recorder to respond
[macros.run_training.cmds]
    # [<target_module>, <PCOMM>, <kwarg_name1 (optional)>, <kwarg_name2 (optional)>]
    com1 = ['dp-lsl-recording', 'UPDATE']
    com2 = ['dp-lsl-recording', 'SELECT_ALL']
    com3 = ['dp-lsl-recording', 'SET_SAVE_PATH', 'fname=fname', 'data_root=data_root']
    com4 = ['dp-lsl-recording', 'RECORD']

[macros.stop_streaming]
    name = 'STOP_LSL_RECORDING'
    description = 'stop the offline recording'
[macros.stop_streaming.cmds]
    com1 = ['dp-lsl-recording', 'STOPRECORD']

[macros.run_online]
    name = 'RUN ONLINE'
    description = 'Run the paradigm online - this requires a trained model to be present'
[macros.run_online.default_json]
    fname = 'sub-P001_ses-S001_run-001_task-online'
    data_root = '{str(DATA_DIR.resolve())}' 
[macros.run_online.cmds]
    # [<target_module>, <PCOMM>, <kwarg_name1 (optional)>, <kwarg_name2 (optional)>]
    com1 = ['dp-lsl-recording', 'UPDATE']
    com2 = ['dp-lsl-recording', 'SELECT_ALL']
    com3 = ['dp-lsl-recording', 'SET_SAVE_PATH', 'fname=fname', 'data_root=data_root']
    com4 = ['dp-lsl-recording', 'RECORD']
    com5 = ['dp-cvep-decoder', 'DECODE ONLINE']
"""

control_room_cfg_pth = Path(
    "./cvep_speller_env/dp-control-room/configs/cvep_speller.toml"
)
with open(control_room_cfg_pth, "w") as f:
    f.write(control_room_cfg)

#
# >>> for dp-cvep-decoder
#

decoder_cfg_pth = root_dir.joinpath("dp-cvep-decoder/configs/decoder.toml")
cfg = toml.load(decoder_cfg_pth)

cfg["cvep"]["capfile"] = str(CAP_FILE.resolve())

cfg["training"]["out_file"] = str(DATA_DIR.joinpath(
    "./dp-cvep/sub-P001_ses-S001_classifier.joblib"
).resolve())
cfg["training"]["out_file_meta"] = str(DATA_DIR.joinpath(
    "./dp-cvep/sub-P001_ses-S001_classifier.meta.json"
).resolve())
cfg["training"]["data_root"] = str(DATA_DIR.resolve())
cfg["training"]["codes_file"] = str(CODES_FILE.resolve())

cfg["training"]["features"]["data_stream_name"] = EEG_LSL_STREAM_NAME
cfg["training"]["features"]["lsl_marker_stream_name"] = MARKER_LSL_STREAM_NAME
cfg["training"]["features"]["selected_channels"] = [
    "EX1", "EX2", "EX3", "EX4", "EX5", "EX6", "EX7",
]

cfg["training"]["decoder"]["event"] = "duration"
cfg["training"]["decoder"]["encoding_length_s"] = 0.3
cfg["training"]["decoder"]["tmin_s"] = 0.1
cfg["training"]["decoder"]["target_accuracy"] = 0.999

cfg["online"]["classifier"]["file"] = str(DATA_DIR.joinpath(
    "./dp-cvep/sub-P001_ses-S001_classifier.early_stop.joblib"
).resolve())
cfg["online"]["classifier"]["meta_file"] = str(DATA_DIR.joinpath(
    "./dp-cvep/sub-P001_ses-S001_classifier.meta.json"
).resolve())

cfg["online"]["input"]["lsl_stream_name"] = EEG_LSL_STREAM_NAME
cfg["online"]["input"]["lsl_marker_stream_name"] = MARKER_LSL_STREAM_NAME
cfg["online"]["input"]["selected_channels"] = [
    "EX1", "EX2", "EX3", "EX4", "EX5", "EX6", "EX7",
]

cfg["online"]["output"]["lsl_stream_name"] = DECODER_OUTPUT_LSL_STREAM_NAME

cfg["online"]["eval"]["start"]["marker"] = "start_trial"
cfg["online"]["eval"]["start"]["max_time_s"] = 4.3

# remove unnecessary
cfg["online"]["eval"].pop("eval_after_nsamples")
cfg["online"]["eval"].pop("marker")

toml.dump(cfg, open(decoder_cfg_pth, "w"))

#
# >>> for dp-cvep-speller
#

speller_cfg_pth = root_dir.joinpath("dp-cvep-speller/configs/speller.toml")
cfg = toml.load(speller_cfg_pth)

cfg["run"]["online"]["decoder"]["lsl_stream_name"] = DECODER_OUTPUT_LSL_STREAM_NAME

cfg["speller"]["screen"]["resolution"] = [2560, 1440]

toml.dump(cfg, open(speller_cfg_pth, "w"))

# ----------------------------------------------------------------------------
# Create single run script in the control room
# ----------------------------------------------------------------------------

platform = sys.platform
suffix = ".ps1" if platform == "win32" else ".sh"

script_file = root_dir.resolve() / "dp-control-room" / f"run_cvep_experiment{suffix}"

with open(script_file, "w") as f:
    f.write(
        f"""
        python -m control_room.main --setup_cfg_path="{control_room_cfg_pth.resolve()}"
        """
    )
