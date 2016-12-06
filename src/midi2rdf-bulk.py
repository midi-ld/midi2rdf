#!/usr/bin/python

import midi
import rdflib
from rdflib import Namespace, ConjunctiveGraph, RDF, RDFS, URIRef, Literal
import sys
from werkzeug.urls import url_fix
import hashlib
import ast
import gzip
import unicodecsv

if len(sys.argv) != 3:
    print "Usage: {0} <midi input file> <rdf output file>".format(sys.argv[0])
    exit(2)

filename = sys.argv[1]

# Read the input MIDI file
pattern_midi = midi.read_midifile(filename)

# Get MD5 to identify the file
md5_id = hashlib.md5(open(filename, 'rb').read()).hexdigest()

mid_uri = URIRef("http://example.org/midi/")
prov_uri = URIRef("http://www.w3.org/ns/prov#")
mid_note_uri = URIRef("http://example.org/midi/notes/")
mid_prog_uri = URIRef("http://example.org/midi/programs/")
# m_uri = URIRef(url_fix("http://example.org/midi/" + "".join(filename.split('.')[0:-1])))
m_uri = URIRef(url_fix("http://example.org/midi/" + str(md5_id) + "/"))
mid = Namespace(mid_uri)
prov = Namespace(prov_uri)
mid_note = Namespace(mid_note_uri)
mid_prog = Namespace(mid_prog_uri)
m = Namespace(m_uri)

# Create the graph
g = ConjunctiveGraph(identifier=m_uri)

# pattern = mid[filename.split('.')[0]]
pattern = mid[md5_id]
g.add((pattern, RDF.type, mid.Pattern))
g.add((pattern, mid.resolution, Literal(pattern_midi.resolution)))
g.add((pattern, mid['format'], Literal(pattern_midi.format)))

# Publication info
# TODO: replace with nanopubs
g.add((pattern, prov.wasDerivedFrom, Literal(filename)))

# Since we won't mess with RDF statement order, we'll have absolute ticks
# pattern_midi.make_ticks_abs()

# We'll append the lyrics in this label
lyrics_label = ""

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
            # Prcoess ASCII conversion of text events
            if type(event_midi).__name__ in ['TrackNameEvent', 'TextMetaEvent', 'LyricsEvent', 'CopyrightMetaEvent', 'MarkerEvent'] and slot == 'data':
                text_data_literal = getattr(event_midi, slot)
                text_value = unicode(''.join(chr(i) for i in text_data_literal), errors='replace')
		# Textfile metadata -- 
		textfile = open('midi-text.csv', 'a')
		writer = unicodecsv.writer(textfile, encoding='utf-8')
		writer.writerow( (filename, type(event_midi).__name__, n_track, n_event, event_midi.tick, text_value) )
		textfile.close()		

                # print text_value
                # text_value = ''.join(chr(i) for i in ast.literal_eval(text_data_literal))
                g.add((event, RDFS.label, Literal(text_value)))
		if type(event_midi).__name__ == 'LyricsEvent':
			lyrics_label += text_value
            elif slot == 'data':
                unknownsfile = open('unknown-types.csv', 'a')
                writer = unicodecsv.writer(unknownsfile, encoding='utf-8')
                writer.writerow( (type(event_midi).__name__, getattr(event_midi, slot)) )
                unknownsfile.close()
            elif type(event_midi).__name__ in ['NoteOnEvent', 'NoteOffEvent'] and slot == 'pitch':
                pitch = str(getattr(event_midi, slot))
                g.add((event, mid['note'], mid_note[pitch]))
            elif type(event_midi).__name__ in ['ProgramChangeEvent'] and slot == 'value':
                program = str(getattr(event_midi, slot))
                g.add((event, mid['program'], mid_prog[program]))

            else:
                g.add((event, mid[slot], Literal(getattr(event_midi, slot))))

# Add the global lyrics link, if lyrics not empty
if lyrics_label:
	g.add((pattern, mid['lyrics'], Literal(lyrics_label)))

g.bind('mid', mid)
g.bind('mid-note', mid_note)
g.bind('mid-prog', mid_prog)
g.bind('prov', prov)

outfile = gzip.open(sys.argv[2] + '.gz', 'wb')
outfile.write(g.serialize(format='nquads'))
outfile.close()

exit(0)
