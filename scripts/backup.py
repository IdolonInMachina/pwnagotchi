import argparse
import os
import sys
import subprocess
import datetime
import time
from paramiko import SSHClient

parser = argparse.ArgumentParser(description="Backup a pwnagotchi.")

parser.add_argument('-u', '--username', help="Unit username",  default='pi')

parser.add_argument('-n', '--hostname',
                    help="Unit hostname or IP", default='10.0.0.2')

parser.add_argument('-o', '--output', help="Output file", default="output.tgz")

args = parser.parse_args()

FILES_TO_BACKUP = [
    "/root/brain.nn",
    "/root/brain.json",
    "/root/.api-report.json",
    "/root/.ssh",
    "/root/.bashrc",
    "/root/.profile",
    "/root/handshakes",
    "/root/peers",
    "/etc/pwnagotchi/",
    "/etc/ssh/",
    "/var/log/pwnagotchi.log",
    "/var/log/pwnagotchi*.gz",
    "/home/pi/.ssh",
    "/home/pi/.bashrc",
    "/home/pi/.profile"
]

current_os = sys.platform.lower()
if 'win' in current_os:
    parameter = "-n"
else:
    parameter = "-c"
with open(os.devnull, 'wb') as devnull:
    call = subprocess.check_call(
        ['ping', parameter, '1', '-w', '2', args.hostname], stdout=devnull, stderr=subprocess.STDOUT)
if call != 0:
    print(f"Unit {args.hostname} can't be reached, make sure it's connected and a static IP assigned to the USB interface")


output = args.output
if output == 'output.tgz':
    curr_time = datetime.datetime.now()
    output = f"backup-{curr_time.strftime('%Y-%m-%d')}.tgz"

print(f"Backing up {args.hostname} to {args.output} ...")

client = SSHClient()
client.load_system_host_keys()
client.connect(args.hostname, username=args.username,
               look_for_keys=True)

stdin, stdout, stderr = client.exec_command(
    f'sudo find {" ".join(FILES_TO_BACKUP)} -type f -print0 | xargs -0 sudo tar cv | gzip -9 > "/home/pi/backups/{output}"')
print(f'STDOUT: {stdout.read().decode("utf8")}')
print(f'STDERR: {stderr.read().decode("utf8")}')

subprocess.call(
    ['scp', f'{args.username}@{args.hostname}:/home/pi/backups/{output}', './backups'])
