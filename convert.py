import midi
import rdflib
from rdflib import Namespace, Graph, RDF, URIRef, Literal

filename = "ghostbusters.mid"

# Read the input MIDI file
pattern_midi = midi.read_midifile(filename)

mid = Namespace("http://example.org/midi/")
m = Namespace("http://example.org/midi/ghostbusters/")

# Create the graph
g = Graph()

pattern = mid[filename.split('.')[0]]
g.add((pattern, RDF.type, mid.Pattern))

# Since we won't mess with RDF statement order, we'll have absolute ticks
# pattern_midi.make_ticks_abs()

for n_track in range(len(pattern_midi)):
    track = m['track' + str(n_track).zfill(2)] #So we can order by URI later
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
print g.serialize(format='turtle')

exit(0)
