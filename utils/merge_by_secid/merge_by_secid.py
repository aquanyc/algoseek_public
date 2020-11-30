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
    

def MergeSecid(secid, files):
    Path(f"{args.merge_dir}/{secid[:2]}").mkdir(parents=True, exist_ok=True)
    
    with gzip.open(f"{args.merge_dir}/{secid[:2]}/{secid}.csv.gz", 'wt') as f_out:
        with gzip.open(files[0], 'rt') as f_in:
            header = f_in.readline()
            f_out.write(header)
        for file_ in files:
            with gzip.open(file_, 'rt') as f_in:
                f_in.readline()  # skip header
                f_out.write(f_in.read())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# command line arguments parser
parser = argparse.ArgumentParser(description='Merger for All SecIds Data')
parser.add_argument(
    'loc_dir', nargs='?', help='A local directory to sync with data buckets'
)
parser.add_argument(
    'merge_dir', nargs='?', help='A directory to store mergered data'
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
    '--threads', type=int, default=1,
    help='The number of parallel processes to apply merge. Default: 1'
)
parser.add_argument(
    '--profile', default='default',
    help='AWS profile name. Default: default (no profile)'
)

args = parser.parse_args()

# update full universe of data organized by year by SecId
for year in range(args.start_year, args.end_year + 1):
    command = [
        "aws", "s3", "sync", f"s3://us-equity-1min-trades-adjusted-secid-{year}", f"{args.loc_dir}/{year}", 
        "--profile", args.profile, "--request-payer", "requester"
    ]
    subprocess.run(command)

# get all data file with year organization
# and group data files by SecId
secid_groups = defaultdict(list)
for filename in sorted(Path(args.loc_dir).glob(f"*/*/*.csv.gz")):
    secid = str(filename).split('/')[-1].split('.')[0]
    secid_groups[secid].append(filename)

# merge data by SecId
with Pool(args.threads) as pool:
    pool.starmap(MergeSecid, secid_groups.items())






