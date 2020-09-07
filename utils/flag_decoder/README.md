# Flag Decoder

## Introduction

algoseek's Equity Trade+Quote and Trade Only datasets provide `Conditions` column with a hex (base-16) value encoding conditions applicable for each event.
This command-line tool can be used to decode quote and/or trade condition flags to code names. 
Please refer to dataset guide for detailed description of conditions.

Python 2.7 or 3.x is required to run the script.

## Command-Line Arguments

| Short | Long          | Description                                                          |
| ----- | ------------- | -------------------------------------------------------------------- |
| -qf   |  --quote_flag | Decode a single quote flag                                           |
| -tf   |  --trade_flag | Decode a single trade flag                                           |
| -i    |  --in         | Decode condition codes from algoseek TAQ or Trade Only file          |
| -o    |  --out        | Write decoded lines from the input file to the specified output file | 
| -b    |  --start      | Start time (HH:MM:SS.SSS, HH:MM:SS, HH:MM or HH format)              |
| -e    |  --stop       | Stop time (HH:MM:SS.SSS, HH:MM:SS, HH:MM or HH format)               |

## Usage

### Decode a quote event code

Condition code 00000008
```
$ python3 flag_decoder.py -qf 00000008
qClosing
```

Condition code 00000401
```
$ python3 flag_decoder.py -qf 00000401
qRegular qNonFirmQuote
```

### Decode a trade event code

Condition code 80000401
```
$ python3 flag_decoder.py -tf 80000401 
tRegular tFormT tOddLot
```

Condition code a0000201
```
$ python3 flag_decoder.py -tf a0000201
tRegular tDerivativelyPriced tTradeThroughExempt tOddLot
```

Condition code 04000001
```
$ python3 flag_decoder.py -tf 04000001
tRegular tOfficialOpen
```

### Decode a file

Read the input from file `20200303_AA.csv.gz`
```
$ python3 flag_decoder.py -i 20200303_AA.csv.gz
```

Read the input from file `20200303_AA.csv.gz` and write to `decoded_20200303_AA.csv.gz`
```
$ python3 flag_decoder.py -i 20200303_AA.csv.gz -o decoded_20200303_AA.csv.gz
```

### Decode a file with time range

Read the input from file `20200303_AA.csv.gz` and decode events beween 9:30 and 09:45
```
$ python3 flag_decoder.py -i 20200303_AA.csv.gz --start 09:30 --stop 09:45
```

