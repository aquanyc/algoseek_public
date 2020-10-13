# Copyright 2018 AlgoSeek, LLC. All Rights Reserved

import sys
# require python >=3.6
if sys.version_info < (3, 6):
    sys.exit("ERROR: Python 3.6 or later is required")

import gzip
import pathlib
import argparse


def extract_gzipped(gzip_path, keep_compressed, verbose):
    dst_path = gzip_path.with_suffix('')
    if verbose: 
        print(f'Extracting {gzip_path.name} ..')
    with gzip.open(gzip_path, 'rb') as f_in:
        with open(dst_path, 'wb') as f_out:
            f_out.write(f_in.read())
    if not keep_compressed:
        gzip_path.unlink()

    
def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        type=pathlib.Path,
        help='Path to a directory with .gz files to be decompressed'
    )
    parser.add_argument(
        '-k', '--keep',
        action='store_true',
        help="Keep (don't delete) input files during decompression"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Verbose. Display the name for each file decompressed"
    )
    return parser


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

parser = setup_parser()
args = parser.parse_args()

for fname in sorted(args.path.glob('**/*.gz')):
    extract_gzipped(fname, args.keep, args.verbose)

