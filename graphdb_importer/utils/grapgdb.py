import json
import math
import re
import time

import requests
from requests_toolbelt import MultipartEncoder

GraphDB_BASE_API = None
REPOSITORY = None
USERNAME = None
PASSWORD = None


def set_config(base_api: str, repo, username=None, password=None):
    global GraphDB_BASE_API, REPOSITORY, USERNAME, PASSWORD

    if base_api.endswith('/'):
        base_api = base_api[:-1]
    GraphDB_BASE_API = base_api
    REPOSITORY = repo
    USERNAME = username
    PASSWORD = password


def get_gdb_token(username, password):
    """
    Return a GDB token.
    Used in headers: `Authorization: gdb_token`
    """
    result = requests.post(f'{GraphDB_BASE_API}/rest/login/{username}',
                           headers={'X-GraphDB-Password': password})

    if result.status_code != 200:
        raise ValueError('Wrong username/password')

    return result.headers['Authorization']


def upload_file(file_location: str, import_name=None, gdb_token=None):
    """
    Import a file, this should support all RDF types that GraphDB supports:
    .ttl.gz, .ttls.gz, .rdf.gz, .rj.gz, .n3.gz, .nt.gz, .nq.gz, .trig.gz, .trigs.gz, .trix.gz, .brf.gz,
    .owl.gz, .jsonld.gz, .ttl, .ttls, .rdf, .rj, .n3, .nt, .nq, .trig, .trigs, .trix, .brf, .owl, .jsonld, .zip

    The file is imported through
    """
    file = open(file_location, "rb")
    filename = re.sub(r'\\', '/', file_location).split('/')[-1]
    import_name = import_name or filename

    import_settings = {"name": import_name,
                       "status": "NONE",
                       "message": "",
                       "context": None,
                       "replaceGraphs": [],
                       "baseURI": None,
                       "forceSerial": False,
                       "type": None,
                       "format": None,
                       "data": None,
                       "timestamp": math.trunc(time.time() * 1000),
                       "parserSettings": {"preserveBNodeIds": False, "failOnUnknownDataTypes": False,
                                          "verifyDataTypeValues": False, "normalizeDataTypeValues": False,
                                          "failOnUnknownLanguageTags": False, "verifyLanguageTags": True,
                                          "normalizeLanguageTags": False, "stopOnError": True},
                       "requestIdHeadersToForward": None}

    # Stream the file upload instead of load the whole file into memory
    # https://toolbelt.readthedocs.io/en/latest/uploading-data.html#streaming-multipart-data-encoder
    data = MultipartEncoder(
        fields={'file': (filename, file, 'application/octet-stream'),
                'importSettings': ('blob', json.dumps(import_settings), 'application/json')}
    )

    # headers = {'Accept': 'application/json, text/plain, */*', 'Content-Type': 'application/json'}
    headers = {'Content-Type': data.content_type}
    if gdb_token:
        headers['Authorization'] = gdb_token

    result = requests.post(f'{GraphDB_BASE_API}/rest/repositories/{REPOSITORY}/import/upload/update/file',
                           data=data, headers=headers)

    # print(result.text)

    if result.status_code != 200 and result.status_code != 202:
        raise ValueError(f"Failed to upload file {filename}: {result.text}")

    file.close()
    return import_name


def import_uploaded_file(import_name: str, named_graph: str = None, replace_graph=True, preserve_bnode=False,
                         gdb_token=None):
    """
    Default graph is used when named_graph is None.
    Set replace_graph to true if you want to replace it.
    """
    settings_replace_graphs = []
    if replace_graph and named_graph:
        settings_replace_graphs = [named_graph]
    elif replace_graph and named_graph is None:
        settings_replace_graphs = ['default']

    import_settings = {"name": import_name,
                       "status": "NONE",
                       "message": "",
                       "context": named_graph or '',
                       "replaceGraphs": settings_replace_graphs,
                       "baseURI": None,
                       "forceSerial": False,
                       "type": "file",
                       "format": None,
                       "data": None,
                       "timestamp": math.trunc(time.time() * 1000),
                       "parserSettings": {"preserveBNodeIds": preserve_bnode, "failOnUnknownDataTypes": False,
                                          "verifyDataTypeValues": False, "normalizeDataTypeValues": False,
                                          "failOnUnknownLanguageTags": False, "verifyLanguageTags": True,
                                          "normalizeLanguageTags": False, "stopOnError": True},
                       "requestIdHeadersToForward": None}

    data = MultipartEncoder(
        fields={'importSettings': ('blob', json.dumps(import_settings), 'application/json')}
    )

    headers = {'Content-Type': data.content_type}
    if gdb_token:
        headers['Authorization'] = gdb_token

    result = requests.post(f'{GraphDB_BASE_API}/rest/repositories/{REPOSITORY}/import/upload/file', headers=headers,
                           data=data)

    if result.status_code != 200 and result.status_code != 202:
        raise ValueError(f"Failed to import file: {import_name} {result.text}")


def check_status(name, gdb_token=None):
    """
    Check import status, return True if import is done, False if in progress.
    Raise an error if import is failed or the import does not exist.
    :param gdb_token:
    :param name: import name
    :return: 'DONE' if import is done
    """
    headers = {'Accept': 'application/json, text/plain, */*', 'X-GraphDB-Repository': REPOSITORY}
    if gdb_token:
        headers['Authorization'] = gdb_token
    result = requests.get(GraphDB_BASE_API + f'/rest/repositories/{REPOSITORY}/import/upload/', headers=headers)
    result = result.json()

    matched_imported_item = None
    for imported_item in result:
        if imported_item['name'] == name:
            matched_imported_item = imported_item

    if matched_imported_item['status'] == 'DONE':
        return True
    elif matched_imported_item['status'] == 'ERROR':
        raise ValueError('Import failed: ' + matched_imported_item['message'])
    elif matched_imported_item['status'] == 'IMPORTING':
        return False
    else:
        raise ValueError('Cannot find the import: ' + name)


def delete_import(name, gdb_token=None):
    headers = {'Accept': 'application/json, text/plain, */*', 'X-GraphDB-Repository': REPOSITORY}
    if gdb_token:
        headers['Authorization'] = gdb_token

    body = [name]
    result = requests.delete(GraphDB_BASE_API + f'/rest/repositories/{REPOSITORY}/import/upload/status?remove=true',
                             headers=headers, json=body)

    if result.status_code != 200:
        raise ValueError("Failed to remove import history: " + name)


def import_and_wait(filename, named_graph: str = None, replace_graph=True, remove_upload_after_import=True,
                    preserve_bnode=False):
    if USERNAME and PASSWORD:
        gdb_token = get_gdb_token(USERNAME, PASSWORD)
        print('Authenticated.')
    else:
        gdb_token = None
    print('File uploading...')
    import_name = upload_file(filename, gdb_token=gdb_token)
    print('File uploaded, importing...')

    import_uploaded_file(import_name, named_graph, replace_graph, preserve_bnode, gdb_token=gdb_token)

    time.sleep(0.1)
    while not check_status(import_name, gdb_token):
        time.sleep(1)

    if remove_upload_after_import:
        delete_import(import_name, gdb_token)
        print('File deleted from server.')
    print('Done')
    return True
