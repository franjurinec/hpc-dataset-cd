import os
import s3fs

def upload_outputs(local_path, s3_path):
    fs = s3fs.S3FileSystem(
        key=os.environ['S3_KEY'],
        secret=os.environ['S3_PASS'],
        client_kwargs={
            'endpoint_url': os.environ['S3_ENDPOINT']
        }
    )
    fs.put(local_path, s3_path, recursive=True)