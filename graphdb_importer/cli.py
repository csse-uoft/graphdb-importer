import argparse
import os
import sys

from .utils.grapgdb import import_and_wait, set_config


class BooleanAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        is_true = values == '1' or values == 'true' or values == 'True'
        setattr(namespace, self.dest, is_true)


my_parser = argparse.ArgumentParser(description='GraphDB Importer')

my_parser.add_argument('FILE',
                       type=str,
                       help='The file you want to import. File format supported:'
                            '.ttl.gz, .ttls.gz, .rdf.gz, .rj.gz, .n3.gz, .nt.gz, .nq.gz, .trig.gz, .trigs.gz, .trix.gz,'
                            '.brf.gz, .owl.gz, .jsonld.gz, .ttl, .ttls, .rdf, .rj, .n3, .nt, .nq, .trig, .trigs, '
                            '.trix, .brf, .owl, .jsonld, .zip')

my_parser.add_argument('-s', '--base-api',
                       type=str,
                       default=os.getenv('GDB_BASE_API'),
                       required=True,
                       dest='base_api',
                       help='The GraphDB server API. i.e. http://1.2.3.4:7200')

my_parser.add_argument('-r', '--repository',
                       type=str,
                       default=os.getenv('GDB_REPOSITORY'),
                       required=True,
                       dest='repo',
                       help='The repository you want to import into. The repository must exists on the GraphDB server.')

my_parser.add_argument('-u', '--username',
                       type=str,
                       dest='username',
                       default=os.getenv('GDB_USERNAME'),
                       help='GraphDB username.')

my_parser.add_argument('-p', '--password',
                       type=str,
                       dest='password',
                       default=os.getenv('GDB_PASSWORD'),
                       help='GraphDB password.')

my_parser.add_argument('-g', '--named-graph',
                       type=str,
                       dest='named_graph',
                       default=os.getenv('GDB_NAMED_GRAPH'),
                       help='Import to a specific named graph.'
                            ' If not specified, default graph/graphs defined in the file is used.'
                            ' If you want to import to the default graph (ignore the graphs defined in the file), set this to "default".')

my_parser.add_argument('-R', '--replace-graph',
                       dest='replace',
                       default=True,
                       choices=["0", "1", "true", "false", "True", "False"],
                       action=BooleanAction,
                       help='Delete the existing graph and import new data. (default: true)')

my_parser.add_argument('-d', '--remove-upload',
                       dest='remove_upload',
                       default=True,
                       choices=["0", "1", "true", "false", "True", "False"],
                       action=BooleanAction,
                       help='Delete the upload from the GraphDB server after import completed. (default: true)')

my_parser.add_argument('-pb', '--preserve-bnode',
                       dest='preserve_bnode',
                       default=False,
                       choices=["0", "1", "true", "false", "True", "False"],
                       action=BooleanAction,
                       help='Preserve blank node IDs. '
                            'This is helpful when you want to import a splitted ontology.'
                            ' (default false)')

args = my_parser.parse_args()

if not os.path.exists(args.FILE):
    print(f'Cannot not find the provided file: {args.FILE}')
    sys.exit(-1)

# print(args)
set_config(base_api=args.base_api, repo=args.repo, username=args.username, password=args.password)
import_and_wait(filename=args.FILE, named_graph=args.named_graph, replace_graph=args.replace,
                preserve_bnode=args.preserve_bnode)
