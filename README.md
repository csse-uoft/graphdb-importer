## GraphDB Importer
### Install
```shell
pip install git+https://github.com/csse-uoft/graphdb-importer
```

### API

#### set_config
Configure the GraphDB server api and specify which repository to use.
```
set_config(base_api: str, repo: str, username=None, password=None)
```
#### import_and_wait
Import a given file and wait for it.

```
import_and_wait(filename: str, named_graph: str = None, replace_graph=True, remove_upload_after_import=True, preserve_bnode=False)
```


### Example
> See [`example.py`](./example.py)

```shell
from graphdb_importer import import_and_wait, set_config

owl_file_path = f"{dir_path}/some-file.owl"
base_api = 'http://graphdb-ip:7200'

set_config(base_api=base_api, repo='repo-name', username='admin', password='admin')
import_owl_and_wait(filename=dir_path, replace_graph=True)
```


------
### CLI Usage
```shell
$ graphdb-importer -h

usage: cli.py [-h] -s BASE_API -r REPO [-u USERNAME] [-p PASSWORD] [-g NAMED_GRAPH] [-R REPLACE] [-d REMOVE_UPLOAD]
              [-pb PRESERVE_BNODE]
              FILE

GraphDB Importer

positional arguments:
  FILE                  The file you want to import. File format supported:.ttl.gz, .ttls.gz, .rdf.gz, .rj.gz, .n3.gz, .nt.gz,
                        .nq.gz, .trig.gz, .trigs.gz, .trix.gz,.brf.gz, .owl.gz, .jsonld.gz, .ttl, .ttls, .rdf, .rj, .n3, .nt, .nq,
                        .trig, .trigs, .trix, .brf, .owl, .jsonld, .zip

optional arguments:
  -h, --help            show this help message and exit
  -s BASE_API, --base-api BASE_API
                        The GraphDB server API. i.e. http://1.2.3.4:7200
  -r REPO, --repository REPO
                        The repository you want to import into. The repository must exists on the GraphDB server.
  -u USERNAME, --username USERNAME
                        GraphDB username.
  -p PASSWORD, --password PASSWORD
                        GraphDB password.
  -g NAMED_GRAPH, --named-graph NAMED_GRAPH
                        Import to a specific named graph. If not specified, default graph/graphs defined in the file is used. 
                        If you want to import to the default graph (ignore the graphs defined in the file), set this to "default".
  -R {0,1,true,false,True,False}, --replace-graph {0,1,true,false,True,False}
                        Delete the existing graph and import new data. (default: true)
  -d {0,1,true,false,True,False}, --remove-upload {0,1,true,false,True,False}
                        Delete the upload from the GraphDB server after import completed. (default: true)
  -pb {0,1,true,false,True,False}, --preserve-bnode {0,1,true,false,True,False}
                        Preserve blank node IDs. This is helpful when you want to import a splitted ontology. (default false)
```

### CLI Example
```shell
$ graphdb-importer knowledge_graph_listing1.owl -s "http://1.2.3.4:7200" -r some-repo-name -u admin -p admin

Authenticated.
File uploading...
File uploaded, importing...
File deleted from server.
Done
```

----
### Install for Development
```shell
pip install -e .
```