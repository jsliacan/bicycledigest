# bicycledigest
Process data from bicycle logger

## Usage

1. Provide a correct `config.yaml`. It is expected to reside in the same directory as `bicycledigest.py`. 
2. Activate virtual environment (step 2 only) or set it up and install requirements if this is the first time.
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
    - `pip install --upgrade pip`
    - `pip install -r requirements.txt`
3. Run the `bicycledigest.py` script (which just executes `main()`).
    - Cmdline arguments with button, lidar, and gps filenames take precedence over entries in the `config.yaml`.
    ```bash
    python bicycledigest.py \
        -b "data/button.csv" \
        -g "data/gps.csv" \
        -l "data/lidar.csv" \
        -r "data/radar.csv"
    ```
    Note that only if all filenames are given as arguments will the commandline options be respected.
4. Collect your artifacts from `out` folder. 
5. Alternatively, run `uv run dashboard.py` and check `127.0.0.1:8050` in your browser for a few interactive plots.

## Example

[![asciicast](https://asciinema.org/a/WT8nvhKc50ESHMxl9NvqfeTOt.svg)](https://asciinema.org/a/WT8nvhKc50ESHMxl9NvqfeTOt)

## Config

Specify location of data files and detection parameters. Note that OCs are not processed beyond selection of corresponding button presses. The following is the section of the YAML file that needs to be customized. The rest can be left as is.

```yaml
sources:
  button_file: "data/button.csv"
  lidar_file: "data/lidar.csv"
  gps_file: "data/gps.csv"
  radar_file: "data/radar.csv"
```



