import midi
import rdflib
from rdflib import Namespace, Graph, RDF, URIRef, Literal

mid = Namespace("http://example.org/midi/")

# Read the input RDF file
g = Graph()
g.parse("ghostbusters.ttl", format="turtle")

# Initialize the MIDI file
pattern = midi.Pattern()

# Retrieve the tracks
for s,p,o in g.triples((None, RDF.type, mid.Track)):
    track = midi.Track()
    pattern.append(track)
    # Retrieve all events on this track
    for x,y,z in g.triples((s, mid.hasEvent, None)):
        event_type = g.objects(z, RDF.type)
        if event_type == mid.NoteOnEvent:
            tick = None
            velocity = None
            pitch = None
            for p in g.objects(z, mid.tick):
                tick = int(p)
            for p in g.objects(z, mid.velocity):
                velocity = int(p)
            for p in g.objects(z, mid.pitch ):
                pitch = int(p)
            on = midi.NoteOnEvent(tick=tick, velocity=velocity, pitch=pitch)
            track.append(on)
        elif event_type == mid.NoteOffEvent:
            tick = None
            pitch = None
            for p in g.objects(z, mid.tick):
                tick = int(p)
            for p in g.objects(z, mid.pitch ):
                pitch = int(p)
            off = midi.NoteOffEvent(tick=tick, pitch=pitch)
            track.append(off)
        elif event_type == mid.EndOfTrackEvent:
            tick = None
            for p in g.objects(z, mid.tick):
                tick = int(p)
            eot = midi.EndOfTrackEvent(tick=tick)
            track.append(eot)
        else
            print "BIG ERROR, EVENT TYPE UNMANAGED"

midi.write_midifile("ghostbusters_roundtrip.mid", pattern)
