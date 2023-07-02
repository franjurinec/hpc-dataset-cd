import os
from typing import List
import s3fs
from dotenv import load_dotenv
import numpy as np
from scipy.interpolate import interp1d

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

def get_time_windowed_arrays(time_array: np.ndarray, list_arrays: List[np.ndarray], t_start:float, t_end:float) -> List[np.ndarray]:
    """ A function that takes a time array, start and end times, and returns the filtered arrays in list_arrays within the time window"""
    window_bool = np.logical_and(time_array >= t_start, time_array <= t_end)
    windowed_arrays = [arr[window_bool] for arr in list_arrays]
    return windowed_arrays

def convert_pulse_dict_to_numpy_array(pulse_dict):
    relevant_mp_columns = ['Rgeo', 'ahor', 'Vol', 'delRoben', 'delRuntn', 'k', 'P_OH', 'PNBI_TOT', 'PICR_TOT', 'IpiFP', 'BTF', 'q95', 'D_tot']

    ######################
    ### Profile Gather ###
    ######################
    profile_data = [pulse_dict[name]['data'] for name in ['radius', 'ne', 'ne_unc', 'Te', 'Te_unc']]
    profile_data.insert(0, pulse_dict['ne']['time'])
    
    t_start_hrts, t_end_hrts = profile_data[0][0], profile_data[0][-1]
    t_start_mps, t_end_mps = 0.0, np.inf
    for mp_key in relevant_mp_columns: 
        _min, _max = pulse_dict[mp_key]['time'].min(), pulse_dict[mp_key]['time'].max()
        if _min > t_start_mps:
            t_start_mps = _min
        if _max < t_end_mps:
            t_end_mps = _max
    t1, t2 = max(t_start_mps, t_start_hrts), min(t_end_mps, t_end_hrts)
    
    relevant_profile_data = get_time_windowed_arrays(profile_data[0], profile_data, t1, t2)
    relevant_time_windows = relevant_profile_data.pop(0)
    relevant_radii = relevant_profile_data[0]
    relevant_profs = np.stack([relevant_profile_data[1], relevant_profile_data[3]], 1)
    
    ######################
    ### Machine params ###
    ######################
    
    
    relevant_machine_parameters: np.array = np.empty((len(relevant_time_windows), len(relevant_mp_columns)))
    for mp_idx, mp_key in enumerate(relevant_mp_columns):
        relevant_mp_vals = np.zeros(len(relevant_time_windows))
        mp_raw_data, mp_raw_time = pulse_dict[mp_key]['data'], pulse_dict[mp_key]['time']
        if mp_raw_time is None:
            relevant_machine_parameters[:, mp_idx] = relevant_mp_vals
            continue
        else:
            f = interp1d(mp_raw_time, mp_raw_data)
            relevant_mp_vals = f(relevant_time_windows)
        relevant_machine_parameters[:, mp_idx] = relevant_mp_vals
    final_dict = {'MPS': relevant_machine_parameters, 'PROFS': relevant_profs, 'RADII': relevant_radii, 'TIME': relevant_time_windows}
    return final_dict



base_dir = os.getcwd()

os.makedirs(os.path.join(base_dir, 'tmp/out'), exist_ok=True)
for pulse_id in PULSE_LIST:
    pulse = get_pulse(pulse_id, SIGNAL_DICT)
    if pulse is None:
        print(f'Skipping {pulse_id}')
        continue
    pulse_transformed = convert_pulse_dict_to_numpy_array(pulse)
    for key, value in pulse_transformed.items():
        result_path = os.path.join(base_dir, 'tmp/out', f'{pulse_id}_{key}.npy')
        print(f'Saving {result_path}')
        np.save(result_path, value)


