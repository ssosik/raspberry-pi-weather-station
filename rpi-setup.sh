#!/bin/bash

# NOTE!!!! Set the authorized_keys to contain the fingerprint of the keys YOU use
cat <<EOF > sshd_config
MaxAuthTries 6
MaxSessions 10
PubkeyAuthentication yes
AuthorizedKeysFile      .ssh/authorized_keys
ChallengeResponseAuthentication no
PasswordAuthentication no
UsePAM no
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem       sftp    /usr/lib/openssh/sftp-server
EOF
mv sshd_config /etc/ssh/sshd_config

mkdir $HOME/.ssh
cat <<EOF > $HOME/.ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDcnA6LSZbTmBDKWBkoaZ2WKYhAuHqdtPTsjbAKrrpFxeATqqolrpCs4pxLqr2hd/CGvD1ax1HC7x5bIkhpfTu0ysZoSx03A/yLNi0quTcGikD3PCFXDY2Afmdud5DEugrOsxfgwLWSz0xqzXfkVqB42EUOLa71cDQfPt/J/fIhu6ymUttMN9t7lDIhRq9vs5DcOOEsV/FtFYOfUfrUEaOx1qtUNBKGSxKeLZKXcyfI03AK0oaI6HTV37tDAdSHdWX7uqyWCNpzk5KDeJ9m2MAf5A5UcQ4PbtJxzlzR0IG6bzUCC3RsnO4qO2aoDMcPUeb1tq07lYajDHjGLSZCBk0B .ssh/id_rsa.pizero
EOF

service sshd restart

# Configure for BME280 temperature and humidity sensor

# Enable I2C in the Interfacing options
# Don't forget to set the timezone!
raspi-config

# Install smbus and i2c-tools
apt-get install -y python-smbus i2c-tools

# Expect `i2c_dev` and `i2c_bcmXXXX`
lsmod | grep i2c_

# Expect `77`
i2cdetect -y 1

apt install python3-pip

pip3 install --upgrade RPi.bme280 google-api-python-client google-auth-httplib2 google-auth-oauthlib pytz

# Write the systemd service
cat <<EOF > environment-monitor.service
[Unit]
Description=Capture Temperature, Humidity, and Pressure every 10 minutes
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 ./environment-sensor.py

[Install]
WantedBy=multi-user.target
EOF

mv environment-monitor.service /lib/systemd/system/environment-monitor.service
chmod 644 /lib/systemd/system/environment-monitor.service

# Enable the service
systemctl daemon-reload
systemctl enable environment-monitor.service
systemctl start environment-monitor.service


