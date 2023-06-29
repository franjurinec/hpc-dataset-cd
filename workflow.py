# Define list of pulses
# Define list of signals
# Define other author/dataset metadata
PULSE_LIST = [81768,81798,85306,92207, 95479]
SIGNAL_DICT = {
    'efit': ['Rgeo', 'ahor', 'Vol', 'delRoben', 'delRuntn', 'k'],
    'power': ['P_OH', 'PNBI_TOT', 'PICR_TOT'], 
    'magn': ['IpiFP', 'BTF', 'q95'],
    'gas': ['D_tot'],
    'hrts': ['radius', 'ne', 'ne_unc', 'Te', 'Te_unc']  
}
METADATA = {}

# Collect source data - pulse list x chosen signals (wrapped dat access call) + data dump (data input dir) + metadata dump (metadata output dir)
collected_pulses = collect_pulses(PULSE_LIST, SIGNAL_DICT)

# Data transformation - transform function x each collected pulse (data input dir -> data output dir) + metadata dump (metadata output dir)
for pulse in collected_pulses:
    pulse_transformed = transform(pulse)
    save_output(pulse_transformed)

# Data/metadata submission - S3 API (data output dir -> remote S3) + InvenioRDM API (metadata output dir -> InvenioRDM record)
if producion_env: # Only upload data / metadata in production env
    submit()

print('Hello world!') # Sanity check
