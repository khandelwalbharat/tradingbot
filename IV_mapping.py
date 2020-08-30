import datetime
import getpass
import os
import json

def get_workdir():
    workdir = "/home/{}/spare/local/tradingbot/IV/".format(getpass.getuser())
    return workdir

workdir = get_workdir()
files = os.listdir(workdir)

IV_mappings = {}

for file in sorted(files):
    year = int(file[:4])
    month = int(file[4:6])
    date = int(file[6:8])
    # day = datetime.date(year, month, date)
    day = file[:8]
    with open(workdir+file, 'r') as f:
        stocks = json.load(f)
    IV_mappings[day] = stocks

with open('IV_mappings.json', 'w') as f:
    json.dump(IV_mappings, f)
