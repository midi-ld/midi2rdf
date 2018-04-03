#!/usr/bin/env python

import mido
import uuid
from rdflib import Graph, Namespace, RDF, Literal

# initialize rdf graph
g = Graph()
# Namespaces
mid = Namespace("http://example.org/midi/")
pattern_id = uuid.uuid4()
m = Namespace("http://example.org/midi/" + str(pattern_id) + "/")

g.bind('mid', mid)

with mido.open_input(u'VMini:VMini MIDI 1 20:0') as port:
    for msg in port:
        status = None
        if msg.type == "note_on":
            status = "NoteOn"
        elif msg.type == "note_off":
            status = "NoteOff"
        else:
            print "BIG ERROR, unexpected event type {}".format(msg.type)
        pitch = msg.bytes()[1]
        velocity = msg.bytes()[2]
        channel = 0
        #print status, pitch, velocity, channel, timestamp
        # Creating triples!
        track_id = uuid.uuid4()
        event = m['track' + str(track_id) + '/event' + str(uuid.uuid4())]
        g.add((event, RDF.type, mid[status]))
        g.add((event, mid.tick, Literal(msg.time)))
        g.add((event, mid.channel, Literal(channel)))
        g.add((event, mid.pitch, Literal(pitch)))
        g.add((event, mid.velocity, Literal(velocity)))
        for s,p,o in g.triples((None, None, None)):
            print g.qname(s),g.qname(p),o,'.'
        g = Graph()
