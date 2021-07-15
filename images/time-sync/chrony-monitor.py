import datetime
from kubernetes import client, config
import logging
import os
import subprocess
import time

ANNOTATION_PREFIX = 'time-sync.riasc.io'

NODE_NAME = os.environ.get('NODE_NAME', 'infis-pi')

def get_status():
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

    for _, source in status.get('sources', {}).items():
        if source.get('state', 'unknown') == 'synced':
            return True

    return False

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
    else:
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
    annotations = {
        ANNOTATION_PREFIX + '/' + key.replace('_', '-'): str(status[key]) if status else None for key in ['stratum', 'ref_name', 'leap_status']
    }

    patch = {
        'metadata': {
            'annotations': annotations
        }
    }

    v1.patch_node(NODE_NAME, patch)

    logging.info('Updated node annotations')

def main():
    logging.basicConfig(level=logging.INFO)

    if os.environ.get('KUBECONFIG'):
        config.load_kube_config()
    else:
        config.load_incluster_config()

    v1 = client.CoreV1Api()

    while True:
        try:
            status = get_status()
            # status = {'sources': {'134.130.4.17': {'mode': 'server', 'state': 'combined', 'stratum': '1', 'poll': '10', 'reach': '377', 'last_rx': '461', 'last_sample': '-0.000032053'}, '134.130.5.17': {'mode': 'server', 'state': 'synced', 'stratum': '1', 'poll': '10', 'reach': '377', 'last_rx': '392', 'last_sample': '-0.000043199'}}, 'ref_id': 86820511, 'ref_name': '134.130.5.17', 'stratum': 2, 'ref_time': datetime.datetime(2021, 6, 28, 13, 43, 10, 329265), 'current_correction': 1.7534e-05, 'last_offset': 2.552e-06, 'rms_offset': 1.9959e-05, 'freq_ppm': -87.802, 'resid_freq_ppm': 0.0, 'skew_ppm': 0.006, 'root_delay': 0.000375683, 'root_dispersion': 0.00056641, 'last_update_interval': 1024.8, 'leap_status': 'normal'}

            logging.info('Got status: %s', status)
        except Exception as e:
            logging.warning('Failed to query Chrony status: %s', e)

            status = None

        patch_node_status(v1, status)
        patch_node(v1, status)

        time.sleep(10)


if __name__ == '__main__':
    main()
