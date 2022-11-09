import os
from graphdb_importer import import_and_wait, set_config

dir_path = os.path.dirname(os.path.realpath(__file__))

owl_file_path = f"{dir_path}/some-file.owl"
base_api = 'http://graphdb-ip:7200'

set_config(base_api=base_api, repo='repo-name', username='admin', password='admin')
import_and_wait(filename=dir_path, replace_graph=True)
