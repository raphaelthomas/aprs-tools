import aprslib
import re
import json
from datetime import datetime 

p = re.compile(r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+(?P<source>\S+)\s+(?P<direction>R|T)\s+(?P<raw>.+)$')

with open('aprx-rf.log', 'rt') as log:
    for count,line in enumerate(log):
        m = re.match(p, line.strip())
        if not m:
            continue

        data = m.groupdict()
        if data['source'] != 'HB9TF-1' and data['source'] != 'HB9TF-2':
            continue

        try:
            aprs_data = aprslib.parse(data['raw'])
        except:
            continue

        aprs_data['source_direction'] = data['direction'] 
        aprs_data['source'] = data['source'] 

        call_ssid = aprs_data['from'].split( '-', 1)
        aprs_data['from_ssid'] = '1'
        aprs_data['from_call'] = call_ssid[0]
        if len(call_ssid) == 2:
            aprs_data['from_ssid'] = call_ssid[1]

        aprs_data['timestamp'] = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S.%f').timestamp()

        print(json.dumps(aprs_data))
