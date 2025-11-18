# bicycledigest
Process data from bicycle logger

## Usage

1. Provide a correct `config.yaml`. It is expected to reside in the same directory as the main script (`bicycledigest.py`). 
2. Activate virtual environment (step 2 only) or set it up and install requirements if this is the first time.
    a. `python3 -m venv .venv`
    b. `source .venv/bin/activate`
    c. `pip install --upgrade pip`
    d. `pip install -r requirements.txt`
3. Run the main script (which just executes `main()`).
4. Collect your artifacts from `out` folder. 

## Example

[![asciicast](https://asciinema.org/a/WT8nvhKc50ESHMxl9NvqfeTOt.svg)](https://asciinema.org/a/WT8nvhKc50ESHMxl9NvqfeTOt)

## Config

Specify location of data files and detection parameters. Note that OCs are not processed beyond selection of corresponding button presses. The following is the section of the YAML file that needs to be customized. The rest can be left as is.

```yaml
sources:
  button_file: "data/button.csv"
  lidar_file: "data/lidar.csv"
  gps_file: "data/gps.csv"
```


