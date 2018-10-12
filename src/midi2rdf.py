#!/usr/bin/python

import midi
import rdflib
from rdflib import Namespace, ConjunctiveGraph, RDF, RDFS, URIRef, Literal, BNode, Graph
from rdflib.collection import Collection
import sys
from werkzeug.urls import url_fix
import hashlib
import ast
import gzip
from datetime import datetime
import music21
music21.environment.UserSettings()['warnings'] = 0

def midi2rdf(filename, ser_format):
    """
    Returns a text/turtle dump of the input MIDI filename
    """

    # Read the input MIDI file
    pattern_midi = midi.read_midifile(filename)

    # Get MD5 to identify the file
    md5_id = hashlib.md5(open(filename, 'rb').read()).hexdigest()

    mid_uri = URIRef("http://purl.org/midi-ld/midi#")
    prov_uri = URIRef("http://www.w3.org/ns/prov#")
    mid_note_uri = URIRef("http://purl.org/midi-ld/notes/")
    mid_prog_uri = URIRef("http://purl.org/midi-ld/programs/")
    m_uri = URIRef(url_fix("http://purl.org/midi-ld/piece/"))
    mid = Namespace(mid_uri)
    prov = Namespace(prov_uri)
    mid_note = Namespace(mid_note_uri)
    mid_prog = Namespace(mid_prog_uri)
    m = Namespace(m_uri)

    # Create the graph
    g = ConjunctiveGraph(identifier=m_uri)

    # piece = mid[filename.split('.')[0]]
    piece = m[md5_id]
    g.add((piece, RDF.type, mid.Piece))
    g.add((piece, mid.resolution, Literal(pattern_midi.resolution)))
    g.add((piece, mid['format'], Literal(pattern_midi.format)))

    # PROV info
    # g.add((piece, prov.wasDerivedFrom, Literal(filename)))
    agent = URIRef("https://github.com/midi-ld/midi2rdf")
    entity_d = piece
    entity_o = URIRef("http://purl.org/midi-ld/file/{}".format(md5_id))
    activity = URIRef(piece + "-activity")

    g.add((agent, RDF.type, prov.Agent))
    g.add((entity_d, RDF.type, prov.Entity))
    g.add((entity_o, RDF.type, prov.Entity))
    g.add((entity_o, RDF.type, mid.MIDIFile))
    g.add((entity_o, mid.path, Literal(filename)))
    g.add((activity, RDF.type, prov.Activity))
    g.add((entity_d, prov.wasGeneratedBy, activity))
    g.add((entity_d, prov.wasAttributedTo, agent))
    g.add((entity_d, prov.wasDerivedFrom, entity_o))
    g.add((activity, prov.wasAssociatedWith, agent))
    g.add((activity, prov.startedAtTime, Literal(datetime.now())))
    g.add((activity, prov.used, entity_o))

    # Since we won't mess with RDF statement order, we'll have absolute ticks
    # pattern_midi.make_ticks_abs()

    # We'll append the lyrics in this label
    lyrics_label = ""

    # Attach key to the piece
    m21stream = music21.converter.parse(filename)
    key = m21stream.analyze('key')
    g.add((piece, mid.key, Literal(key)))
    tracks = []
    for n_track in range(len(pattern_midi)):
        track = URIRef(piece + '/track' + str(n_track).zfill(2)) #So we can order by URI later -- UGLY PATCH
        tracks.append(track)
        g.add((track, RDF.type, mid.Track))
        # g.add((piece, mid.hasTrack, track))
        events = []
        for n_event in range(len(pattern_midi[n_track])):
            event_midi = pattern_midi[n_track][n_event]
            event = URIRef(piece + '/track' + str(n_track).zfill(2) + '/event'+ str(n_event).zfill(4))
            events.append(event)
            g.add((event, RDF.type, mid[(type(event_midi).__name__)]))
            # g.add((track, mid.hasEvent, event))
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
                    # print text_value
                    # text_value = ''.join(chr(i) for i in ast.literal_eval(text_data_literal))
                    g.add((event, RDFS.label, Literal(text_value)))
                    if type(event_midi).__name__ == 'LyricsEvent':
            			lyrics_label += text_value
                elif type(event_midi).__name__ in ['NoteOnEvent', 'NoteOffEvent'] and slot == 'pitch':
                    pitch = str(getattr(event_midi, slot))
                    c = music21.pitch.Pitch()
                    c.midi = int(pitch)
                    scale_degree = key.getScaleDegreeFromPitch(c.name)
                    g.add((event, mid['note'], mid_note[pitch]))
                    g.add((event, mid['scaleDegree'], Literal(scale_degree)))
                elif type(event_midi).__name__ in ['ProgramChangeEvent'] and slot == 'value':
                    program = str(getattr(event_midi, slot))
                    g.add((event, mid['program'], mid_prog[program]))
                else:
                    g.add((event, mid[slot], Literal(getattr(event_midi, slot))))

        # Add events to an rdf:List to keep their order
        # Watch the new term mid.hasEvents -- in plural
        event_list = BNode()
        c = Collection(g, event_list, events)
        g.add((track, mid.hasEvents, event_list))
    # Add tracks to an rdf:List to keep their order
    # Watch the new term mid.hasTracks -- in plural
    track_list = BNode()
    c = Collection(g, track_list, tracks)
    g.add((piece, mid.hasTracks, track_list))

    # Add the global lyrics link, if lyrics not empty
    if lyrics_label:
    	g.add((piece, mid['lyrics'], Literal(lyrics_label)))

    g.bind('midi', mid)
    g.bind('midi-note', mid_note)
    g.bind('midi-prog', mid_prog)
    g.bind('prov', prov)

    # Finished -- record PROV end times
    end_time = Literal(datetime.now())
    g.add((entity_d, prov.generatedAtTime, end_time) )
    g.add((activity, prov.endedAtTime, end_time) )

    return g.serialize(format=ser_format)

if __name__ == "__main__":


    if len(sys.argv) < 4:
        print "Usage: {0} <midi input file> -f nquads|turtle|... [<rdf output file> [--gz]]".format(sys.argv[0])
        exit(2)

    filename = sys.argv[1]
    dump = midi2rdf(filename, sys.argv[3])

    if len(sys.argv) > 4:
        if '--gz' in sys.argv:
            with gzip.open(sys.argv[4], 'wb') as outfile:
                outfile.write(dump)
        else:
            with open(sys.argv[4], 'w') as outfile:
                outfile.write(dump)
    else:
        print dump

    exit(0)
