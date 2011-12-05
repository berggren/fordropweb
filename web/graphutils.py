import json
from neo4j import GraphDatabase
from settings import NEO4J_RESOURCE
from apps.report.models import UserFile

def add_node(db, request, obj, type):
    node = None
    if not obj.graph_id:
        if type == 'file':
            user_file = UserFile.objects.filter(file=obj, user=request.user)[0]
            with db.transaction:
                node = db.node(name=user_file.filename, type='report', web_id=obj.id)
        if type == 'person':
            with db.transaction:
                node = db.node(name=obj.user.get_full_name(), type='person')
        if type == 'investigation':
            with db.transaction:
                node = db.node(name=obj.title, type='investigation')
        if type == 'reference':
            with db.transaction:
                node = db.node(name=obj.name, type='reference')
        obj.graph_id = node.id
        obj.save()
    else:
        node = db.node[int(obj.graph_id)]
    return node

def add_relationship(db, node1, node2, type):
    with db.transaction:
        n1 = db.node[int(node1)]
        n2 = db.node[int(node2)]
        n1.relationships.create(type, n2)
    return True

def gen_arbor_json(db):
    print db
    return

def get_related2(db, graph_id):
    ref_node = db.node[int(graph_id)]
    nodes = {}
    traverse = db.traversal().relationships('created').traverse(ref_node)
    for node in traverse.nodes:
        print node
        try:
            web_id = node['web_id']
        except KeyError:
            web_id = None
        nodes[node['name']] = {'label':node['name'], 'id':node.id, 'web_id':web_id, 'type':node['type']}
        d = {'nodes': nodes}
        print json.dumps(d, indent=4)
    return json.dumps(d)

def open_db(uri=NEO4J_RESOURCE):
    return GraphDatabase(uri)

try:
    neo4jdb = open_db()
except Exception as e:
    print e

def _close_db():
    try:
        neo4jdb.shutdown()
    except NameError:
        print 'Could not shutdown Neo4j database. Is it open in another process?'

import atexit
atexit.register(_close_db)