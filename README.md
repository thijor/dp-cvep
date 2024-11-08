# Dareplane c-VEP Demo

This repository contains the documentation and resources to set up a [Dareplane](https://github.com/bsdlab/Dareplane) c-VEP demo. 

## Setup

1. Make a conda environment with Python 3.10 (not higher, as PsychoPy needs 3.10) as follows:

```conda create --name dp-cvep```

2. Activate the `dp-cvep` conda environment as follows:

```conda activate do-cvep```

3. Run the setup script `setup_cvep_demo.py`. It downloads all required modules and edits the `config.toml` files ready for a demo in the labs. 

4. In the `dp-cvep` environment, install all the requirements of each of the downloaded Dareplane modules that we be used as follows:

```pip install -r requirements.txt```

5. Install the LSL Recorder (https://github.com/labstreaminglayer/App-LabRecorder) and make sure it is alive (on the background).

The demo has been set up for the lab (MM 01.422). If you want to run the demo elsewhere, please check the dp-cvep-speller `speller.toml` config:
  - The screen ID to open the speller UI at the correct screen: `speller.screen.id`
  - The screen resolution of that screen: `speller.screen.resolution`
  - The screen refresh rate of that screen: `speller.screen.refresh_rate_hz`

If you are not using actual EEG, but want to use simulated EEG, for instance because you are testing the software, please do the following instead of starting a normal EEG stream:

6. Clone the Dareplane mock streamer (https://github.com/bsdlab/dp-mockup-streamer). 
7. Run it as follows:

```python -m mockup_streamer.random_cli --stream_name="BioSemi" --sfreq=512```

8. Change the following in the dp-cvep-decoder `decoder.toml` config:
   - The selected channels: `training.features.selected_channels = [0, 1, 2, 3, 4, 5, 6]`
   - The selected channels: `online.input.selected_channels = [0, 1, 2, 3, 4, 5, 6]`

## Running

1. Activate the `dp-cvep` conda environment as follows:

```conda activate do-cvep```

2. In the control room directory, there is a file called `run_cvep_experiment`. In it is a Python command to start the control room properly. Run it from the control room directory, with the conda environment active. 

3. Open a browser and go to `localhost:8050`. You should see the control room.

4. Training 
   1. To start the training phase, in this order, press “training” in the speller (starts the speller UI) and “run_training” in the macros (starts the LSL recording). 
   2. The speller waits for a keypress to continue, press key c.
   3. The speller runs 10 cued trials (indicated by green cues), then stops. Press “stop LSL” in the macros (stops the LSL recording and saves the data). Press c to quit the speller.

5. Calibration
   1. Now you have training data, so we can calibrate the model. Press “fit model” in the decoder (calibrated the model). It prints the performance in the log (left bottom), and shows this in a figure. Close the figure to continue. 
 
6. Online
   1. To start the online phase, in this order, press “load model” in decoder (loads the trained model), “connect decoder” in decoder (starts the decoder), “online” in speller (starts the speller UI), “start decoding” in decoder (starts decoding), “start online” in macros (starts the LSL recording). 
   2. The speller waits for a keypress to continue, press key c 
   3. The speller runs 999 trials, then stops. The classifier is applied using dynamic stopping, so trials will stop as soon as possible. If a symbol is selected, it is highlighted in blue and added to the text. If !! is spelled, the speller is stopped. You can press q or escape to stop the speller manually. The < symbol performs a backspace.

## Troubleshooting
There are some known issues and "solutions":
- Sometimes the connection(s) get refused when starting the control room. Typically, just kill all Python processes (e.g., hit ctrl+c many times, and/or `pkill -f python`), and restart.
- On macOS, the control room does not start the first time when the LSL recorder is on. A work-around: first start without the recorder, it crashes. Then restart with the Recorder, then it works. Magic.
- If you just ran the speller (either in training or online), and want to run it again, it might complain that it “wants to add keys that already exist”. Somehow the speller is not closed fully the previous time, so cannot reopen. Kill everything and restart the control room. 
- If you just ran the online phase and stopped the speller in any way, the decoder will still be running. Depending on your needs, stop the decoder.
