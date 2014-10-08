import os
import sys
import json

if len(sys.argv) == 2:
    xname = sys.argv[1]
else:
    xname = 'login'

fname = 'har_files/' + xname + '.har'
"""
sum_file = 'xdebug_files/' + xname + '/sum.log'
sum_data = {}
with open(sum_file) as f:
    for line in f.readlines():
        sid, t, fom = line.split(' ')
        sum_data[sid] = int(t)
"""

s = ''
with open(fname) as f:
    s = f.read()

json_data = json.loads(s)


csv_header = 'id,Block,DNS,Connect,Send,Wait,Receive,Total,---,PHP Execution Time'
print csv_header


blocked = 0.0
dns = 0.0
connect = 0.0
send = 0.0
wait = 0.0
receive = 0.0
time = 0.0

for i in xrange(len(json_data['log']['entries'])):
    data = json_data['log']['entries'][i]

    xid = data['request']['queryString'][0]['value']
    rt = data['timings']

    print '{0},{1},{2},{3},{4},{5},{6},{7},---,{8}'.format(
        xid,
        int(round(rt['blocked'])),
        int(round(rt['dns'])),
        int(round(rt['connect'])),
        int(round(rt['send'])),
        int(round(rt['wait'])),
        int(round(rt['receive'])),
        int(round(data['time'])),
        'N/A'
        #sum_data[str(xid)]
    )

    blocked += rt['blocked']
    send += rt['send']
    wait += rt['wait']
    receive += rt['receive']
    time += data['time']

    if rt['dns'] != -1:
        dns += rt['dns']

    if rt['connect'] != -1:
        connect += rt['connect']


print '{0},{1},{2},{3},{4},{5},{6},{7},---,{8}'.format(
    'TOTAL(ms)',
    int(blocked),
    int(dns),
    int(connect),
    int(send),
    int(wait),
    int(receive),
    int(time),
    'N/A'
    #sum(sum_data.values())
)

print '{0},{1},{2},{3},{4},{5},{6},{7},---,{8}'.format(
    'Percent(%)',
    round(blocked / time * 100, 2),
    round(dns / time * 100, 2),
    round(connect / time * 100, 2),
    round(send / time * 100, 2),
    round(wait / time * 100, 2),
    round(receive / time * 100, 2),
    '100%',
    'N/A'
    #round(sum(sum_data.values()) / wait * 100, 2)
)

print csv_header

