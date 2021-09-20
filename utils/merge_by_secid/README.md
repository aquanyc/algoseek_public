# Update Equity Trade Adjusted Minute Bars

## Introduction

algoseek's Equity Trade Adjusted Minute Bars dataset is organized by SecID - a unique identifier
for each equity security that remains unchanged even during a name or ticker changes.
The data is partitioned into buckets by year, so each bucket has one csv.gz file per SecID.

The dataset uses backward adjustment approach.
It means that any new corporate events trigger the entire stock history change.
Also the entire dataset is updated on daily basis with bars for the previous trading session.
As the result, you will need to update ~8000 symbols due to daily updates and ~300 symbols affected by corporate events.

When working with the full universe of symbols, getting all these changes requires fetching Gigabytes of data daily.
Having data partitioned by year reduces the amount to be downloaded but
on the other hand, it is convenient to have one file per SecID when working with data.
This script allows getting updates for the data partitioned by year and merging it into a dataset with a single file per SecID.

Currently, can be used for buckets: us-equity-1min-trades-adjusted-secid-yyyy, us-equity-cumulative-backward-adjustment-secid-yyyy.

## Command-Line Arguments

Positional arguments:

bucket_name - Name of bucket to sync in format: bucket-name-yyyy

loc_dir - A local directory to sync with data buckets

Optional arguments:

| Name           | Description                                                 |
| -------------- | ----------------------------------------------------------- |
|  --merge_dir   | A directory to store merged data. Default: None             |
|  --start_year  | Start year for data. Default: 2007                          |
|  --end_year    | End year for data. Default: current year                    |
|  --secids      | A list of secids to be merged                               |
|  --secids_file | A file with seсids to be merged                             |
|  --threads     | The number of parallel processes to apply merge. Default: 1 |
|  --profile     | AWS profile name. Default: default (no profile)             |

## Usage

Get updates for full universe of symbols for Equity Trade Adjusted Minute Bars dataset from 2010 to 2019 separated by year located in `algoseek_data` folder and merge all data to folder `algoseek_data_merged` using 8 processes and aws profile `algoseek`:
```
python3 merge_by_secid.py us-equity-1min-trades-adjusted-secid-yyyy algoseek_data --merge_dir algoseek_data_merged --start_year 2010 --end_year 2019 --threads 8 --profile algoseek
```

Get updates for 33449 and 38497 SecIds for Equity Trade Adjusted Minute Bars dataset from 2010 to 2019 separated by year located in `algoseek_data` folder and merge all data to folder `algoseek_data_merged` using 2 processes and aws profile `algoseek`:
```
python3 merge_by_secid.py us-equity-1min-trades-adjusted-secid-yyyy algoseek_data --merge_dir algoseek_data_merged --start_year 2010 --end_year 2019 --secids 33449 38497 --threads 8 --profile algoseek
```

Get updates for a list of SecIds from `secids.csv` file for Equity Trade Adjusted Minute Bars dataset from 2010 to 2019 separated by year located in `algoseek_data` folder and merge all data to folder `algoseek_data_merged` using 8 processes and aws profile `algoseek`:
```
python3 merge_by_secid.py us-equity-1min-trades-adjusted-secid-yyyy algoseek_data --merge_dir algoseek_data_merged --start_year 2010 --end_year 2019 --secids_file secids.csv --threads 8 --profile algoseek
```

Fetch the history from 2015 to present using default AWS keys without merging the data:
```
python3 merge_by_secid.py us-equity-cumulative-backward-adjustment-secid-yyyy algoseek_data --start_year 2015
```

**Note:** if you are not using named AWS profiles and have just one pair of AWS keys configured you don't need to use the `profile` option.

**Note:** if you are working with a list of secids you have to use just one optional argument --secids or --secids_file.

**Note:** if you are using the file with secids, it should be one column with secids without header.
