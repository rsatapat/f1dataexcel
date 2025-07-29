# f1dataexcel
F1DataExcel is a Python command-line utility for downloading Formula 1 session data as an excel file using [FastF1](https://theoehrly.github.io/Fast-F1/). It supports structured workflows and integrates `argparse` to provide a user-friendly CLI.

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/yourusername/f1dataexcel.git
cd f1dataexcel
```
### 2. Create a Conda environment
```bash
conda env create -f environment.yml
```
### 3. (Optional) Install as a CLI command
If you want to use f1dataexcel as a global command in your environment:
```bash
pip install -e .
```
### Basic syntax
Without installation
```bash
python -m f1dataexcel 2024 -d path/to/folder
```
With installation
```bash
f1dataexcel 2024 -d path/to/folder
```

### Disabling FastF1 Cache (Optional)
```bash
f1dataexcel 2024 -d path/to/folder --no-cache
```
