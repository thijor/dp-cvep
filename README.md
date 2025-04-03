# Dareplane c-VEP Demo

This repository contains the documentation and resources to set up a demo of a c-VEP BCI for communication using [Dareplane](https://github.com/bsdlab/Dareplane). 

## Setup

1. Make a [conda](https://www.anaconda.com/download) environment with Python 3.10 (not higher, as PsychoPy needs 3.10) as follows:

```
conda create --name dp-cvep python=3.10.15
```

2. Activate the `dp-cvep` conda environment as follows:

```
conda activate dp-cvep
```

3. Run one of the setup scripts to download all required modules. Se below for explanations of the individual setup scripts and when to use which.

```
python setup_cvep_demo_antneuro.py
```
```
python setup_cvep_demo_biosemi.py
```
```
python setup_cvep_demo_mockup.py
```

4. After downloading the modules using the setup script, install all the requirements of each of the downloaded Dareplane modules (control room, LSL recorder, speller, decoder, potentially mockup stream). Do so by changing the directory to the module root that contains the `requirements.txt` and do the following, still from within the active `dp-cvep` environment:

```
pip install -r requirements.txt
```

5. Install the [LSL Lab Recorder](https://github.com/labstreaminglayer/App-LabRecorder). Make sure it is running on the background.

## Demo with the ANTneuro amplifier

This demo has been set up for the ANTneuro Eego amplifier together with one of the DCC lab's demo laptops. It uses 7 electrodes (Fpz, Cz, Pz, POz, Oz, O1, O2) and a screen with a 60 Hz presentation rate and 1920 x 1080 resolution.

During the setup, use:

```
python setup_cvep_demo_antneuro.py
```

## Demo with the Biosemi amplifier

This demo has been set up for the Biosemi Active2 amplifier together with the DCC lab setup in MM 01.422. It uses 7 EX electrodes (Fpz, Cz, POz, Oz, Iz, O1, O2) and a screen with a 60 Hz presentation rate and 2560 x 1440 resolution.

During the setup, use:

```
python setup_cvep_demo_biosemi.py
```

## Demo with a mockup EEG stream

This demo has been set up for when no EEG amplifier is available, for instance for testing. It uses 7 mock electrodes.

During the setup, use:

```
python setup_cvep_demo_mockup.py
```

This setup includes the [Dareplane mockup streamer](https://github.com/bsdlab/dp-mockup-streamer). To start it, in a separate terminal, in the same `dp-cvep` conda environment, run the mockup streamer from its module root as follows:

```
python -m mockup_streamer.random_cli --stream_name="mockup" --sfreq=512
```

## Changing the demo

If you want to run the with other settings, please consider the speller config in `dp-cvep-speller/configs/speller.toml` and the decoder config in `dp-cvep-decoder/configs/decoder.toml`. For instance:
- In the speller:
  - The screen ID to open the speller UI at the correct screen: `speller.screen.id = 1`
  - The screen resolution of that screen: `speller.screen.resolution = [1920, 1080]`
  - The screen refresh rate of that screen: `speller.screen.refresh_rate_hz = 60`
- In the decoder:
  - The selected channels: `data.selected_channels = [0, 1, 2, 3, 4, 5, 6]`
  - The channel cap and locations: `data.capfile = antneuro7.loc`

## Running the demo

1. Make sure you have the LSL Lab Recorder running.

2. Activate the `dp-cvep` conda environment as follows:

```
conda activate dp-cvep
```

3. In the control room directory, find the file `run_cvep_experiment`. In it is a Python command to start the control room. Run it from the control room root:

```
python -m control_room.main --setup_cfg_path="path/to/dp-control-room/configs/cvep_speller.toml"
```

4. Open a browser and go to `localhost:8050`. You should see the control room. If you started the EEG source (actual or simulated), you should see this at the left top.

5. Training 
   1. To start the training phase, in this order, press `TRAINING` in the dp-cvep-speller (starts the speller UI) and `RUN TRAINING` in the Macros (starts the LSL recording). 
   2. The speller waits for a keypress to continue, press key `c`.
   3. The speller runs 10 cued trials (indicated by green cues), then stops. 
   4. Press `STOP LSL RECORDING` in the macros (stops the LSL recording and saves the data). 
   5. The speller waits for a keypress to finish, press key `c`. 
   6. Note, you can press key `q` or `escape` to stop the speller at any time manually.

5. Calibration
   1. Now you have supervised training data, so we can calibrate the model. Press `FIT MODEL` in the dp-cvep-decoder (calibrated the model). It prints the performance in the log (left bottom), and shows a figure. 
   2. Close the figure to continue. 
   3. The calibrated classifier is saved to file automatically. 
 
6. Online
   1. To start the online phase, in this order, press `LOAD MODEL` in dp-cvep-decoder (loads the trained model), `CONNECT DECODER` in dp-cvep-decoder (starts the decoder), `ONLINE` in dp-cvep-speller (starts the speller UI), `DECODE ONLINE` in dp-cvep-decoder (starts decoding), `RUN ONLINE` in Macros (starts the LSL recording). 
   2. The speller waits for a keypress to continue, press key `c`. 
   3. The speller runs 999 trials, then stops. The classifier is applied using dynamic stopping, so trials will stop as soon as possible. If a symbol is selected, it is highlighted in blue and added to the text. If the `!` symbols is spelled twice in a row, the speller is stopped. The `<-` symbol performs a backspace. The `<<` symbol clears the sentence. The `>>` symbol accepts the autocomplete. The symbol showing a speaker activates text2speech with the currently spelled sentence. 
   4. The speller waits for a keypress to finish, press key `c`.
   5. Note, you can press `q` or `escape` to stop the speller at any time manually. 

## Troubleshooting

There are some known issues and "solutions": 
- If you do not get the control room started, try the following: 
  - Kill all Python processes (e.g., hold ctrl+c, and/or `pkill -f python`), and restart.
  - Make sure there are no other LSL streams running yet (e.g., the EEG/mockup stream). Start the control room first. Only when the control room is alive, start any other streams.
  - First start without the LSL recorder, it crashes. Then restart with the Recorder, then it works. Magic.
- If you ran `FIT MODEL` and you get the error saying 'No training files found', double-check the saved data in the `data` directory. For instance, the file should have capitals for P001 and S001, which are lowercase depending on the LSL Recorder version.
- If you just ran the speller (either `TRAINING` or `ONLINE`), and want to run it again, it might complain that it 'wants to add keys that already exist'. Somehow the speller is not closed fully the previous time, so cannot reopen. Kill everything and restart the control room. 
- If you just ran `ONLINE` and stopped the speller in any way, the decoder will still be running. Depending on your needs, stop the decoder by pressing `STOP` in dp-cvep-decoder.
- If you run the online phase and want to record the data, pressing `RUN ONLINE` might crash the decoder stream. A workaround is to not press `RUN ONLINE`, but instead record manually via the LSL Recorder app.

## References

- Dold, M., Pereira, J., Sajonz, B., Coenen, V. A., Thielen, J., Janssen, M. L., & Tangermann, M. (2025). Dareplane: a modular open-source software platform for BCI research with application in closed-loop deep brain stimulation. Journal of Neural Engineering, 22(2), 026029. doi: [10.1088/1741-2552/adbb20](https://doi.org/10.1088/1741-2552/adbb20)
- Thielen, J., Van Den Broek, P., Farquhar, J., & Desain, P. (2015). Broad-band visually evoked potentials: re(con)volution in brain-computer interfacing. PLOS One, 10(7), e0133797. doi: [10.1371/journal.pone.0133797](https://doi.org/10.1371/journal.pone.0133797)
- Thielen, J., Marsman, P., Farquhar, J., & Desain, P. (2021). From full calibration to zero training for a code-modulated visual evoked potentials for brain–computer interface. Journal of Neural Engineering, 18(5), 056007. doi: [0.1088/1741-2552/abecef](https://doi.org/0.1088/1741-2552/abecef)
