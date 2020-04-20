import sys
import argparse
import hashlib, base64
import secrets
from datetime import datetime, date
from enum import Enum

# Number of potential salt values
SALT_SIZE = 10001
BYTE_LEN_RAND = 16

# Receipt types
class ReceiptType(Enum):
    HOUR = 0
    ZIPCODE = 1


def getCurrentHour():
  now = datetime.now()
  hourStr = now.strftime("%H")
  return hourStr


def getCurrentDate():
  today = date.today()
  todayStr = today.strftime("%d/%m/%Y")
  return todayStr


def randSaltGenerator():
  secretsGenerator = secrets.SystemRandom()
  randSalt = secretsGenerator.randint(0, SALT_SIZE)
  return randSalt


def randBytesGenerator(k):
  return secrets.token_bytes(k)


def hashInputFormat(receiptType, hourStr, dateStr):
  r = randBytesGenerator(BYTE_LEN_RAND)
  sha = hashlib.sha256()
  if (receiptType == ReceiptType.HOUR):
      sha.update(receiptType, r, hour, date)
  elif (receiptType == ReceiptType.ZIPCODE):
    sha.update(receiptType, r, hour, date)
  code = sha.hexdigest()
  return code[:16]

# Creates a dictionary of hash codes for the day
# hashDict[type][hash] = hour of verifying code
#def generateHashDict(day):




def verifyCode(receiptType, receipt, hashList):
    for saltValue in range(SALT_SIZE):
        sha = hashlib.sha256()
        sha.update(saltValue, receipt)
        potentialHash = sha.hexdigest()
        if potentialHash in hashList[receiptType].keys():
            return hashDict[receiptType][potentialHash]
    return -1


if __name__ == "__main__":
      # Argument Parser
    parser = argparse.ArgumentParser()
    parser_args = parser.parse_args()

    print(getCurrentHour())
    print(getCurrentDate())
    print(randSaltGenerator())
    print(randBytesGenerator(16))
    print(hashInputFormat(0, getCurrentHour(), getCurrentDate()))
