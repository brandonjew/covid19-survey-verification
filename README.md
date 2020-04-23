# Simple Survey Receipt Verification

Requires Python 3 and all scripts should be run from the main repository directory

## Generating Tables

Generate all the tables with:

`python3 generate_tables.py` 

This command will generate a directory `tables` in the main repository directory that contains the verification and receipt tables as pickled objects separated by day.
These will be loaded to get and verify receipts.
Note that this will generate the tables for the next 100 days and cannot be run if the `tables` directory already exists to avoid breaking existing receipts.


## Getting receipts

Get a receipt for right now with:

`python3 get_receipt.py`

This command will print out the receipt for the current hour

## Verifying receipts

Verify a receipt with:

`python3 get_verification.py {receipt}`

This will print the date and hour that the receipt is valid for or will print "Receipt not valid".
