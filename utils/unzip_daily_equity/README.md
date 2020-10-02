# Unzip Daily Equity Data

## Introduction

algoseek's Equity Minute Bar datasets are packaged into daily zip files.
When extracting these files on a Windows machine, you might encounter two issues:

**Windows Device Filenames.** 

Windows reserves certain filenames for devices, for example, PRN for parallel port. 
Files with these names cannot be deleted or accessed, so a data file with the same stock symbol cannot be read. 
It applies to the following file names: AUX, CON, PRN, NUL.

**Preferred Stocks and When Issued.** 
The Windows operating system is not case-sensitive so it is unable to tell the difference for example,
between CpN (preferred Series N stock for C symbol) and a regular stock CPN. 
Please refer to algoseek Symbology Guide for a full list
of special stocks that use a lowercase letter in the symbol name.

This script allows extracting files from algoseek daily zip files taking into account these issues
by appending and undescore (`_`) to the end of the file name. It means that `AUX` is extracted as `AUX_` and when
both CpN and CPN exist in the archive then `CpN` is extracted as `CPN_`.

Python 3.6 or higher is required to run the script.

## Command-Line Arguments

Positional arguments:

zip_path - Path of the ZIP archive(s) to decompress or directory with zip files

Optional arguments:

| Short | Long           | Description                                                 |
| ----- | -------------- | ----------------------------------------------------------- |
| -d    |  --dest_path   | An optional directory to which to extract files             |
| -v    |  --verbose     | Print the name of archive being extracted                   |
| -n    |  --num_proc    | Specifies the number of jobs to run simultaneously          |

## Usage

Extract a single zip file to the current directory:
```
python3 unzip_daily_equity.py 20200305.zip
```

Extract multiple file to the folder `algoseek_data`:
```
python3 unzip_daily_equity.py -d algoseek_data 20200303.zip 20200304.zip 20200305.zip
```

Extract all file from `2020` folder into `algoseek_data` using 8 processes:
```
python3 unzip_daily_equity.py 2020/ -d algoseek_data -n 8
```



