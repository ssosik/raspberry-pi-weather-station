from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import argparse
import csv
import os
import pdb
import shutil
import sys
import time

# NOTE This is not safe for concurrent run with the environment-sensor script

parser = argparse.ArgumentParser(description="Retry uploading failed CSV entries")
parser.add_argument("--file", "-f", help="Specify the file to source CSV rows from", required=True)
args = parser.parse_args()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1QvvjjL3BVvwIS3QMYUIrN6Okn2mEoSGVeYFkE42C99g'
SHEET_RANGE = 'Environment Readings Upload!A1'

creds = None

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


backupfile = args.file + f'-bak.{time.time()}'
shutil.copyfile(args.file, backupfile)

# Read out the lines from the current version of the file
with open(args.file, "r") as csvfile:
    lines = csvfile.readlines()

maxloops = 50
i = 0
while len(lines):

    i+=1
    if i > maxloops:
        break

    # pop off the first line and attempt to publish it to the Sheet. If if fails
    # write it back to disk
    row = lines.pop(0)

    # null out the file
    open(args.file, 'w').close()

    # Write back the rest of the file
    for line in lines:
        r = line.strip().split(',')
        sys.stdout.flush()
        with open(args.file, "a") as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(r)
            csvfile.flush()

    body = { 'values': [row.strip().split(',')] }

    print(f"Publish row {body}")
    sys.stdout.flush()

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
            print(f"updated 1 Row Result: {result}")
            sys.stdout.flush()

        else:
            raise Exception(f"update not expected {result}")

    except Exception as e:
        # If we fall through here, the google update didn't succeed so write the CSV
        # Push the row back into the file
        print(f"Publish error {e}, Writing back row {row}")
        sys.stdout.flush()
        with open(args.file, "a") as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(row.strip().split(','))
            csvfile.flush()

    # Read out the lines from the current version of the file then empty it
    with open(args.file, "r") as csvfile:
        lines = csvfile.readlines()

os.remove(backupfile)
