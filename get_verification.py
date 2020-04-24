import verification
import sys

def main(hourReceipt):
    vstatus = verification.verify_receipt(hourReceipt)
    if (vstatus == None):
        print("Receipt not valid")
    else:
        print(vstatus.strftime("%Y-%m-%dT%H:%M:%SZ"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Receipt must be first positional argument only")
    hourReceipt = sys.argv[1]
    main(hourReceipt)
