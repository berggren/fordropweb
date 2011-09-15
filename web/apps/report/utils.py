import hashlib
import magic
import tempfile
import datetime
import os
import sys
import shutil
import pefile
from dns import message, query
from dns.exception import DNSException
from datetime import datetime
from settings import FD_FILEBASEPATH

def handle_uploaded_file(f):
    # Check filesize, if >20MB return
    #if f.size > 20971520:
    #    return None
    # Setup dstdir
    dt = datetime.now().strftime("%Y%m")
    path = FD_FILEBASEPATH+"/"+dt
    if not os.path.exists(path):
        os.makedirs(path)
        os.chmod(path, 0757)
    tmpfile = tempfile.mkstemp(dir=path)
    fh = open(tmpfile[1], "w")
    for chunk in f.chunks():
        fh.write(chunk)
    fh.close()
    fh = open(fh.name, 'rb')
    fileread = fh.read()
    md5 = hashlib.md5(fileread).hexdigest()
    sha1 = hashlib.sha1(fileread).hexdigest()
    sha256 = hashlib.sha256(fileread).hexdigest()
    filetype = get_filetype(fh.name)
    filepath = path+"/"+sha1+".file"
    if not os.path.exists(filepath):
        shutil.move(fh.name, filepath)
        fh.close()
    else:
        fh.close()
        os.unlink(fh.name)
    try:
        stringspath = get_strings(filepath, sha1, path)
    except: pass
    try:
        get_pefile(filepath, sha1, path)
    except: pass
    d = {'filesize': f.size, 'filename': f.name, 'md5': md5, 'sha1': sha1, 'sha256': sha256, 'filetype': filetype, 'datefolder': dt}
    return d

def get_filetype(file):
    if sys.platform == "darwin":
        type = "Magic not supported on MacOSX"
    else:
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        type =  ms.file(file)
    return type

def get_strings(file, sha1, path):
    stringsfile = path+"/"+sha1+".strings"
    if not os.path.exists(stringsfile):
        cmd = "/usr/bin/strings %s" % file
        fh = open(stringsfile, "w")
        for line in os.popen(cmd).read():
            fh.write(line)
        fh.close()
    return stringsfile

def get_pefile(file, sha1, path):
    outfile = path+"/"+sha1+".pedump"
    if not os.path.exists(outfile):
        try:
            pe = pefile.PE(file)
        except: return None
        pe_dump_all = pe.dump_info()
        fh = open(outfile, "w")
        fh.write(pe_dump_all)
        fh.close()
    return outfile

def query_mhr(hash):
    query_string = "%s.malware.hash.cymru.com" % hash
    try:
        q = message.make_query(query_string, 'TXT')
        d = query.udp(q, '130.237.72.200', timeout=5)
        if d.answer:
            for n in d.answer:
                result = str(n).split("\"")[1]
                unixtime = result.split()[0]
                percent = result.split()[1]
                dt = datetime.fromtimestamp(float(unixtime))
                return dt, percent
        else:
            return None, None
    except DNSException:
        return None, None

def add_node_to_graph(obj, type):
    import neo4jrestclient.client as neo4j
    graphdb = neo4j.GraphDatabase("http://127.0.0.1:7474/db/data/")
    if not obj.graphid:
        if type == 'file':
            node = graphdb.nodes.create(name=obj.sha256, type='report')
        if type == 'person':
            node = graphdb.nodes.create(name=obj.user.get_full_name(), type='person')
        if type == 'investigation':
            node = graphdb.nodes.create(name=obj.title, type='investigation')
        if type == 'reference':
            node = graphdb.nodes.create(name=obj.name, type='reference')
        obj.graphid = node.id
        obj.save()
    else:
        node = graphdb.nodes.get(obj.graphid)
    return node

def add_relationship_to_graph(node1, node2, type):
    import neo4jrestclient.client as neo4j
    graphdb = neo4j.GraphDatabase("http://127.0.0.1:7474/db/data/")
    n1 = graphdb.nodes.get(node1)
    n2 = graphdb.nodes.get(node2)
    try:
        graphdb.relationships.create(n1, type, n2)
    except: return False
    return True

def add_to_graph(hash, reporter):
    import neo4jrestclient.client as neo4j
    graphdb = neo4j.GraphDatabase("http://127.0.0.1:7474/db/data/")
    file_node = graphdb.nodes.create(name=hash, type='report')
    reporter_node = graphdb.nodes.create(name=reporter, type="reporter")
    graphdb.relationships.create(reporter_node, "reported", file_node)
    return file_node.id
