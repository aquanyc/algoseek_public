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

## Command-Line Arguments

Positional arguments:

loc_dir - A local directory to sync with data buckets

merge_dir - A directory to store merged data

Optional arguments:

| Name           | Description                                                 |
| -------------- | ----------------------------------------------------------- |
|  --start_year  | Start year for data. Default: 2007                          |
|  --end_year    | End year for data. Default: current year                    |
|  --threads     | The number of parallel processes to apply merge. Default: 1 |
|  --profile     | AWS profile name. Default: default (no profile)             |

## Usage

Get updates for full universe of symbols from 2010 to 2019 separated by year located in `algoseek_data` folder and merge all data to folder `algoseek_data_merged` using 8 processes and and aws profile `algoseek`:
```
python3 merge_by_secid.py algoseek_data algoseek_data_merged --start_year 2010 --end_year 2019 --threads 8 --profile algoseek
```

Fetch the history from 2015 to present using default AWS keys and 4 processes to merge the data:
```
python3 merge_by_secid.py algoseek_data algoseek_data_merged --start_year 2015 --threads 4
```

**Note:** if you are not using named AWS profiles and have just one pair of AWS keys configured you don't need to use the `profile` option.

### To-Do

1. Choice: merge or not merge
2. Update only a list of symbols 
