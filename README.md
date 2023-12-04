# dicom2elk

A simple and fast package that extracts relevant tags from dicom files and uploads them in JSON format to elasticsearch.

# How to install on Ubuntu 22.04

## Pre-requisites

### Clone the repository on your machine

In a terminal:

```bash
cd "<your_prefered_folder"
git clone git@github.com:TranslationalML/dicom2elk.git dicom2elk
cd dicom2elk
```

### Install Python environment

You need Python 3.10 installed on your computer to use `dicom2elk`.

We recommend using a virtual or conda environment to isolate the dependencies of this package. 

**Option 1**: To create a virtual environment, you can use the following command:

```bash
python3 -m venv .venv
```

Note that you may have to install [`pip`](https://pip.pypa.io/en/stable/) and [`venv`](https://docs.python.org/3/library/venv.html) if you don't have them already installed on your system. This can be done as follows:

```bash
sudo apt-get install python3-pip
pip install virtualenv
```

Then, activate the created environment:

```bash
source venv/bin/activate
```

To deactivate it:

```bash
deactivate
```


**Option 2**: To create a conda environment, you will need miniconda or micromamba installed, the later the prefered (which appeared to be more efficient). To install micromamba, run the following command:

```bash
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
```

You might need to open a new Terminal to finalize the installation. Please consult the [official docs](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) for more details.

Then, install the environment:

```bash
micromamba env create -f conda/environment.yml
```

This will create a dedicated Python 3.10 environment named `dicom2elk` with all depedencies installed.

Then, do not forget to activate the environment with the following command:

```bash
micromamba activate dicom2elk
```

### Install `dicom2elk` package with `pip`

In a terminal in the folder of your clone and with your environment (`venv`/`conda`) activated, run the following `Make` command:

```bash
make install-python
```

This will run the command `pip install .[all]` for you.

            
## Usage

```output
dicom2elk -h
usage: dicom2elk: A simple and fast package that extracts relevant tags from dicom files and uploads them in JSON format to elasticsearch.
       [-h] -i INPUT_DCM_LIST [-c CONFIG] -o OUTPUT_DIR [--dry-run] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
       [-n N_THREADS] [-b BATCH_SIZE] [-p {multiprocessing,asyncio}] [-s SLEEP_TIME_MS] [--profile]
       [--profile-tsv PROFILE_TSV] [-v]

options:
  -h, --help            show this help message and exit
  -i INPUT_DCM_LIST, --input-dcm-list INPUT_DCM_LIST
                        Text file providing a list of dicom files to process
  -c CONFIG, --config CONFIG
                        Config file in JSON format which defines all variables related to Elasticsearch
                        instance (url, port, index, user, pwd)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Specify an output directory to save the log file.
                        If --dry-run is specified, all JSON files are also saved in this directory
  --dry-run             When specified, extracted tags for each dicom file of the list are saved in distinct JSON files in the output directory
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level
  -n N_THREADS, --n-threads N_THREADS
                        Number of threads to use for parallel processing
  -b BATCH_SIZE, --batch-size BATCH_SIZE
                        Batch size for extracting and saving/uploading metadata tags from dicom files
  -p {multiprocessing,asyncio}, --process-handler {multiprocessing,asyncio}
                        Process handler to use for parallel/asynchronous processing.
                        Can be either 'multiprocessing' or 'asyncio'
  -s SLEEP_TIME_MS, --sleep-time-ms SLEEP_TIME_MS
                        Sleep time in milliseconds to wait between each file processing.
                        This might be useful to avoid overloading the system.
  --profile             When specified, performance / memory profiling is performed and results are saved. If 
                        --profile-tsv is specified, results are saved in the specified TSV file. Otherwise
                        results are saved in a TSV file named after the input dicom list file with the suffix
                        '.profile.tsv' in the specified `output_dir` directory.
  --profile-tsv PROFILE_TSV
                        Specify a TSV file to save mem/perf profiling results.
  -v, --version         show program's version number and exit
```
