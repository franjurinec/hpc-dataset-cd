import os
import json
import urllib
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

INVENIO_RDM_URL = os.getenv("INVENIO_RDM_URL")
INVENIO_RDM_KEY = os.getenv("INVENIO_RDM_KEY")
AUTH_HEADERS = {"Authorization": f"Bearer {INVENIO_RDM_KEY}"}

def create_draft(record_data):
    response = requests.post(
        urllib.parse.urljoin(INVENIO_RDM_URL, "/api/records"),
        json=record_data,
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


def create_new_version(record_id):
    response = requests.post(
        urllib.parse.urljoin(INVENIO_RDM_URL, f"/api/records/{record_id}/versions"),
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


def update_draft(record_id, record_data):
    response = requests.put(
        urllib.parse.urljoin(INVENIO_RDM_URL, f"/api/records/{record_id}/draft"),
        json=record_data,
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


def start_file_uploads(record_id, filenames):
    response = requests.post(
        urllib.parse.urljoin(INVENIO_RDM_URL, f"/api/records/{record_id}/draft/files"),
        json=[{"key": filename} for filename in filenames],
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


def upload_file_contents(record_id, filename, content):
    headers = AUTH_HEADERS
    headers["Content-Type"] = "application/octet-stream"
    response = requests.put(
        urllib.parse.urljoin(
            INVENIO_RDM_URL, f"/api/records/{record_id}/draft/files/{filename}/content"
        ),
        data=content,
        headers=headers,
        timeout=3000,
    )
    return response.json()


def complete_file_upload(record_id, filename):
    response = requests.post(
        urllib.parse.urljoin(
            INVENIO_RDM_URL, f"/api/records/{record_id}/draft/files/{filename}/commit"
        ),
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


def publish_draft(record_id):
    response = requests.post(
        urllib.parse.urljoin(
            INVENIO_RDM_URL, f"/api/records/{record_id}/draft/actions/publish"
        ),
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


def get_draft(record_id):
    response = requests.get(
        urllib.parse.urljoin(INVENIO_RDM_URL, f"/api/records/{record_id}/draft"),
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


def get_latest_version(record_id):
    response = requests.get(
        urllib.parse.urljoin(
            INVENIO_RDM_URL, f"/api/records/{record_id}/versions/latest"
        ),
        headers=AUTH_HEADERS,
        timeout=3000,
    )
    return response.json()


# Custom Functions
def get_or_create_new_draft(record_id):
    draft = get_draft(record_id)
    if draft["status"] == 404:
        draft = create_new_version(record_id)
    return draft


def upload_metadata_as_json(record_id, metadata, filename="METADATA.json"):
    start_file_uploads(record_id, [filename])
    upload_file_contents(record_id, filename, json.dumps(metadata).encode("utf-8"))
    return complete_file_upload(record_id, filename)


def create_demo_record():
    basic_info = {"author_name": "Fran", "author_surname": "Jurinec"}
    record_data = {
        "access": {"record": "public", "files": "public"},
        "files": {"enabled": False},
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": basic_info["author_surname"],
                        "given_name": basic_info["author_name"],
                        "type": "personal",
                    },
                },
            ],
            "resource_type": {"id": "dataset"},
            "title": "Sample Automated Record",
        },
    }

    draft = create_draft(record_data)
    return publish_draft(draft["id"])
