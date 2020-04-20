# Covid19 Symptom Survey Crypto
# Python3

import sys
import argparse
import hashlib, base64
import secrets
from datetime import datetime, date, timedelta
from enum import Enum


SALT_SIZE = 10001     # Number of potential salt values
BYTE_LEN_RAND = 16  # Size of randomness for random prefix to SHA256 input in generating receipt
RECEIPT_LEN = 16        # Size of receipt

# Receipt types
class ReceiptType(Enum):
    HOUR = 0
    ZIPCODE = 1

# VerificationTable
# Keeps track of (value, code) mappings
# - values are instances of the appropriate receipt type (e.g. the datetime object of the corresponding hour)
# - codes are hashes of the receipts for the corresponding value
class VerificationTable:
    _receiptType = 0
    _valueToCodeDict = {}
    _codeToValueDict = {}
    def __init__(self, receiptType):
        self._receiptType = receiptType
    def getType():
       return self._receiptType
    def addCodeValuePair(self, code, value):
       self._valueToCodeDict[value] = code
       self._codeToValueDict[code] = value
    def removeCodeValuePair(self, code, value):
       if (value in self._valueToCodeDict.keys()):
          del self._valueToValueDict[value]
       if (code in self._codeToCodeDict.keys()):
          del self._codeToValueDict[code]
    def getCode(self, value):
        if (value in self._valueToCodeDict.keys()):
            return self._valueToCodeDict[value]
        return None
    def getValue(self, code):
        if (code in self._codeToValueDict.keys()):
            return self._codeToValueDict[code]
        return None

    # Returns an unsorted list of (value, code) pairs
    def getCodeValueList(self):
        lst = []
        for value in self._valueToCodeDict.keys():
            lst.append((value, self._valueToCodeDict[value]))
        return lst

    # If values can be compared, will return a list of (value, code) pairs, sorted by value
    # Undefined behavior if values are incomparable
    def getSortedCodeValueList(self):
        lst = []
        for value in sorted(self._valueToCodeDict.keys()):
            lst.append((value, self._valueToCodeDict[value]))
        return lst

    # If values can be compared, will return a list of (value, code) pairs with values between valueStart and valueEnd, sorted by value
    # Undefined behavior if values are incomparable
    def getSortedCodeValueList(self, valueStart, valueEnd):
        lst = []
        for value in sorted(self._valueToCodeDict.keys()):
            if (valueStart <= value and value <= valueEnd):
                lst.append((value, self._valueToCodeDict[value]))
        return lst

    # If values can be compared, will return a VerificationTable that contains only the (value, code) pairs with values between valueStart and valueEnd
    # Undefined behavior if values are incomparable
    def getSubTable(self, valueStart, valueEnd):
        table = VerificationTable(self._receiptType)
        for value in sorted(self._valueToCodeDict.keys()):
            if (valueStart <= value and value <= valueEnd):
                table.addCodeValuePair((value, self._valueToCodeDict[value]))
        return table


def randSaltGenerator():
    secretsGenerator = secrets.SystemRandom()
    randSalt = secretsGenerator.randint(0, SALT_SIZE)
    return randSalt


def randBytesGenerator(k):
    return secrets.token_bytes(k)


def generateReceipt(receiptType, value):
    r = randBytesGenerator(BYTE_LEN_RAND)
    sha = hashlib.sha256()
    if (receiptType == ReceiptType.HOUR):
        sha.update(b'0')
        sha.update(r)
        sha.update(bytes(str.encode(value.strftime("%H"))))
        sha.update(bytes(str.encode(value.strftime("%d/%m/%Y"))))
    elif (receiptType == ReceiptType.ZIPCODE):
        sha.update(b'1')
        sha.update(r)
        sha.update(bytes(str.encode(value)))
    code = sha.hexdigest()
    return code[:RECEIPT_LEN]


def allHours(numHoursInFuture, startdate = datetime.now()):
    hour = timedelta(hours = 1)
    return [startdate + (hour * k) for k in range(numHoursInFuture)]


# For ReceiptType = HOUR only
# Returns a list of (datetime, receipt) pairs for each hour over numDays starting from startDate
def generateDatetimeReceiptPairs(numDays, startdate = datetime.now()):
    numHours = numDays * 24
    dateList = allHours(numHours, startdate)
    return [(d, generateReceipt(ReceiptType.HOUR, d)) for d in dateList]


def generateVerificationTable(receiptType, receiptList):
    table = VerificationTable(receiptType)
    for (datetimeObj, receipt) in receiptList:
        sha = hashlib.sha256()
        sha.update((str(randSaltGenerator())).encode())
        sha.update(receipt.encode())
        verifyHex = sha.hexdigest()
        table.addCodeValuePair(verifyHex, datetimeObj)
    return table


def verifyReceipt(receipt, verificationTable):
    for saltValue in range(SALT_SIZE):
        sha = hashlib.sha256()
        sha.update((str(saltValue)).encode())
        sha.update(receipt.encode())
        potentialCode = sha.hexdigest()
        value = verificationTable.getValue(potentialCode)
        if (value != None):
            return value
    return None


if __name__ == "__main__":
      # Argument Parser
    parser = argparse.ArgumentParser()
    parser_args = parser.parse_args()

    # Testing
    dates = generateDatetimeReceiptPairs(1)
    table = generateVerificationTable(ReceiptType.HOUR, dates)

    # Test
    print(dates[0][1])
    print(verifyReceipt(dates[0][1], table))






