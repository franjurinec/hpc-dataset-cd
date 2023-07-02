import os
import s3fs
from dotenv import load_dotenv
import numpy as np
from data_transform import convert_pulse_dict_to_numpy_array

# Load .env variables
load_dotenv()

PULSE_LIST = [81768,81798,85306,92207, 95479]
SIGNAL_DICT = {
    'efit': ['Rgeo', 'ahor', 'Vol', 'delRoben', 'delRuntn', 'k'],
    'power': ['P_OH', 'PNBI_TOT', 'PICR_TOT'], 
    'magn': ['IpiFP', 'BTF', 'q95'],
    'gas': ['D_tot'],
    'hrts': ['radius', 'ne', 'ne_unc', 'Te', 'Te_unc']  
}
METADATA = {}
BASE_DIR = os.getcwd()

# Typically this would be a facility-specific access method
remote_fs = s3fs.S3FileSystem(
    key=os.getenv('S3_KEY'),
    secret=os.getenv('S3_PASS'),
    client_kwargs={
        'endpoint_url': 'https://a3s.fi'
    }
)

def get_pulse(shot_number, diagnostic_signal_dict):
    pulse_dict = {}
    for diagnostic, signal_names in diagnostic_signal_dict.items():
        for signal_name in signal_names:
            signal_dict = {}
            for dimension in ['data', 'time']:
                object_name =  f'{shot_number}_{diagnostic}_{signal_name}_{dimension}.npy'
                try:
                    data = np.load(remote_fs.open(f'JET_PULSES/{object_name}'), allow_pickle=True)
                    if diagnostic in ['efit', 'power', 'magn', 'gas']: 
                        data = data.item()[dimension]
                    if isinstance(data, str) and signal_name == 'PICR_TOT': 
                        signal_dict['time'] = pulse_dict['PNBI_TOT']['time']
                        signal_dict['data'] = np.zeros_like(pulse_dict['PNBI_TOT']['time'])
                    else:
                        signal_dict[dimension] = data
                except FileNotFoundError as _:
                    print(f'Did not find {object_name} in JET_PULSES, not returning Pulse')
                    return None
            pulse_dict[signal_name] = signal_dict
    return pulse_dict

os.makedirs(os.path.join(BASE_DIR, 'tmp/out'), exist_ok=True)
for pulse_id in PULSE_LIST:
    pulse = get_pulse(pulse_id, SIGNAL_DICT)
    if pulse is None:
        print(f'Skipping {pulse_id}')
        continue
    pulse_transformed = convert_pulse_dict_to_numpy_array(pulse)
    for key, value in pulse_transformed.items():
        result_path = os.path.join(BASE_DIR, 'tmp/out', f'{pulse_id}_{key}.npy')
        print(f'Saving {result_path}')
        np.save(result_path, value)
