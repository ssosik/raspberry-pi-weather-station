# sudo pip3 install --upgrade pytz RPi.bme280 google-api-python-client google-auth-httplib2 google-auth-oauthlib
#

from __future__ import print_function
import bme280
import csv
import smbus2
import time
import os.path
import sys
from pytz import timezone    
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1QvvjjL3BVvwIS3QMYUIrN6Okn2mEoSGVeYFkE42C99g'
SHEET_RANGE = 'Environment Readings Upload!A1'

# BME280 settings
port = 1
address = 0x77
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

csv_outfile = f"/home/pi/data.csv"
tz = timezone('US/Eastern')

creds = None

try:
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

except Exception as e:
    print(f"Login error {e}")
    sys.stdout.flush()
    service = None


print("Reading values from environment sensor")
sys.stdout.flush()

# Get Data from Sensor
bme280data = bme280.sample(bus, address, calibration_params)
humidity = format(bme280data.humidity, ".1f")
temp_f = format((bme280data.temperature * 9/5) + 32, ".1f")
pressure = format(bme280data.pressure, ".1f")
now = bme280data.timestamp
local_time = tz.localize(now)

row = (local_time.strftime('%m/%d/%Y %I:%M:%S%p'), temp_f, humidity, pressure)
body = { 'values': [row] }

try:
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()

    updates = result.get('updates')
    if updates is not None and updates.get('updatedRows') == 1:
        # The good case, we updated a row, continue
        print("updated 1 Row")
        sys.stdout.flush()

    else:
        raise Exception(f"update not expected {result}")

except Exception as e:
    # If we fall through here, the google update didn't succeed so write the CSV
    # Emit row to CSV
    print(f"Publish error {e}, defaulting to writing CSV to disk")
    sys.stdout.flush()

    with open(csv_outfile, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row)
