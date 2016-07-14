#!/usr/bin/python

import midi
import rdflib
from rdflib import Namespace, Graph, RDF, URIRef, Literal
import sys
from werkzeug.urls import url_fix

if len(sys.argv) != 3:
    print "Usage: {0} <midi input file> <rdf output file>".format(sys.argv[0])
    exit(2)

filename = sys.argv[1]

# Read the input MIDI file
pattern_midi = midi.read_midifile(filename)

mid = Namespace("http://example.org/midi/")
m = Namespace(url_fix("http://example.org/midi/" + "".join(filename.split('.')[0:-1])))

# Create the graph
g = Graph()

pattern = mid[filename.split('.')[0]]
g.add((pattern, RDF.type, mid.Pattern))
g.add((pattern, mid.resolution, Literal(pattern_midi.resolution)))
g.add((pattern, mid['format'], Literal(pattern_midi.format)))

# Since we won't mess with RDF statement order, we'll have absolute ticks
# pattern_midi.make_ticks_abs()

for n_track in range(len(pattern_midi)):
    track = m['track' + str(n_track).zfill(2)] #So we can order by URI later -- UGLY PATCH
    g.add((track, RDF.type, mid.Track))
    g.add((pattern, mid.hasTrack, track))
    for n_event in range(len(pattern_midi[n_track])):
        event_midi = pattern_midi[n_track][n_event]
        event = m['track' + str(n_track).zfill(2) + '/event'+ str(n_event).zfill(4)]
        g.add((event, RDF.type, mid[(type(event_midi).__name__)]))
        g.add((track, mid.hasEvent, event))
        # Save the 'tick' slot (shared among all events)
        g.add((event, mid.tick, Literal(event_midi.tick)))
        # Save the 'channel' slot
        if hasattr(event_midi, 'channel'):
            g.add((event, mid.channel, Literal(event_midi.channel)))
        # Save any other slots the event may have
        for slot in event_midi.__slots__:
            g.add((event, mid[slot], Literal(getattr(event_midi, slot))))

g.bind('mid', mid)

outfile = open(sys.argv[2], 'w')
outfile.write(g.serialize(format='turtle'))
outfile.close()

exit(0)