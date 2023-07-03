const INVENIO_API_URL = process.env.INVENIO_API_URL
const INVENIO_API_KEY = process.env.INVENIO_API_KEY
const ROOT_RECORD = process.env.ROOT_RECORD

const authHeaders = {
    Authorization: `Bearer ${INVENIO_API_KEY}`
}

// Get or create new draft from root record
const draft = fetch(new URL(`/api/records/${ROOT_RECORD}/draft`, INVENIO_API_URL), {
    headers: authHeaders
}).then(res => res.json())
if (draft.status === 404)
    draft = fetch(new URL(`/api/records/${ROOT_RECORD}/versions`, INVENIO_API_URL), {
        headers: authHeaders,
        method: 'POST'
    }).then(res => res.json())

// Update record using metadata
// TODO

// Upload metadata JSON file
// TODO

// Publish Record
// TODO
