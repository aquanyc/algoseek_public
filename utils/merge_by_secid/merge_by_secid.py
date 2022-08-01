import sys
import csv
import gzip
import argparse
import subprocess

from pathlib import Path
from multiprocessing import Pool
from urllib.request import urlopen
from collections import defaultdict
from datetime import datetime, timedelta

# check python version
if sys.version_info < (3, 5):
    sys.stderr.write("You need python 3.5 or later to run this script\n")
    exit(1)


def tradedate_range(start_d, end_d, holidays):
    '''Range of trade dates from start date to end date including'''
    dt_start_d = datetime.strptime(start_d, "%Y%m%d")
    dt_end_d = datetime.strptime(end_d, "%Y%m%d")
    
    dt_tradedates = (dt_start_d + timedelta(n) for n in range((dt_end_d - dt_start_d).days + 1) if (dt_start_d + timedelta(n)).weekday() not in (5, 6))

    return (tradedate.strftime("%Y%m%d") for tradedate in dt_tradedates if tradedate.strftime("%Y%m%d") not in holidays)

def market_holidays():
    '''Market holidays'''
    with urlopen('https://us-equity-market-holidays.s3.amazonaws.com/holidays.csv') as resp:
        content = resp.read().decode('utf-8')
    
    return content.split()[1:]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup_parser():
    '''Command line arguments parser'''
    parser = argparse.ArgumentParser(description='Merger for All SecIds Data')
    parser.add_argument(
        'bucket_name', help='Name of bucket to sync'
    )
    parser.add_argument(
        'loc_dir', type=Path, help='A local directory to sync with data buckets'
    )
    parser.add_argument(
        '--tradedate_agg', default=False, action='store_true', help='If data aggregated by tradedate'
    )
    parser.add_argument(
        '--merge_dir', default=None, type=Path, help='A directory to store mergered data'
    )
    parser.add_argument(
        '--start_date', type=str, default='20070101',
        help='Start date for data. Default: 20070101'
    )
    parser.add_argument(
        '--end_date', type=str, default=(datetime.today() - timedelta(1)).strftime("%Y%m%d"),
        help='End date for data. Default: yesterday'
    )
    parser.add_argument(
        '--start_year', type=int, default=2007,
        help='Start year for data. Default: 2007'
    )
    parser.add_argument(
        '--end_year', type=int, default=datetime.today().year,
        help='End year for data. Default: current year'
    )
    parser.add_argument(
        '--tickers', nargs='*',
        help='A list of tickers to download'
    )
    parser.add_argument(
        '--tickers_file', default=None, type=Path,
        help='A file with tickers to download'
    )
    parser.add_argument(
        '--secids', nargs='*',
        help='A list of secids to be merged'
    )
    parser.add_argument(
        '--secids_file', default=None, type=Path,
        help='A file with seсids to be merged'
    )
    parser.add_argument(
        '--threads', type=int, default=1,
        help='The number of parallel processes to download tradedate-organized data or to apply merge. Default: 1'
    )
    parser.add_argument(
        '--profile', default='default',
        help='AWS profile name. Default: default (no profile)'
    )
    return parser


def tradedate_task(tradedate):
    for ticker in tickers:
        command = ["aws", "s3", "cp", f"s3://{args.bucket_name}/{tradedate}/{ticker[0]}/{ticker}.csv.gz".replace('yyyy', str(tradedate[:4])), 
            f"{args.loc_dir}/{tradedate[:4]}/{tradedate}/{ticker[0]}/{ticker}.csv.gz", "--profile", args.profile, "--request-payer", "requester"]
        
        subprocess.run(command)

def merge_by_secid(secid, files):
    parent_dir = args.merge_dir / secid[:2]
    parent_dir.mkdir(parents=True, exist_ok=True)

    ext = files[0].name.split('.', 1)[1]
    
    open_func = gzip.open if ext.endswith('.gz') else open
    
    with open_func(parent_dir / f"{secid}.{ext}", 'wt') as f_out:
        with open_func(files[0], 'rt') as f_in:
            header = f_in.readline()
            f_out.write(header)
        
        for file_ in files:
            with open_func(file_, 'rt') as f_in:
                f_in.readline()  # skip header
                f_out.write(f_in.read())

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


parser = setup_parser()
args = parser.parse_args()

# update data organized by year by ticker
if args.tradedate_agg:
    holidays = market_holidays()    
    tradedates = tradedate_range(args.start_date, args.end_date, holidays)

    tickers = None
    if args.tickers_file:
        with open(args.tickers_file) as f_ticker:
            tickers = f_ticker.read().splitlines()
    elif args.tickers:
        tickers = args.tickers

    if tickers:
        with Pool(args.threads) as pool:
            pool.map(tradedate_task, tradedates)
    else:
        for year in range(args.start_year, args.end_year + 1):
            command = ["aws", "s3", "sync", f"s3://{args.bucket_name}".replace('yyyy', str(year)), 
                f"{args.loc_dir}/{year}", "--profile", args.profile, "--request-payer", "requester"]
            
            subprocess.run(command)
    
    sys.exit()

# update full universe of data organized by year by SecId
for year in range(args.start_year, args.end_year + 1):
    command = ["aws", "s3", "sync", f"s3://{args.bucket_name}".replace('yyyy', str(year)), 
        f"{args.loc_dir}/{year}", "--profile", args.profile, "--request-payer", "requester"]
    
    secids = None
    if args.secids_file:
        with open(args.secids_file) as f_secid:
            secids = f_secid.read().splitlines()
    if args.secids:
        secids = args.secids
    
    if secids:
        command.extend(["--exclude", "*"])
        for secid in secids:
            command.extend(["--include", f"{secid[0:2]}/{secid}.*"])
    
    subprocess.run(command)

# for merging data by SecId
if args.merge_dir:
    # get all data file with year organization
    # and group data files by SecId
    secid_groups = defaultdict(list)
    target_files = args.loc_dir.glob(f"*/*/*")
    
    for file_path in sorted(target_files):
        secid = file_path.name.split('.')[0]
        if secids:
            if secid in secids:
                secid_groups[secid].append(file_path)
        else:
            if 'daily-changes' not in file_path.parts:
                secid_groups[secid].append(file_path)
    
    # merge data by SecId
    with Pool(args.threads) as pool:
        pool.starmap(merge_by_secid, secid_groups.items())

