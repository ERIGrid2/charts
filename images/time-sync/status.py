import logging
import os
import time
import subprocess
import threading

from datetime import datetime
from http.client import responses
from tornado import ioloop, web
from kubernetes import client, config
from gpsdclient import GPSDClient

API_PREFIX = '/v1'
UPDATE_INTERVAL = 10.0
ANNOTATION_PREFIX = 'time-sync.riasc.eu'
NODE_NAME = os.environ.get('NODE_NAME', 'infis-pi')

class BaseRequestHandler(web.RequestHandler):

    def initialize(self, status):
            self.status = status

    def write_error(self, status_code, **kwargs):
        self.finish({
            'error': responses.get(status_code, 'Unknown error'),
            'code': status_code,
            **kwargs
        })

class StatusHandler(BaseRequestHandler):

    def get(self):
        if self.status:
            return self.status
        else:
            raise web.HTTPError(500, "failed to get status")

class SyncedHandler(BaseRequestHandler):

    def get(self):
        if not is_synced(self.status):
            raise web.HTTPError(500, "not synced")

def patch_node_status(v1, status):
    synced = is_synced(status)

    if synced is True:
        condition = {
            'type': 'TimeSynced',
            'status': 'True',
            'reason': 'ChronyHasSyncSource',
            'message': 'Time of node is synchronized'
        }
    elif synced is False:
        condition = {
            'type': 'TimeSynced',
            'status': 'False',
            'reason': 'ChronyHasNoSyncSource',
            'message': 'Time of node is not synchronized'
        }
    else: # e.g. None
        condition = {
            'type': 'TimeSynced',
            'status': 'Unknown',
            'reason': 'ChronyNotRunning',
            'message': 'Time of node is not synchronized'
        }

    patch = {
        'status': {
            'conditions': [condition]
        }
    }

    ret = v1.patch_node_status(NODE_NAME, patch)

    logging.info('Updated node condition')

def patch_node(v1, status):
    gpsd_status = status.get('gpsd')
    chrony_status = status.get('chrony')

    annotations = {}

    if chrony_status:
        for key in ['stratum', 'ref_name', 'leap_status']:
            annotations[key] = chrony_status.get(key)

    if gpsd_status:
        if tpv := gpsd_status.get('tpv'):
            if tpv.get('mode') == 1:
                fix = 'none'
            elif tpv.get('mode') == 2:
                fix = '2d'
            elif tpv.get('mode') == 2:
                fix = '3d'
            else:
                fix = 'unknown'

            if tpv.get('status') == 2:
                status = 'dgps'
            else:
                status = 'none'

            annotations.update({
                'latitude': tpv.get('lat'),
                'longitude': tpv.get('lon'),
                'altitude': tpv.get('alt'),
                'gps-fix': fix,
                'gps-status': status
            })

    patch = {
        'metadata': {
            'annotations': {
                ANNOTATION_PREFIX + '/' + key.replace('_', '-'): value for (key, value) in annotations.items()
            }
        }
    }

    v1.patch_node(NODE_NAME, patch)

    logging.info('Updated node annotations')

def get_chrony_status():
    sources = {}
    fields = {
        'sources': sources
    }

    ret = subprocess.run(['chronyc', '-ncm', 'tracking', 'sources'], capture_output=True, check=True)

    lines = ret.stdout.decode('ascii').split('\n')
    cols = lines[0].split(',')

    fields['ref_id'] = int(cols[0])
    fields['ref_name'] = cols[1]
    fields['stratum'] = int(cols[2])
    fields['ref_time'] = datetime.utcfromtimestamp(float(cols[3]))
    fields['current_correction'] = float(cols[4])
    fields['last_offset'] = float(cols[5])
    fields['rms_offset'] = float(cols[6])
    fields['freq_ppm'] = float(cols[7])
    fields['resid_freq_ppm'] = float(cols[8])
    fields['skew_ppm'] = float(cols[9])
    fields['root_delay'] = float(cols[10])
    fields['root_dispersion'] = float(cols[11])
    fields['last_update_interval'] = float(cols[12])
    fields['leap_status'] = cols[13].lower()

    for line in lines[1:]:
        cols = line.split(',')
        if len(cols) < 8:
            continue

        name = cols[2]
        if cols[0] == '^':
            mode = 'server'
        elif cols[0] == '=':
            mode = 'peer'
        elif cols[0] == '#':
            mode = 'ref_clock'

        if cols[1] == '*':
            state = 'synced'
        elif cols[1] == '+':
            state = 'combined'
        elif cols[1] == '-':
            state = 'excluded'
        elif cols[1] == '?':
            state = 'lost'
        elif cols[1] == 'x':
            state = 'false'
        elif cols[1] == '~':
            state = 'too_variable'

        sources[name] = {
            'mode': mode,
            'state': state,
            'stratum': cols[3],
            'poll': cols[4],
            'reach': cols[5],
            'last_rx': cols[6],
            'last_sample': cols[7]
        }

    return fields

def is_synced(status):
    if status is None:
        return None

    chrony_status = status.get('chrony')
    if chrony_status is None:
        return None

    for _, source in status.get('sources', {}).items():
        if source.get('state', 'unknown') == 'synced':
            return True

    return False

def stream_gpsd_status(status):
    client = GPSDClient(host="127.0.0.1")

    gpsd_status = {}
    status['gpsd'] = gpsd_status

    # or as python dicts (optionally convert time information to `datetime` objects)
    for result in client.dict_stream(convert_datetime=True):
        cls = result['class'].lower()
        gpsd_status[cls] = result

def update_thread(v1, status):
    
    while True:
        update(v1, status)
        time.sleep(UPDATE_INTERVAL)

def update(v1, status):
    try:
        status['chrony'] = get_chrony_status()
        # status['chrony'] = {
        #     "sources": {
        #         "134.130.4.17": {
        #             "mode": "server",
        #             "state": "combined",
        #             "stratum": "1",
        #             "poll": "10",
        #             "reach": "377",
        #             "last_rx": "461",
        #             "last_sample": "-0.000032053",
        #         },
        #         "134.130.5.17": {
        #             "mode": "server",
        #             "state": "synced",
        #             "stratum": "1",
        #             "poll": "10",
        #             "reach": "377",
        #             "last_rx": "392",
        #             "last_sample": "-0.000043199",
        #         },
        #     },
        #     "ref_id": 86820511,
        #     "ref_name": "134.130.5.17",
        #     "stratum": 2,
        #     "ref_time": datetime.datetime(2021, 6, 28, 13, 43, 10, 329265),
        #     "current_correction": 1.7534e-05,
        #     "last_offset": 2.552e-06,
        #     "rms_offset": 1.9959e-05,
        #     "freq_ppm": -87.802,
        #     "resid_freq_ppm": 0.0,
        #     "skew_ppm": 0.006,
        #     "root_delay": 0.000375683,
        #     "root_dispersion": 0.00056641,
        #     "last_update_interval": 1024.8,
        #     "leap_status": "normal",
        # }

        logging.info('Got status: %s', status)
    except Exception as e:
        logging.warning('Failed to query status: %s', e)

        status = None

        patch_node_status(v1, status)
        patch_node(v1, status)

def main():
    logging.basicConfig(level=logging.INFO)

    if os.environ.get('KUBECONFIG'):
        config.load_kube_config()
    else:
        config.load_incluster_config()

    v1 = client.CoreV1Api()
    status = None

    # Start background thread
    t = threading.Thread(target=update_thread, args=(v1, status))
    t.start()

    t2 = threading.Thread(target=stream_gpsd_status, args=(status))
    t2.start()

    args = {
        'status': status
    }

    app = web.Application([
        (API_PREFIX + r"/", StatusHandler, args),
        (API_PREFIX + r"/synced", SyncedHandler, args)
    ])

    app.listen(80)
    ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
