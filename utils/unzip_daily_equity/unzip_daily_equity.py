# Copyright 2018 AlgoSeek, LLC. All Rights Reserved

import sys
# require python >=3.6
if sys.version_info < (3, 6):
    sys.exit("ERROR: Python 3.6 or later is required")

import pathlib
import zipfile
import argparse
import multiprocessing


def windows_extract_zipday(zip_file_name, target_path=None, verbose=False):
    if verbose:
        print(f'Extracting {zip_file_name} to {target_path}')
    with zipfile.ZipFile(zip_file_name) as zpf:
        names_lookup = set(zpf.namelist())
        for obj in zpf.infolist():
            if '.' in obj.filename:
                basename, ext = obj.filename.rsplit('.', 1)
                basename_upper = basename.upper() + '.' + ext
                if basename_upper in names_lookup and basename_upper != obj.filename:
                    obj.filename = basename + '_.' + ext
            try:
                zpf.extract(obj, path=target_path)
            except FileNotFoundError:
                obj.filename = basename + '_.' + ext
                zpf.extract(obj, path=target_path)
            except Exception as e:
                print(f'Failed to extract {obj.filename}: {e}')


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'zip_path',
        nargs='+',
        type=pathlib.Path,
        help='Path of the ZIP archive(s) to decompress or directory with zip files'
    )
    parser.add_argument(
        '-d', '--dest_path',
        default=pathlib.Path.cwd(),
        type=pathlib.Path,
        help='An optional directory to which to extract files'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print the name of archive being extracted'
    )
    parser.add_argument(
        '-n', '--num_proc',
        type=int,
        default=2,
        help='Specifies the number of jobs to run simultaneously'
    )
    return parser


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

parser = setup_parser()
args = parser.parse_args()

if not args.dest_path.is_dir():
    sys.exit(f"ERROR: Destination path {args.dest_path} does not exist")

target_args = []
for path in args.zip_path:
    if path.is_file():
        target_args.append((path, str(args.dest_path), args.verbose))
    elif path.is_dir():
        dest_path = args.dest_path / path
        dest_path.mkdir(exist_ok=True)
        for fname in path.glob('*.zip'):
            target_args.append((fname, str(dest_path), args.verbose))
    else:
        print(f"ERROR: Skipping {path} - not a file or directory")

with multiprocessing.Pool(args.num_proc) as pool:
    pool.starmap(windows_extract_zipday, target_args)

