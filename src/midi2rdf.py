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
import argparse

import music21
music21.environment.UserSettings()['warnings'] = 0

def midi2rdf(filename, ser_format='turtle', order='uri'):
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
    sequence_uri = URIRef("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#")
    mid = Namespace(mid_uri)
    prov = Namespace(prov_uri)
    mid_note = Namespace(mid_note_uri)
    mid_prog = Namespace(mid_prog_uri)
    m = Namespace(m_uri)
    sequence = Namespace(sequence_uri)

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
        if order in ['uri', 'prop_number', 'prop_time', 'sop']:
            g.add((piece, mid.hasTrack, track))
        elif order in ['list']:
            g.add((piece, RDF.type, RDF.List))
        elif order in ['seq']:
            g.add((piece, RDF.type, RDF.Seq))
        else:
            print("ERROR: {} is an unsupported order strategy".format(order))
        events = []
        absoluteTick = 0
        for n_event in range(len(pattern_midi[n_track])):
            event_midi = pattern_midi[n_track][n_event]
            event = URIRef(piece + '/track' + str(n_track).zfill(2) + '/event'+ str(n_event).zfill(4))
            events.append(event)
            g.add((event, RDF.type, mid[(type(event_midi).__name__)]))
            if order in ['uri', 'prop_number', 'prop_time', 'sop']:
                g.add((track, mid.hasEvent, event))
            elif order in ['list']:
                g.add((track, RDF.type, RDF.List))
            elif order in ['seq']:
                g.add((track, RDF.type, RDF.Seq))
            else:
                print("ERROR: {} is an unsupported order strategy".format(order))
            absoluteTick += int(event_midi.tick)
            # Save the 'tick' slot (shared among all events)
            g.add((event, mid.tick, Literal(event_midi.tick)))
            if order in ['prop_number']:
                g.add((event, mid.absoluteTick, Literal(absoluteTick)))
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

        if order in ['list']:
            # Add events to an rdf:List to keep their order
            # Watch the new term mid.hasEvents -- in plural
            event_list = BNode()
            c = Collection(g, event_list, events)
            g.add((track, mid.hasEvents, event_list))
        elif order in ['seq']:
            # Add events to an rdf:Seq to keep their ordering
            event_list = BNode()
            for i in range(1, len(events)+1):
                g.add((event_list, URIRef(str(RDF) + '_{}'.format(i)), events[i-1]))
            g.add((track, mid.hasEvents, event_list))
        elif order in ['sop']:
            # Link events with the sequence ontology design pattern
            for i in range(len(events)):
                if i > 0:
                    g.add((events[i], sequence['follows'], events[i-1]))
                if i < len(events)-1:
                    g.add((events[i], sequence['precedes'], events[i+1]))
    if order in ['list']:
        # Add tracks to an rdf:List to keep their order
        # Watch the new term mid.hasTracks -- in plural
        track_list = BNode()
        c = Collection(g, track_list, tracks)
        g.add((piece, mid.hasTracks, track_list))
    elif order in ['seq']:
        # Add tracks to an rdf:Seq to keep their order
        track_list = BNode()
        for i in range(1, len(tracks)+1):
            g.add((track_list, URIRef(str(RDF) + '_{}'.format(i)), tracks[i-1]))
        g.add((piece, mid.hasTracks, track_list))
    elif order in ['sop']:
        for i in range(len(tracks)):
            if i > 0:
                g.add((tracks[i], sequence['follows'], tracks[i-1]))
            if i < len(events)-1:
                g.add((tracks[i], sequence['precedes'], tracks[i+1]))

    # Add the global lyrics link, if lyrics not empty
    if lyrics_label:
    	g.add((piece, mid['lyrics'], Literal(lyrics_label)))

    g.bind('midi', mid)
    g.bind('midi-note', mid_note)
    g.bind('midi-prog', mid_prog)
    g.bind('prov', prov)
    g.bind('sequence', sequence)

    # Finished -- record PROV end times
    end_time = Literal(datetime.now())
    g.add((entity_d, prov.generatedAtTime, end_time) )
    g.add((activity, prov.endedAtTime, end_time) )

    return g.serialize(format=ser_format)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='midi2rdf', description="MIDI to RDF converter")
    parser.add_argument('filename', nargs=1, type=str, help="Path to the MIDI file to convert")
    parser.add_argument('--format', '-f', dest='format', nargs='?', choices=['xml', 'n3', 'turtle', 'nt', 'pretty-xml', 'trix', 'trig', 'nquads'], default='turtle', help="RDF serialization format")
    parser.add_argument('outfile', nargs='?', type=str, default=None, help="Output RDF file (if omitted defaults to stdout)")
    parser.add_argument( '--gz', '-z', dest='gz', action='store_true', default=False, help="Compress the output of the conversion")
    parser.add_argument('--order', '-o', dest='order', nargs='?', choices=['uri', 'prop_number', 'prop_time', 'seq', 'list', 'sop'], default='uri', help="Track and event ordering strategy")
    parser.add_argument('--version', '-v', dest='version', action='version', version='0.2')
    args = parser.parse_args()

    dump = midi2rdf(args.filename[0], args.format, args.order)

    if args.outfile:
        if args.gz:
            with gzip.open(args.outfile, 'wb') as out:
                out.write(dump)
        else:
            with open(args.outfile, 'w') as out:
                out.write(dump)
    else:
        print(dump)

    exit(0)
