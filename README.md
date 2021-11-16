# Simple raspberry pi weather tracking to Google Sheet

Use this to setup a raspberry Pi Zero with the BME 280
temperature/humidity/pressure sensor to periodically record stats and then
attempt to upload them to a Google Sheet. Simple script with no retries, so it
writes to a CSV file in case the stats publishing fails. Included reupdater
script to go through the CSV file and attempt to publish the failed rows.

# Useful links

Info on Raspberry Pi Zero:
  https://www.raspberrypi.com/products/raspberry-pi-zero/
RaspberryPi Docs:
  https://www.raspberrypi.com/documentation/
  https://www.raspberrypi.com/documentation/computers/remote-access.html#passwordless-ssh-access
Guide for writing a temperature sensor python script
  https://medium.com/initial-state/how-to-build-a-raspberry-pi-refrigerator-freezer-monitor-f7a91075c2fd
Docs on how to set up publishing to a Sheet through Google Sheets API
  See section below
Set up systemd to automatically run a script:
  https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

# Get Raspbian Lite on an SD Card

Download the imager from https://www.raspberrypi.com/software/

Insert Micro SD card and image it

Once done, eject and then remount the SD card

# Initial Image customization

The SD card should be mounted under 'boot'

## Enable SSH

```bash
# Just touch this file to enable SSH
touch /Volumes/boot/ssh
```

## Setup WIFI

```bash
# Write the boot/wpa_supplicant.conf file with network SSID and Password
SSID="your-network"
PSK="your-network-password"
cat <<EOF > /Volumes/boot/wpa_supplicant.conf
country=us
update_config=1
ctrl_interface=/var/run/wpa_supplicant
network={
 scan_ssid=1
 ssid="$SSID"
 psk="$PSK"
}
EOF
```

# Unmount SD card boot the raspberry pi from it

Assuming it booted up fine and was able to connect to the network.

Need to find the IP address it has assigned

```
ssh pi@10.10.10.119
```

Find the default password according to this page https://tutorials-raspberrypi.com/raspberry-pi-default-login-password/

`raspberry`

# Configure the running host

```
./rpi-setup.sh
```

# Try to automatically publish to google doc

https://support.google.com/googleapi/answer/6158862?hl=en
https://console.cloud.google.com/apis/credentials?project=foo-bar-226711

API Key= XXXXXXXX

https://docs.brainstormforce.com/create-google-sheet-api-key/
https://developers.google.com/sheets/api/quickstart/python

--------

Create a project: https://developers.google.com/workspace/guides/create-project

Enable Google Workspace API for Google Doc https://developers.google.com/workspace/guides/create-project#enable-api
https://console.cloud.google.com/apis/api/docs.googleapis.com/overview?project=foo-bar-226711

https://console.cloud.google.com/apis/credentials/oauthclient/527041641119-5akroaikm71tvpod72drk27i25040vm0.apps.googleusercontent.com?project=foo-bar-226711
Client ID: XXXXXXXX-XXXXXXXX.apps.googleusercontent.com
Secret: XXXXXXXX-XXXXXXXX-XXXXXXXX

--------

https://developers.google.com/sheets/api/quickstart/python
https://developers.google.com/workspace/guides/create-project
https://console.cloud.google.com/apis/api/sheets.googleapis.com/overview?project=foo-bar-226711

Search for 'Sheets API' in search box, select it, then enable it.

Credential should be associated there.


## Notes on trying to get google API working

Download the credentials JSON from https://console.cloud.google.com/apis/api/sheets.googleapis.com/credentials?project=foo-bar-226711
and move to `credentials.json`

```bash
# On Mac
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

python3 google-sheets-api-test.py
# Above will do a browser redirect
```

NOTE That the browser redirect will login via me@foobar.com

I needed to go to the OAuth Consent Screen and Publish the App

Scopes: https://developers.google.com/identity/protocols/oauth2/scopes#sheets
Append API https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append
