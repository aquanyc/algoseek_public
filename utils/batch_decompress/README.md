# Batch Decompress Gzipped Files

## Introduction

Many algoseek's data files are stored in csv.gz format.
When downloading thousands individual files with several levels of nested folders,
you might find it difficult to extract all these files. 
This script allows to decompress all gzip-compressed files under the provided path and inside all its subfolders.
If the file name for the decompressed file already exists, it will be overwritten.

Python 3.6 or higher is required to run the script.

## Command-Line Arguments

Positional arguments:

path - a path to the directory with *.gz files (works with arbitrary level of nested folders)

Optional arguments:

| Short | Long           | Description                                                 |
| ----- | -------------- | ----------------------------------------------------------- |
| -k    |  --keep        | Keep (don't delete) input files during decompression        |
| -v    |  --verbose     | Display the name for each file decompressed                 |

## Usage

Decompress all csv.gz files in `algoseek_data` folder and all its subfolders:
```
python3 batch_decompress.py algoseek_data
```
After this operation all .gz files will be replaced by uncompressed .csv files.
If you want to retain compressed files use `-k` command-line option:
```
python3 batch_decompress.py -k algoseek_data
```
In this case you will have csv.gz alongside decompressed .csv files.
