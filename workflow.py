import os
from services.data_access import get_pulse
import services.s3 as s3
import services.invenio as invenio

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

def transform(pulse):
    return {}

# Data transformation - transform function x each collected pulse (data input dir -> data output dir) + metadata dump (metadata output dir)
for pulse_id in PULSE_LIST:
    pulse = get_pulse(pulse_id, SIGNAL_DICT)
    pulse_transformed = transform(pulse)
    # fs.save(pulse_transformed)

# Data/metadata submission - S3 API (data output dir -> remote S3) + InvenioRDM API (metadata output dir -> InvenioRDM record)
if os.environ['MODE'] == 'production': # Only upload data / metadata in production env
    s3.upload_outputs()
    invenio.submit_record()

print('Hello world!') # Sanity check
