import verification

def main():
    hourReceiptTable, hourVerificationTable, startdate, numDays = verification.generate_receipt_and_verification_tables(randomSeedPath="./verification/randomSeed.txt")
    subtables = verification.generate_daily_subtables(hourReceiptTable, hourVerificationTable, startdate, numDays)
    paths = verification.pickle_tables_and_subtables(hourReceiptTable, hourVerificationTable, subtables)

if __name__ == "__main__":
    main()
