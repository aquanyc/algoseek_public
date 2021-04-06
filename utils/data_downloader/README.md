# Data Downloader

## Introduction

This script allows to download a subset of data in algoseek buckets filtered by trading date and/or list of symbols.
It skips files for which you do not have the access. 

Note: data downloader only works for buckets with a tradedate-based structure (e.g. `bucket_name/yyyymmdd/`)

Python 3.6 or higher is required to run the script.

## Command-Line Arguments


Required arguments:

| Name           | Description                                                             |
| -------------- | ----------------------------------------------------------------------- |
|  --bucket_name | A name of the source S3 bucket to download data from                    |
|  --loc_dir     | A path to the local destination directory                               |
|  --start_date  | The start date of data in the bucket to be downloaded (yyyymmdd format) |
|  --end_date    | The end date of data in the bucket to be downloaded (yyyymmdd format)   |


Optional arguments:

| Name           | Description                                                 |
| -------------- | ----------------------------------------------------------- |
|  --symbols     | A space separated list of symbols (base symbols for futures) to download for each date. Default: all symbols            |
|  --threads     | The number of parallel processes for data download. Default: 1 |
|  --profile     | AWS profile name. Default: default (no profile)             |
|  --sync        | Enable synchronize mode (copy only new files from the bucket)  |
|  --verbose     | Enable extra verbosity            |


## Usage

Download the entire `us-futures-1min-trades-2020-zipday` bucket with 4 parallel processes:
```
python3 data_downloader.py --bucket_name us-futures-1min-trades-2020-zipday --loc_dir data --start_date 20200101 --end_date 20201231 --threads 4  --verbose

```

Download data for AAPL, AMD and IBM between 20210301 and 20210310 from `us-equity-trades-2021` bucket using 6 threads with the sync mode enabled:
```
python3 data_downloader.py --bucket_name us-equity-trades-2021 --loc_dir data --start_date 20210301 --end_date 20210310 --symbols IBM AMD AAPL --threads 6  --verbose --sync

```
