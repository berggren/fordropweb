import json
from django.http import HttpResponse
from neo4j import GraphDatabase
from settings import NEO4J_RESOURCE

def add_node(db, request, obj, type):
    node = None
    if not obj.graph_id:
        if type == 'file':
            with db.transaction:
                if obj.filename != "":
                    node = db.node(name=obj.filename, type='report', web_id=obj.id)
                else:
                    node = db.node(name=obj.md5, type='report', web_id=obj.id)
        if type == 'person':
            with db.transaction:
                node = db.node(name=obj.user.username, type='person', web_id=obj.user.id)
        if type == 'investigation':
            with db.transaction:
                node = db.node(name=obj.title, type='investigation', web_id=obj.id)
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

def arbor(db, graph_id):
    node_color = {
        'investigation':    'orange',
        'person':           'green',
        'report':           'grey'
    }
    ref_node = db.node[int(graph_id)]
    nodes, edges, e = {}, {}, {}
    nodes[ref_node['name']] = {'color':node_color[ref_node['type']],'label':ref_node['name'], 'id':ref_node.id}
    for rel in ref_node.relationships:
        nodes[rel.start['name']] = {'color':node_color[rel.start['type']],'label':rel.start['name'], 'id':rel.start.id}
        nodes[rel.end['name']] = {'color':node_color[rel.end['type']],'label':rel.end['name'], 'id':rel.end.id}
        e[rel.end['name']] = {'label': rel.type.toString(), 'directed':True}
        edges[rel.start['name']] = e
    d = {'nodes': nodes, 'edges': edges}
    return HttpResponse(json.dumps(d))


def get_related(db, graph_id):
    ref_node = db.node[int(graph_id)]
    nodes = {}
    traverse = db.traversal().relationships('created').relationships('reported').traverse(ref_node)
    for node in traverse.nodes:
        if node == ref_node:
            continue
        try:
            web_id = node['web_id']
        except KeyError:
            web_id = None
        nodes[node['name']] = {'label':node['name'], 'id':node.id, 'web_id':web_id, 'type':node['type']}
        d = {'nodes': nodes}
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
