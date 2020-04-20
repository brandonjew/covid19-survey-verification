# Covid19 Symptom Survey Crypto
# python3

import sys
import os
import hashlib, base64
import secrets
import copy
import itertools
from datetime import datetime, date, timedelta
from enum import Enum

#################################################################################################
#################################################################################################
# Sample Usage

#1) Generate receipts and codes. Run once. 
def SAMPLE_generate_receipts_and_codes():
  startdate = datetime.now()
  startdate = startdate.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
  numDays = 100
  zipcodeList = [12345, 67890]
  randBytesGenerator = RandBytesGenerator(os.path.join(sys.path[0], "randomSeed.txt"))
  hourReceiptTable = generateHourReceiptTable(randBytesGenerator, numDays, startdate)
  hourVerificationTable = generateVerificationTable(ReceiptType.HOUR, hourReceiptTable)
  zipcodeReceiptTable = generateZipcodeReceiptTable(randBytesGenerator, numDays, zipcodeList, startdate)
  zipcodeVerificationTable = generateVerificationTable(ReceiptType.ZIPCODE, zipcodeReceiptTable)
  return (hourReceiptTable, hourVerificationTable, zipcodeReceiptTable, zipcodeVerificationTable)

# Note that ReceiptTables should be kept private, but VerificationTables can be made public

#2) Generate receipts for users upon completion of the survey
def SAMPLE_generate_receipts_for_users(hourReceiptTable, zipcodeReceiptTable, zipcode):
  date = datetime.now()
  date = date.replace(minute = 0, second = 0, microsecond = 0)
  hourReceipt = hourReceiptTable.getReceiptFromValue(date)
  date = date.replace(hour = 0)
  zipc = ZipcodeObject(zipcode, date)
  zipcodeReceipt = zipcodeReceiptTable.getReceiptFromValue(zipc)
  return (hourReceipt, zipcodeReceipt)
  
#3) Verify receipts from users
def SAMPLE_verify_receipts(hourReceipt, zipcodeReceipt, hourVerificationTable, zipcodeVerificationTable):
  hourVerify = verifyReceipt(hourReceipt, hourVerificationTable)
  zipcodeVerify = verifyReceipt(zipcodeReceipt, zipcodeVerificationTable)
  return (hourVerify, zipcodeVerify)

#4) Generate subtables of hourVerificationTable and zipcodeVerificationTable that contain only the codes for the given day
# These subtables can be given out daily to verifiers
def SAMPLE_generate_verification_subtables_for_day(hourVerificationTable, zipcodeVerificationTable, date):
  date = date.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
  deltaDay = timedelta(days = 1)
  endDate = date + deltaDay
  hourVerificationSubtable = hourVerificationTable.getSubTable(date, endDate)
  zipcodeVerificationSubtable = zipcodeVerificationTable.getSubTable(date, endDate, lambda zipcodeObj: zipcodeObj.datetime)
  return hourVerificationSubtable, zipcodeVerificationSubtable

# Note that the data in any ReceiptTable or VerificationTable can be converted to a list of tuples using getValueReceiptList() and getValueCodeList() respectively.
#################################################################################################
#################################################################################################



SALT_SIZE = 10001   # Number of potential salt values
RECEIPT_LEN = 16  # Size of receipt
BYTE_LEN_RAND = 16  # Size of randomness for random prefix to SHA256 input in generating receipt 

class ReceiptType(Enum):
  HOUR = 0          # Values of this type are datetime objects
  ZIPCODE = 1       # Values of this type are ZipcodeObjects defined below

class ZipcodeObject:
  def __init__(self, zipcode, datetime):
    self.zipcode = zipcode    
    self.datetime = datetime
  def __hash__(self):
    return hash((self.zipcode, self.datetime))
  def __eq__(self, other):
    return ((self.__class__ == other.__class__) and (self.datetime == other.datetime) and (self.zipcode == other.zipcode))

# ReceiptTable
# Keeps track of (value, receipt) mappings
# - values are instances of the appropriate ReceiptType (e.g. the datetime object of the corresponding hour)
# - receipts correspond to values and are given out to users upon completion of the survey
# Should be kept private
class ReceiptTable:
  def __init__(self, receiptType):
    self._receiptType = receiptType # Type of values stored in the verification table
    self._dict = {}
  def __init__(self, receiptType, receiptDict):	
    self._receiptType = receiptType
    self._dict = copy.deepcopy(receiptDict)
  def getType():
    return self._receiptType
  def addValueReceiptPair(self, value, receipt):
    self._dict[value] = receipt
  def removeValueReceiptPair(self, value, receipt):
    if (value in self._dict.keys()):
      del self._dict[value]

 # Returns the receipt corresponding to the given value, or None if not in the table
  def getReceiptFromValue(self, value):
    if (value in self._dict.keys()):
      return self._dict[value]
    return None

  # Returns an unsorted list of all values in the table
  def getValueList(self):
    return list(self._dict.keys())

  # Returns an unsorted list of all receipts in the table
  def getReceiptList(self):
    return list(self._dict.values())

  # Returns a list of (value, receipt) pairs
  def getValueReceiptList(self):
    return [(k, v) for k,v in self._dict.items()]

  # Returns a dictionary mapping values to receipts
  def getValueReceiptDict(self):
    return self._dict  

  # If values can be compared, will return a ReceiptTable that contains only the (value, receipt) pairs with values between valueStart and valueEnd
  # Undefined behavior if values are incomparable
  def getSubTable(self, valueStart, valueEnd, sortKey = None):
    newDict = {}
    for value in sorted(self._dict.keys(), key = sortKey):
      sortValue = value
      if (sortKey != None):
          sortValue = sortKey(value)
      if ((valueStart <= sortValue) and (sortValue < valueEnd)):
        newDict[value] = self._dict[value]
    return ReceiptTable(self._receiptType, newDict)

# VerificationTable
# Keeps track of (value, code) mappings
# - values are instances of the appropriate ReceiptType (e.g. the datetime object of the corresponding hour)
# - codes are hashes of the receipts for the corresponding value
# Can be given out publicly
class VerificationTable:
  def __init__(self, receiptType):
    self._receiptType = receiptType # Type of values stored in the verification table
    self._valueToCodeDict = {}
    self._codeToValueDict = {}
  def getType():
    return self._receiptType
  def addValueCodePair(self, value, code):
    self._codeToValueDict[code] = value
    self._valueToCodeDict[value] = code
  def removeValueCodePair(self, value, code):
    if (code in self._codeToCodeDict.keys()):
      del self._codeToValueDict[code]
    if (value in self._valueToCodeDict.keys()):
      del self._valueToCodeDict[value]

  # Returns the code corresponding to the given value, or None if not in the table
  def getCodeFromValue(self, value):
    if (value in self._valueToCodeDict.keys()):
      return self._valueToCodeDict[value]
    return None

  # Returns the value corresponding to the given code, or None if not in the table
  def getValueFromCode(self, code):
    if (code in self._codeToValueDict.keys()):
      return self._codeToValueDict[code]
    return None  

  # Returns an unsorted list of all values in the table
  def getValueList(self):
    return list(self._valueToCodeDict.keys())

  # Returns an unsorted list of all codes in the table
  def getCodeList(self):
    return list(self._valueToCodeDict.values())

  # Returns an unsorted list of (value, code) pairs
  def getValueCodeList(self):
    return [(k, v) for k,v in self._valueToCodeDict.items()]

  # If values can be compared, will return a list of (value, code) pairs, sorted by value
  # Undefined behavior if values are incomparable
  def getSortedValueCodeList(self, sortKey = None):
    lst = []
    for value in sorted(self._valueToCodeDict.keys(), key = sortKey):
      lst.append((value, self._valueToCodeDict[value]))
    return lst   

  # If values can be compared, will return a list of (value, code) pairs with values between valueStart and valueEnd, sorted by value
  # Undefined behavior if values are incomparable
  def getSortedValueCodeList(self, valueStart, valueEnd, sortKey = None):
    lst = []
    for value in sorted(self._valueToCodeDict.keys(), key = sortKey):
      sortValue = value
      if (sortKey != None):
        sortValue = sortKey(value)
      if ((valueStart <= sortValue) and (sortValue < valueEnd)):
        lst.append((value, self._valueToCodeDict[value]))
    return lst   

  # If values can be compared, will return a VerificationTable that contains only the (value, code) pairs with values between valueStart and valueEnd
  # Undefined behavior if values are incomparable
  def getSubTable(self, valueStart, valueEnd, sortKey = None):
    table = VerificationTable(self._receiptType)
    for value in sorted(self._valueToCodeDict.keys(), key = sortKey):
      sortValue = value
      if (sortKey != None):
        sortValue = sortKey(value)
      if ((valueStart <= sortValue) and (sortValue < valueEnd)):
        table.addValueCodePair(value, self._valueToCodeDict[value])
    return table


# Stateful random bytes generator that uses the file given during initialization as its seed
class RandBytesGenerator():
  _state = 0
  _secretsGenerator = 0
  def __init__(self, randSeedFileName):
    with open(randSeedFileName, 'r') as f:
      self._state = f.read().encode()
    self._secretsGenerator = secrets.SystemRandom()
  def getNextRandBytes(self, k):
    self._state = bytes([a ^ b for a,b in zip(self._state, secrets.token_bytes(BYTE_LEN_RAND))])
    sha = hashlib.sha256()
    sha.update(self._state)
    self._state = sha.digest()
    return self._state[:k]

def randSaltGenerator():
  secretsGenerator = secrets.SystemRandom()
  randSalt = secretsGenerator.randint(0, SALT_SIZE)
  return randSalt

# Generates a receipt of size RECEIPT_LEN for the given value
def generateReceipt(receiptType, value, randBytesGenerator):
  r = randBytesGenerator.getNextRandBytes(BYTE_LEN_RAND)
  sha = hashlib.sha256()
  if (receiptType == ReceiptType.HOUR):
    sha.update(b'0')
    sha.update(r)
    sha.update(bytes(str.encode(value.strftime("%H"))))
    sha.update(bytes(str.encode(value.strftime("%d/%m/%Y"))))
  elif (receiptType == ReceiptType.ZIPCODE):
    sha.update(b'1')
    sha.update(r)
    sha.update(bytes(value.zipcode))
    sha.update(bytes(str.encode(value.datetime.strftime("%d/%m/%Y"))))
  code = sha.hexdigest()
  return code[:RECEIPT_LEN]


# For ReceiptType.HOUR only
# Generates a ReceiptTable of (datetime, receipt) pairs for each hour over numDays starting from startDate
# Should be run once
def generateHourReceiptTable(randBytesGenerator, numDays, startdate = datetime.now()):
  startdate = startdate.replace(minute = 0, second = 0, microsecond = 0)
  numHours = numDays * 24
  hour = timedelta(hours = 1)
  dateList = [startdate + (hour * k) for k in range(numHours)]
  return ReceiptTable(ReceiptType.HOUR, {d:generateReceipt(ReceiptType.HOUR, d, randBytesGenerator) for d in dateList})

# For ReceiptType.ZIPCODE only
# Generates a ReceiptTable of (ZipcodeObject, receipt) pairs for each zipcode in zipcodeList over numDays starting from startDate
# Should be run once
def generateZipcodeReceiptTable(randBytesGenerator, numDays, zipcodeList, startdate = datetime.now()):
  startdate = startdate.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
  dateList = [startdate + (k * timedelta(days = 1)) for k in range(numDays)]
  allPairsZipcodesDates = list(itertools.product(zipcodeList, dateList))
  return ReceiptTable(ReceiptType.ZIPCODE, {ZipcodeObject(z, d):generateReceipt(ReceiptType.ZIPCODE, ZipcodeObject(z, d), randBytesGenerator) for (z, d) in allPairsZipcodesDates})

# Generates a VerificationTable from the ReceiptTable
# Should be run once after the ReceiptTable is generated
# Note that the verification codes are randomized with random salts, so different calls to this function will generate different codes
def generateVerificationTable(receiptType, receiptTable):
  table = VerificationTable(receiptType)
  for (value, receipt) in receiptTable.getValueReceiptDict().items():
    sha = hashlib.sha256()
    sha.update((str(randSaltGenerator())).encode())
    sha.update(receipt.encode())
    verifyHex = sha.hexdigest()
    table.addValueCodePair(value, verifyHex)
  return table

# Returns the value (eg. datetime) corresponding to the receipt in the verification table, or None if the receipt is invalid.
def verifyReceipt(receipt, verificationTable):
  for saltValue in range(SALT_SIZE):
    sha = hashlib.sha256()
    sha.update((str(saltValue)).encode())
    sha.update(receipt.encode())
    potentialCode = sha.hexdigest()
    value = verificationTable.getValueFromCode(potentialCode)
    if (value != None):
      return value
  return None

if __name__ == "__main__":

  # Test code
  hr, hv, zr, zv = SAMPLE_generate_receipts_and_codes()
  hreceipt, zreceipt = SAMPLE_generate_receipts_for_users(hr, zr, 12345)
  print(hreceipt, zreceipt)
  hverify, zverify = SAMPLE_verify_receipts(hreceipt, zreceipt, hv, zv)
  print(hverify)
  print(zverify.zipcode, zverify.datetime)
  hsv, zsv = SAMPLE_generate_verification_subtables_for_day(hv, zv, datetime.now())
  #print(hsv.getValueCodeList())
  print([(z.zipcode, z.datetime, v) for (z, v) in zsv.getValueCodeList()])
  
  # More test code
  #randBytesGenerator = RandBytesGenerator(os.path.join(sys.path[0], "randomSeed.txt"))
  #dates = generateHourReceiptTable(randBytesGenerator, 100)
  #table = generateVerificationTable(ReceiptType.HOUR, dates)
  #print((dates.getReceiptList())[0])
  #print(verifyReceipt((dates.getReceiptList())[0], table))

  #zipc = ZipcodeObject(12345, datetime.now())
  #receipt = generateReceipt(ReceiptType.ZIPCODE, ZipcodeObject(12345, datetime.now()), randBytesGenerator)
  #table2 = generateVerificationTable(ReceiptType.ZIPCODE, ReceiptTable(ReceiptType.ZIPCODE, {zipc: receipt}))
  #print(verifyReceipt(receipt, table2).zipcode)

  #zipcodeList = [12345, 12346, 12347]
  #zipcodeReceiptTable = generateZipcodeReceiptTable(randBytesGenerator, 1, zipcodeList)
  #print(zipcodeReceiptTable.getReceiptList())


    
    
    
    
    
    