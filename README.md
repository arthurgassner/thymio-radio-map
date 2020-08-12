# Automatic radio map construction for CSI-based fingerprinting with LTE

Fingerprint-based indoor localization methods require the construction of a radio map. This is a tool automating this tedious task, by having a robot follow a line, and stop every x cm to gather location-dependent characteristics (i.e. a fingerprint).

## Summary

Fingerprint-based indoor localization methods require the construction of a radio map. This is a tedious task which can be automated. The presented solution consists of a Software-Defined Radio (SDR) mounted on a wheeled-robot (Thymio II). The SDR is connected to a LTE tower using a modified version of the srsLTE software. The robot follows a line, stopping every x cm to let the SDR gather characteristics (**Channel State Information** (CSI), **Received Signal Strength Indicator** (RSSI), **Reference Signal Receive Power** (RSRP), ...) from its communication with the LTE tower. Those characteristics are saved, along with the robot's location (estimated through dead-reckoning), and are ready to be used as fingerprints.

![](doc/img/thymio_running.gif)

---

## Requirements

- Thymio II
- USRP B200mini
- PC/SC reader with a SIM card

---

## How to install

1. **Install a fork of `srsLTE`** following [this](https://github.com/arthurgassner/srsLTE)
    > This fork saves the channel characteristics (CSI, RSSI, RSRP, ...) to a file

    > Make sure `SRSUE_FOLDERPATH` in `run.py` points to the correct location (of the `srsue` folder, from the `srsLTE` installation)

2. **Install the Thymio Suite** and **prepare the connection with the Thymio II** following [this](https://www.thymio.org/help/linux-installation/)

3. **Install Aseba** following [this](http://wiki.thymio.org/en:linuxinstall)

    > - Run `asebamedulla --version` to ensure it is correctly installed

4. **Ensure that you're able to connect** to the Thymio II by launching `asebastudio` through some terminal. You'll be prompted to select a target: select the one called `Thymio-II`. This should establish the connection.

    > If clicking on the `Thymio-II` target simply re-shows the same popup, this is a known bug. To fix it, add yourself to the dialout group (`sudo adduser <USERNAME> dialout`), replacing `<USERNAME>` by your Ubuntu username. Log out then log in for the change to take effect.

    > Make sure the Thymio II is connected to the computer by USB

5. **Create conda environment** (called `thymio`) and activate it:

    ```bash
    conda env create -f environment.yml -n thymio
    conda activate thymio
    ```

6. **Install `dbus`**, **`gobject`** and **sox**:

    `pip install dbus-python`

    > To install `dbus-python`, you might need to first run `sudo apt install git virtualenv build-essential python3-dev libdbus-glib-1-dev libgirepository1.0-dev libcairo2-dev`

    `pip install PyGObject`

    `sudo apt install sox`

---


## How to run

### Non-continuous (Reconnect to the eNodeB at every RP)

1. **Connect by USB** the **Thymio II**, the **Software-Defined Radio** and the **PC/SC reader** (with a SIM card plugged in) to the computer

2. Open a terminal and **establish the connection to the Thymio II** by running:

    ```bash
    asebamedulla "ser:name=Thymio-II"
    ```

    > This opens a connection to the Thymio II. The terminal should read `Found Thymio-II on port /dev/ttyACM0` and keep running.

3. Open another terminal and launch the run script by running:

    ```bash
    conda activate thymio
    python run.py
    ```

### Continuous (Connect once)

1. **Connect by USB** the **Thymio II**, the **Software-Defined Radio** and the **PC/SC reader** (with a SIM card plugged in) to the computer

2. Open a terminal and **establish the connection to the Thymio II** by running:

    ```bash
    asebamedulla "ser:name=Thymio-II"
    ```

    > This opens a connection to the Thymio II. The terminal should read `Found Thymio-II on port /dev/ttyACM0` and keep running.

3. Open another terminal and **launch srsUE** from this repo's root directory

    ```bash
    sudo srsue <PATH_TO_SRSLTE-MODIFIED>/srsue/ue.conf
    ```

    > Replace `<PATH_TO_SRSLTE-MODIFIED>` by the path to the `srsLTE-modified` software, and `ue.conf` by the configuration file you want to run 

4. **Wait for the SDR to connect** (the terminal will somewhere output `Network attach: 10.xx.xx.xx`)

    > The fingerprint files (i.e. `ce.txt`, `else.txt` and `info.txt`) should appear in this repo's root directory. Watch out, because `ce.txt` will grow quickly in size.

5. Open another terminal and **ping the above IP address** by running 

    ```bash
    ping 10.xx.xx.xx
    ```

    > This maintains the connection between the SDR and the eNodeB. Otherwise, no traffic is sent and the connection eventually times out.

6. Open another terminal and **launch the run script** by running:

    ```bash
    conda activate thymio
    python run_continuous.py
    ```

---

## Test files

To ensure that the Thymio and SDR are working, several files are available:

- `test_thymio.py`
- `test_fingerprint.py`

### `test_thymio.py`

To ensure that the Thymio II is able to work as intended:

1. **Plug in the Thymio II** through USB and place the Thymio II on the line to follow

2. Open a terminal and **establish the connection to the Thymio II** by running:

    ```bash
    asebamedulla "ser:name=Thymio-II"
    ```

3. Open another terminal and **launch the test script** by running:

    ```bash
    conda activate thymio
    python test_thymio.py
    ```

    > This should instruct the Thymio to follow the black-line for x cm, then wait, then repeat y times

![](doc/img/thymio_running.gif)

### `test_fingerprint.py`

To ensure that the Software Defined Radio works as intended:

1. **Connect via USB** the **Software-Defined Radio** (SDR) and the **PC/SC reader** (with a SIM card plugged in) to the computer

    > For the SDR, you **have** to used USB 3.0, else the datarate is too high for the connection.

2. Open a terminal and **launch the test script** by running:

    ```bash
    conda activate thymio
    python test_fingerprint.py
    ```

    > This should instruct the SDR to connect to the eNodeB, gather a fingerprint and save it in a folder called `test_fingerprint`

---

## How to handle the generated files

Some python scripts were written to facilitate the data gathering step, i.e.:

-   `move_fingerprint.py`: 
    - Move the files generated by `sudo srsue ue.conf` (i.e. `ce.txt`, `else.txt` and `info.txt`) into their own folders (`ce`, `else`, `info`) 
    - Record the (x,y) coordinates where those files were gathered into a JSON file (i.e. `locations.json`)

-   `clean_fingerprints.py` 
    - Clean the fingerprint files (i.e. `ce_0_raw.txt`, `else_0_raw.txt` and `info_0_raw.txt`) 
    - Save the cleaned files, e.g.:
        * `ce_0_raw.txt` -> `ce_0.parquet`
        * `else_0_raw.txt` -> `else_0.pkl` 
        * `info_0_raw.txt` -> `info_0.pkl`

-   `plot_fingerprints.py` 
    - Plot the amplitude and phase held in the cleaned `ce.txt` (e.g. `ce_0.parquet`) 
    - Save the plot, e.g.: 
        - `ce_0.parquet` -> `ce_0.png`

---

## Misc

Tested with

-   Ubuntu 18.04
-   Aseba medulla 1.6.1