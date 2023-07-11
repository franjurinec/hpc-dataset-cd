import os
import json
from random import randint
import s3fs
import numpy as np
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Typically this would be a facility-specific access method
remote_fs = s3fs.S3FileSystem(
    key=os.getenv('S3_KEY'),
    secret=os.getenv('S3_PASS'),
    client_kwargs={
        'endpoint_url': 'https://a3s.fi'
    }
)

# Prepare metadata output dir
META_DIR = os.path.join(os.getcwd(), 'tmp/meta')
os.makedirs(META_DIR, exist_ok=True)
os.makedirs(os.path.join(META_DIR, 'in_pulses'), exist_ok=True)


# Output base AUG metadata
with open(os.path.join(META_DIR, 'source_meta.json'), "w", encoding="UTF-8") as source_meta_file:
    source_meta = json.dumps({
        "name": "JET",
        "website": "https://euro-fusion.org/devices/jet/"
    }, indent=4)
    source_meta_file.write(source_meta)

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
                    output_metadata(shot_number, {
                            'pulse': shot_number, 
                            'success': False
                            }, 'in_pulses')
                    return None
            pulse_dict[signal_name] = signal_dict
    output_metadata(shot_number, {
        'pulse': shot_number, 
        'success': True, 
        'diagnostics': {k:{'signals': v, 'calibration': randint(1,10)} for k, v in diagnostic_signal_dict.items()} 
        }, 'in_pulses')
    return pulse_dict

def output_metadata(name, metadata, out_dir):
    with open(os.path.join(META_DIR, out_dir, f'{name}.json'), "w", encoding="UTF-8") as meta_file:
        meta_json_object = json.dumps(metadata, indent=4)
        meta_file.write(meta_json_object)
