# aprx-rf-to-csv.py
# script to parse aprx-rf.log and convert to CSV for further data processing
#
# REFERENCES
# - APRS Symbol Maps
#   http://www.aprs.org/symbols/symbolsX.txt
#   http://aprs.org/symbols/symbols-new.txt
#
# TODO
# - refactor actual CSV printing
# - possibly split to different outputs depending on format (mic-e vs object vs compressed)?
# - declutter main loop, use functions (as soon as I know how)
# - document code (however this is supposed to be done with Python)

import aprslib
import pyproj
import re
from geopy.distance import distance
from datetime import datetime
import math

MYCALL = 'HB9TF-1'
MYLAT = None
MYLON = None

print("timestamp,call,ssid,latitude,longitude,azimuth_deg,distance_m,format,symbol")

# aprx-rf.log pattern
p = re.compile(r'^(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+(?P<source>\S+)\s+(?P<direction>R|T)\s+(?P<message>.+)$')
geo = pyproj.Geod(ellps='WGS84')

with open('data/aprx-rf.log', 'rt') as log:
    for count,line in enumerate(log):
        # try to parse log line, store in data variable
        m = re.match(p, line.strip())
        if not m:
            continue
        data = m.groupdict()

        # we are only interested in packets from by HB9TF-1
        if data['source'] != MYCALL:
            continue

        # try to parse the APRS message, ignore the log line if the message is unparseable
        try:
            aprs_data = aprslib.parse(data['message'])
        except:
            continue

        # we ignore all messages without coordinates
        if any(l not in aprs_data for l in ('latitude', 'longitude')):
            continue

        # extract APRS iGate location from beacon as dynamic reference point for distance calculations
        if data['direction'] == 'T' and aprs_data['from'] == MYCALL:
            MYLAT = aprs_data['latitude']
            MYLON = aprs_data['longitude']
            continue

        if MYLAT is None or MYLON is None:
            continue

        # if any(l not in aprs_data for l in ('altitude', 'from')):
        #     continue

        fwd_azimuth,back_azimuth,distance = geo.inv(MYLAT, MYLON, aprs_data['latitude'], aprs_data['longitude'])

        if math.isnan(fwd_azimuth) or math.isnan(distance):
            continue

        call_ssid = aprs_data['from'].split( '-', 1)
        call = call_ssid[0]
        ssid = '1'
        if len(call_ssid) == 2:
            ssid = call_ssid[1]

        # t = datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S.%f')
        # t.timestamp()

        print("{},{},{},{},{},{},{},{},{}{}".format(data['datetime'], call, ssid, round(aprs_data['latitude'],5), round(aprs_data['longitude'],5), round(fwd_azimuth), round(distance), aprs_data['format'], aprs_data['symbol_table'], aprs_data['symbol']))

        # if count >= 10000:
        #    break
