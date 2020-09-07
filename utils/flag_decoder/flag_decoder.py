#!/usr/bin/python

import sys
import csv
import gzip
import argparse

# create args parser
parser = argparse.ArgumentParser(description='Add condition flags as string.')
parser.add_argument('-qf', '--quote_flag', action='store', dest='quote_flag', help='Decode manual quote code')
parser.add_argument('-tf', '--trade_flag', action='store', dest='trade_flag', help='Decode manual trade code')
parser.add_argument('-i', '--in', action='store', dest='input_file', help='Input file')
parser.add_argument('-o', '--out', action='store', dest='output_file', default=None, help='Output file. Default is stdout')
parser.add_argument('-b', '--start', action='store', dest='start_time', help='Start time HH:MM:SS.SSS or HH:MM:SS or HH:MM or HH (including)')
parser.add_argument('-e', '--stop', action='store', dest='stop_time', help='Stop time HH:MM:SS.SSS or HH:MM:SS or HH:MM or HH (including)')
args = parser.parse_args()

# default values
start = None
stop = None
input_file = None
output_file = None
gzin = False
gzout = False
cTimestamp = None
cConditions = None
cEventType = None

# get parameters from argparser
input_file = args.input_file
output_file = args.output_file
start = args.start_time
stop = args.stop_time
quote_flag = args.quote_flag
trade_flag = args.trade_flag

# trade flag values
tradeFlags = ['tRegular', 'tCash', 'tNextDay', 'tSeller', 'tYellowFlag', 'tIntermarketSweep',
              'tOpeningPrints', 'tClosingPrints', 'tReOpeningPrints', 'tDerivativelyPriced',
              'tFormT', 'tSold', 'tStopped', 'tExtendedHours', 'tOutOfSequence', 'tSplit',
              'tAcquisition', 'tBunched', 'tStockOption', 'tDistribution', 'tAveragePrice',
              'tCross', 'tPriceVariation', 'tRule155', 'tOfficialClose', 'tPriorReferencePrice',
              'tOfficialOpen', 'tCapElection', 'tAutoExecution', 'tTradeThroughExempt', '?', 'tOddLot']

# quote flag values
quoteFlags = ['qRegular', 'qSlow', 'qGap', 'qClosing', 'qNewsDissemination', 'qNewsPending',
              'qTradingRangeIndication', 'qOrderImbalance', 'qClosedMarketMaker',
              'qVolatilityTradingPause', 'qNonFirmQuote', 'qOpeningQuote',
              'qDueToRelatedSecurity', 'qResume', 'qInViewOfCommon', 'qEquipmentChangeover',
              'qSubPennyTrading', 'qNoOpenNoResume', 'qLimitUpLimitDownPriceBand',
              'qRepublishedLimitUpLimitDownPriceBand', 'qManual', 'qFastTrading', 'qOrderInflux']

# convert indeger flag into string
def convertIntFlag(val, flags):
    res = []
    for i in range(len(flags)):
        if val & (1 << i) > 0:
            res.append(flags[i])
    return ' '.join(res)

# convert hex flag into string
def convertHexFlag(val, flags):
    return convertIntFlag(int(val, 16), flags)

if quote_flag is not None:
    print(convertHexFlag(quote_flag, quoteFlags))
    sys.exit(0)
if trade_flag is not None:
    print(convertHexFlag(trade_flag, tradeFlags))
    sys.exit(0)

# check for missing parameters
if input_file is None:
    if len(sys.argv) > 1:
        print('Input file is missing')
    parser.print_help(None)
    sys.exit(1)

# process one record. check time and add decoded flag
def process_record(record):
    new_record = record[:]
    # check timestamp
    if (start is not None):
        time = record[cTimestamp][:len(start)]
        if (time < start):
            return None
    if (stop is not None):
        time = record[cTimestamp][:len(stop)]
        if (time > stop):
            return None

    # choose flag values: QUOTE or TRADE
    flags = quoteFlags
    if record[cEventType].startswith('TRADE'):
        flags = tradeFlags

    # convert flag
    flagsStr = convertHexFlag(record[cConditions], flags)

    new_record.append(flagsStr)
    return new_record

# check input and output file compression
if input_file.lower().endswith('.gz') or input_file.lower().endswith('.gzip'):
    gzin = True
if output_file and (output_file.lower().endswith('.gz') or output_file.lower().endswith('.gzip')):
    gzout = True

# open input file
if gzin:
    in_file = gzip.open(input_file, 'rt')
else:
    in_file = open(input_file, 'r')
reader = csv.reader(in_file, skipinitialspace=True, delimiter=',', quotechar='"')

# read input file header
header = next(reader)

# find column indexes
cTimestamp = header.index('Timestamp')
cEventType = header.index('EventType')
cConditions = header.index('Conditions')

# open output file
if output_file:
    if gzout:
        out_file = gzip.open(output_file, 'wt')
    else:
        out_file = open(output_file, 'w')
else:
    out_file = sys.stdout
writer = csv.writer(out_file, delimiter=',')

# write header into output file
new_header = header[:]
new_header.append('CondDecoded')
writer.writerow(new_header)

# process all records
for record in reader:
    if not record:
        continue
    new_record = process_record(record)
    if new_record is not None:
        writer.writerow(new_record)

# close files
in_file.close()
out_file.close()
