# Copyright 2021 AlgoSeek, LLC. All Rights Reserved

import pathlib
import argparse
import datetime
import multiprocessing

import boto3


def setup_parser():
    # command line arguments parser
    parser = argparse.ArgumentParser(description='Download files from AWS bucket to a local directory')
    parser.add_argument(
        '--bucket_name', 
        required=True,
        help='A name of the source S3 bucket to download from'
    )
    parser.add_argument(
        '--loc_dir', 
        required=True, type=pathlib.Path,
        help='A local destination directory path'
    )
    parser.add_argument(
        '--start_date',
        required=True,
        help='The start date of data in the bucket to be downloaded (yyyymmdd format)'
    )
    parser.add_argument(
        '--end_date',
        required=True,
        help='The end date of data in the bucket to be downloaded (yyyymmdd format'
    )
    parser.add_argument(
        "--symbols",
        nargs="*", default=[],
        help="A space separated list of symbols (base symbols for futures) to download for each date. Default: all symbols"
    )
    parser.add_argument(
        '--threads', type=int, default=1,
        help='The number of parallel processes for data download. Default: 1'
    )
    parser.add_argument(
        '--profile', default='default',
        help='AWS profile name. Default: default (no profile)'
    )
    parser.add_argument(
        '--sync',  action='store_true',
        help='Synchronize mode: do not download files from the bucket that already exist locally'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Enable extra verbosity'
    )
    return parser


def symbol_pattern(bucket_name, symbol):
    if 'equity' in bucket_name:
        return f'{symbol[0]}/{symbol}.csv.gz'
    elif 'futures' in bucket_name:
        return f'/{symbol}/'
    elif 'options' in bucket_name:
        return f'{symbol[0]}/{symbol}/'


def list_dates(start_date_str, end_date_str):
    start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')
    while start_date <= end_date:
        yield start_date.strftime("%Y%m%d")
        start_date = start_date + datetime.timedelta(days=1)


def list_objects(bucket_name, dates, symbols):
    object_names = []
    if symbols:
        for date in dates:
            for symbol in symbols:
                prefix = f'{date}/{symbol_pattern(bucket_name, symbol)}'
                object_names.extend([
                    obj.key 
                    for obj in s3.Bucket(bucket_name).objects.filter(
                        Prefix=prefix, RequestPayer='requester'
                    )
                ])
    else:
        for date in dates:
            object_names.extend([
                obj.key 
                for obj in s3.Bucket(bucket_name).objects.filter(
                    Prefix=date, RequestPayer='requester'
                )
            ])
    return object_names


def copy_object(bucket_name, object_key, local_folder, sync=False, verbose=False):
    object_local_path = local_folder / object_key
    if sync and object_local_path.exists():
        return
    object_local_path.parent.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"downloading s3://{bucket_name}/{object_key} ..")
    try:
    	s3.Bucket(bucket_name).download_file(
    	    object_key,
    	    str(object_local_path),
    	    ExtraArgs={'RequestPayer': 'requester'}
    	)
    except s3.meta.client.exceptions.ClientError as e:
    	print(e)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


parser = setup_parser()
args = parser.parse_args()

session = boto3.session.Session(profile_name=args.profile)
s3 = session.resource('s3')

dates = list_dates(args.start_date, args.end_date)

objects = list_objects(args.bucket_name, dates, set(args.symbols))

payload = [
    (args.bucket_name, object_name, args.loc_dir, args.sync, args.verbose)
    for object_name in objects
]

with multiprocessing.Pool(args.threads) as pool:
    pool.starmap(copy_object, payload)


