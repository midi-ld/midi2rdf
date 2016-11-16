#!/usr/bin/python

import rdflib
from rdflib import Graph
import gzip

if len(sys.argv) != 2:
    print "Usage: {0} <midi rdf file>".format(sys.argv[0])
    exit(2)

g = Graph(sys.argv[1])
qres = g.query("prefix mid: <http://example.org/midi/> prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> select ?label where {?e a mid:TextMetaEvent . ?e rdfs:label ?label}")
for row in qres:
    print row

exit(0)
