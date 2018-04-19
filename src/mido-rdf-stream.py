#!/usr/bin/env python

# mido-rdf-stream.py: stream and save MIDI RDF triples

import mido
import uuid
from rdflib import Graph, Namespace, RDF, Literal, URIRef
from datetime import datetime
import time
import sys

# initialize rdf graph
g = Graph()
# Namespaces
midi_r = Namespace("http://purl.org/midi-ld/")
midi = Namespace("http://purl.org/midi-ld/midi#")
prov = Namespace("http://www.w3.org/ns/prov#")

g.bind('midi-r', midi_r)
g.bind('midi', midi)
g.bind('prov', prov)

# Initialize pattern, track and event IDs
pattern_id = uuid.uuid4()
track_id = 0
event_id = 0

# time counter
start_time = time.time()

# Initialize the MIDI graph
piece = midi_r['pattern/' + str(pattern_id)]
g.add((piece, RDF.type, midi.Piece))
g.add((piece, midi.resolution, Literal(460)))
g.add((piece, midi['format'], Literal(1)))

# We'll set a single track (TODO: support more)
track = URIRef(piece + '/track' + str(track_id).zfill(2))
g.add((track, RDF.type, midi.Track))
g.add((piece, midi.hasTrack, track))

# Testing graph init stuff
# event_uri = midi_r["pattern/" + str(pattern_id) + "/" + 'track' + str(track_id).zfill(2) + '/event' + str(0).zfill(2)]
# g.add((track, midi.hasEvent, event_uri))
# g.add((event_uri, RDF.type, midi.SetTempoEvent))
# g.add((event_uri, midi.bpm, Literal(8.300007e+01)))
# g.add((event_uri, midi.mpqn, Literal(722891)))
# g.add((event_uri, midi.tick, Literal(0)))
#
# event_uri = midi_r["pattern/" + str(pattern_id) + "/" + 'track' + str(track_id).zfill(2) + '/event' + str(1).zfill(2)]
# g.add((track, midi.hasEvent, event_uri))
# g.add((event_uri, RDF.type, midi.TimeSignatureEvent))
# g.add((event_uri, midi.denominator, Literal(4)))
# g.add((event_uri, midi.metronome, Literal(96)))
# g.add((event_uri, midi.numerator, Literal(4)))
# g.add((event_uri, midi.thirtyseconds, Literal(8)))
# g.add((event_uri, midi.tick, Literal(0)))
#
# event_uri = midi_r["pattern/" + str(pattern_id) + "/" + 'track' + str(track_id).zfill(2) + '/event' + str(2).zfill(2)]
# g.add((track, midi.hasEvent, event_uri))
# g.add((event_uri, RDF.type, midi.ControlChangeEvent))
# g.add((event_uri, midi.channel, Literal(0)))
# g.add((event_uri, midi.control, Literal(101)))
# g.add((event_uri, midi.tick, Literal(0)))
# g.add((event_uri, midi.value, Literal(0)))
#
# event_uri = midi_r["pattern/" + str(pattern_id) + "/" + 'track' + str(track_id).zfill(2) + '/event' + str(3).zfill(2)]
# g.add((track, midi.hasEvent, event_uri))
# g.add((event_uri, RDF.type, midi.ProgramChangeEvent))
# g.add((event_uri, midi.channel, Literal(0)))
# g.add((event_uri, midi.tick, Literal(0)))
# g.add((event_uri, midi.program, URIRef("http://purl.org/midi-ld/programs/74")))

# event_uri = midi_r["pattern/" + str(pattern_id) + "/" + 'track' + str(track_id).zfill(2) + '/event' + str(2).zfill(2)]
# g.add((event_uri, midi.channel, Literal(0)))
# g.add((event_uri, midi.control, Literal(101)))
# g.add((event_uri, midi.tick, Literal(0)))
# g.add((event_uri, midi.value, Literal(0)))
# g.add((event_uri, RDF.type, midi.ControlChangeEvent))
# g.add((track, midi.hasEvent, event_uri))

# PROV info
# g.add((piece, prov.wasDerivedFrom, Literal(filename)))
agent = URIRef("https://github.com/midi-ld/midi2rdf")
entity_d = piece
entity_o = URIRef("http://purl.org/midi-ld/file/{}".format(pattern_id))
activity = URIRef(piece + "-activity")

g.add((agent, RDF.type, prov.Agent))
g.add((entity_d, RDF.type, prov.Entity))
g.add((entity_o, RDF.type, prov.Entity))
g.add((entity_o, RDF.type, midi.MIDIFile))
g.add((entity_o, midi.path, Literal(pattern_id)))
g.add((activity, RDF.type, prov.Activity))
g.add((entity_d, prov.wasGeneratedBy, activity))
g.add((entity_d, prov.wasAttributedTo, agent))
g.add((entity_d, prov.wasDerivedFrom, entity_o))
g.add((activity, prov.wasAssociatedWith, agent))
g.add((activity, prov.startedAtTime, Literal(datetime.now())))
g.add((activity, prov.used, entity_o))

print g.serialize(format='nt')

try:
    with mido.open_input(u'VMini:VMini MIDI 1 20:0') as port:
        for msg in port:
            sg = Graph()
            status = None
            if msg.type == "note_on":
                status = "NoteOnEvent"
            elif msg.type == "note_off":
                status = "NoteOffEvent"
            else:
                print "BIG ERROR, unexpected event type {}".format(msg.type)
            pitch = msg.bytes()[1]
            velocity = msg.bytes()[2]
            channel = 0
            #print status, pitch, velocity, channel, timestamp
            # Creating triples!
            event_uri = midi_r["pattern/" + str(pattern_id) + "/" + 'track' + str(track_id).zfill(2) + '/event' + str(event_id).zfill(4)]
            sg.add((track, midi.hasEvent, event_uri))
            sg.add((event_uri, RDF.type, midi[status]))
            sg.add((event_uri, midi.tick, Literal(int((time.time() - start_time)*1000))))
            start_time = time.time()
            sg.add((event_uri, midi.channel, Literal(channel)))
            sg.add((event_uri, midi.note, URIRef('http://purl.org/midi-ld/notes/{}'.format(pitch))))
            sg.add((event_uri, midi.velocity, Literal(velocity)))

            print sg.serialize(format='nt')

            # Merge sg with main graph
            g = g + sg

            event_id += 1
except KeyboardInterrupt:
    # Add end of track event
    event_id += 1
    event_uri = midi_r["pattern/" + str(pattern_id) + "/" + 'track' + str(track_id).zfill(2) + '/event' + str(event_id).zfill(4)]
    eg = Graph()
    eg.add((track, midi.hasEvent, event_uri))
    eg.add((event_uri, RDF.type, midi.EndOfTrackEvent))
    eg.add((event_uri, midi.tick, Literal(0)))

    print eg.serialize(format='nt')

    g = g + eg

    sys.stderr.write(piece)
    sys.stderr.write('\n')

    exit(0)

    # print "Here is your RDF graph!"
    # print len(g)
    # for s,p,o in g.triples((None, None, None)):
    #     print s,p,o
    # with open('out.ttl', 'w') as outfile:
    #     outfile.write(g.serialize(format='turtle'))
