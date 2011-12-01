from django.http import HttpResponse
import neo4jrestclient.client as neo4j
#from neo4j import GraphDatabase
import simplejson

from settings import NEO4J_RESOURCE
from apps.report.models import UserFile

class FordropGraphClient():
    def __init__(self):
        self.graphdb = neo4j.GraphDatabase(NEO4J_RESOURCE)

    def add_node(self, request, obj, type):
        node = None
        if not obj.graph_id:
            if type == 'file':
                user_file = UserFile.objects.filter(file=obj, user=request.user)[0]
                node = self.graphdb.nodes.create(name=user_file.filename, type='report', web_id=obj.id)
            if type == 'person':
                node = self.graphdb.nodes.create(name=obj.user.get_full_name(), type='person')
            if type == 'investigation':
                node = self.graphdb.nodes.create(name=obj.title, type='investigation')
            if type == 'reference':
                node = self.graphdb.nodes.create(name=obj.name, type='reference')
            obj.graph_id = node.id
            obj.save()
        else:
            node = self.graphdb.nodes.get(obj.graph_id)
        return node

    def add_relationship(self, node1, node2, type):
        n1 = self.graphdb.nodes.get(node1)
        n2 = self.graphdb.nodes.get(node2)
        self.graphdb.relationships.create(n1, type, n2)
        return True

    def gen_arbor_json(self, graph_id):
        node_color = {
            'investigation':    'orange',
            'person':           'green',
            'report':           'grey'
        }
        ref_node = self.graphdb.nodes.get(graph_id)
        nodes, edges, e = {}, {}, {}
        nodes[ref_node.properties['name']] = {'color':node_color[ref_node.properties['type']],'label':ref_node.properties['name'], 'id':ref_node.id}
        for node in ref_node.traverse(stop="1", returns=neo4j.NODE):
            nodes[node.properties['name']] = {'color':node_color[node.properties['type']],'label':node.properties['name'], 'id':node.id}
        for rel in ref_node.relationships.all():
            e[rel.start.properties['name']] = {'label': rel.type, 'directed':True}
            e[rel.end.properties['name']] = {'label': rel.type, 'directed':True}
            edges[ref_node.properties['name']] = e
        d = {'nodes': nodes, 'edges': edges}
        return HttpResponse(simplejson.dumps(d))

    def get_related(self, graph_id):
        ref_node = self.graphdb.nodes.get(graph_id)
        nodes = {}
        for node in ref_node.traverse(stop="none", returns=neo4j.NODE):
            nodes[node.properties['name']] = {'label':node.properties['name'], 'id':node.id, 'type':node.properties['type']}
        d = {'nodes': nodes}
        return HttpResponse(simplejson.dumps(d))

    def get_related2(self, graph_id):
        ref_node = self.graphdb.nodes.get(graph_id)
        nodes = {}
        for node in ref_node.traverse(stop="none", returns=neo4j.NODE):
            try:
                web_id = node.properties['web_id']
            except KeyError:
                web_id = None
            nodes[node.properties['name']] = {'label':node.properties['name'], 'id':node.id, 'web_id':web_id, 'type':node.properties['type']}
        d = {'nodes': nodes}
        return simplejson.dumps(d)

