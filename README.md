# Dareplane c-VEP Demo

This repository contains the documentation and resources to set up a [Dareplane](https://github.com/bsdlab/Dareplane) c-VEP demo. 

## Setup

1. Make a conda environment with Python 3.10 (not higher, as PsychoPy needs 3.10) as follows:

```
conda create --name dp-cvep python=3.10.15
```

2. Activate the `dp-cvep` conda environment as follows:

```
conda activate dp-cvep
```

3. Run the setup script `setup_cvep_demo.py`. It downloads all required modules and edits the `config.toml` files ready for a demo in the labs. 

4. In the `dp-cvep` environment, install all the requirements of each of the downloaded Dareplane modules (control room, LSL recorder, speller, decoder). Do so by changing the directory to the module root that contains the `requirements.txt` as follows:

```
cd path/to/module
pip install -r requirements.txt
```

5. Install the LSL Recorder (https://github.com/labstreaminglayer/App-LabRecorder) and make sure it is alive (on the background).

The demo has been set up for the lab (MM 01.422). If you want to run the demo elsewhere, please check the speller config in `dp-cvep-speller/configs/speller.toml`, specifically:
  - The screen ID to open the speller UI at the correct screen: `speller.screen.id`
  - The screen resolution of that screen: `speller.screen.resolution`
  - The screen refresh rate of that screen: `speller.screen.refresh_rate_hz`

If you are not using actual EEG, but want to use simulated EEG, for instance because you are testing the software, please do steps 6-8 instead of starting a normal EEG stream:

6. Clone the Dareplane mockup streamer (https://github.com/bsdlab/dp-mockup-streamer).
7. In a separate terminal, in the same dp-cvep conda environment, run the mockup streamer from its module root as follows:

```
cd path/to/dp-mockup-streamer
python -m mockup_streamer.random_cli --stream_name="BioSemi" --sfreq=512
```

8. Change the following in the dp-cvep-decoder `decoder.toml` config:
   - The selected channels: `data.selected_channels = [0, 1, 2, 3, 4, 5, 6]`

## Running

1. Activate the `dp-cvep` conda environment as follows:

```
conda activate dp-cvep
```

2. In the control room directory, there is a file called `run_cvep_experiment`. In it is a Python command to start the control room properly. Run it from the control room root. I.e., perform something like the following:

```
cd path/to/dp-control-room
python -m control_room.main --setup_cfg_path="path/to/dp-control-room/configs/cvep_speller.toml"
```

3. Open a browser and go to `localhost:8050`. You should see the control room. If you started the EEG source (actual or simulated), you should see this at the left top.

4. Training 
   1. To start the training phase, in this order, press “TRAINING” in the dp-cvep-speller (starts the speller UI) and “RUN TRAINING” in the Macros (starts the LSL recording). 
   2. The speller waits for a keypress to continue, press key c.
   3. The speller runs 10 cued trials (indicated by green cues), then stops. Press “STOP LSL RECORDING” in the macros (stops the LSL recording and saves the data). Press c to quit the speller.
   4. The speller waits for a keypress to finish, press key c. 
   5. Note, you can press q or escape to stop the speller manually.

5. Calibration
   1. Now you have training data, so we can calibrate the model. Press “FIT MODEL” in the dp-cvep-decoder (calibrated the model). It prints the performance in the log (left bottom), and shows this in a figure. Close the figure to continue. It saves the calibrated classifier to file. 
 
6. Online
   1. To start the online phase, in this order, press “LOAD MODEL” in dp-cvep-decoder (loads the trained model), “CONNECT DECODER” in dp-cvep-decoder (starts the decoder), “ONLINE” in dp-cvep-speller (starts the speller UI), “DECODE ONLINE” in dp-cvep-decoder (starts decoding), “RUN ONLINE” in Macros (starts the LSL recording). 
   2. The speller waits for a keypress to continue, press key c 
   3. The speller runs 999 trials, then stops. The classifier is applied using dynamic stopping, so trials will stop as soon as possible. If a symbol is selected, it is highlighted in blue and added to the text. If !! is spelled, the speller is stopped. The < symbol performs a backspace.
   4. The speller waits for a keypress to finish, press key c.
   5. Note, you can press q or escape to stop the speller manually. 

## Troubleshooting
There are some known issues and "solutions": 
- If you do not get the control room started, try the following: 
  - Kill all Python processes (e.g., hit ctrl+c many times, and/or `pkill -f python`), and restart.
  - Make sure there are no other LSL streams running yet (e.g., the EEG/mockup stream). Start the control room first. Only when the control room is alive, start any other streams.
  - First start without the LSL recorder, it crashes. Then restart with the Recorder, then it works. Magic.
- If you ran "FIT MODEL" and you get the error saying 'No training files found', double-check the saved data in `data`. For instance, the file should have capitals for P001 and S001, which are lowercase depending on the LSL Recorder version.
- If you just ran the speller (either "TRAINING" or "ONLINE"), and want to run it again, it might complain that it 'wants to add keys that already exist'. Somehow the speller is not closed fully the previous time, so cannot reopen. Kill everything and restart the control room. 
- If you just ran "ONLINE" and stopped the speller in any way, the decoder will still be running. Depending on your needs, stop the decoder by pressing "STOP" in dp-cvep-decoder.
- If you run the online phase and want to record the data, pressing "RUN ONLINE" might crash the decoder stream. A workaround is to not press "RUN ONLINE", but instead record manually via the LSL Recorder app.
