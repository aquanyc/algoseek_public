import sys
import gzip
import argparse
import subprocess

from pathlib import Path
from datetime import datetime
from multiprocessing import Pool
from collections import defaultdict


# check python version
if sys.version_info < (3, 5):
    sys.stderr.write("You need python 3.5 or later to run this script\n")
    exit(1)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def setup_parser():
    # command line arguments parser
    parser = argparse.ArgumentParser(description='Merger for All SecIds Data')
    parser.add_argument(
        'bucket_name', help='Name of bucket to sync'
    )
    parser.add_argument(
        'loc_dir', type=Path, help='A local directory to sync with data buckets'
    )
    parser.add_argument(
        '--merge_dir', default=None, type=Path, help='A directory to store mergered data'
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
        '--secids', nargs='*',
        help='A list of secids to be merged'
    )
    parser.add_argument(
        '--secids_file', default=None, type=Path,
        help='A file with seсids to be merged'
    )
    parser.add_argument(
        '--threads', type=int, default=1,
        help='The number of parallel processes to apply merge. Default: 1'
    )
    parser.add_argument(
        '--profile', default='default',
        help='AWS profile name. Default: default (no profile)'
    )
    return parser


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

# update full universe of data organized by year by SecId
for year in range(args.start_year, args.end_year + 1):
    secids = None
    if args.secids_file:
        with open(args.secids_file) as f_secid:
            secids = f_secid.read().splitlines()
    if args.secids:
        secids = args.secids
    command = [
        "aws", "s3", "sync", f"s3://{args.bucket_name}".replace('yyyy', str(year)), 
        f"{args.loc_dir}/{year}", "--profile", args.profile, "--request-payer", "requester"
    ]
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
