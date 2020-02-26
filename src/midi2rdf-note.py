#!/usr/bin/python

import rdflib
from rdflib import Namespace, ConjunctiveGraph, RDF, RDFS, URIRef, Literal
import sys
from werkzeug.urls import url_fix
import hashlib
import ast
import gzip
from datetime import datetime
import mido
from mido import tick2second

import music21
music21.environment.UserSettings()['warnings'] = 0

# Lookup table wiht event names
msg_name = {'note_on' : "NoteOnEvent",
            'note_off' : "NoteOffEvent",
            'time_signature' : "TimeSignatureEvent",
            'program_change' : "ProgramChangeEvent",
            'end_of_track' : "EndOfTrackEvent",
            'midi_port' : "PortEvent",
            'track_name' : "TrackNameEvent",
            'control_change' : "ControlChangeEvent",
            'sequencer_specific' : "SequencerSpecificEvent",
            'key_signature' : "KeySignatureEvent",
            'set_tempo' : "SetTempoEvent",
            'text' : "TextMetaEvent",
            'smpte_offset' : "SmpteOffsetEvent",
            'channel_prefix' : "ChannelPrefixEvent"}

# Bookkeeping of active notes for NoteEvent
active_notes = [None]*127

def midi2rdf(filename, ser_format):
    """
    Returns a text/turtle dump of the input MIDI filename
    """

    # Read the input MIDI file
    # pattern_midi = midi.read_midifile(filename)
    midifile = mido.MidiFile(filename)

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
    # TODO: find the way to get resolution and format in Mido
    # g.add((piece, mid.resolution, Literal(pattern_midi.resolution)))
    # g.add((piece, mid['format'], Literal(pattern_midi.format)))

    # PROV info
    g.add((piece, prov.wasDerivedFrom, Literal(filename)))
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

    # We'll append the lyrics in this label
    lyrics_label = ""

    # Attach key to the piece
    m21stream = music21.converter.parse(filename)
    key = m21stream.analyze('key')
    g.add((piece, mid.key, Literal(key)))

    # Main loop
    tempo = 500000
    for i,tr in enumerate(midifile.tracks):
        track = URIRef(piece + '/track' + str(i).zfill(2))
        g.add((piece, mid.hasTrack, track))
        g.add((track, RDF.type, mid.Track))
        abs_time = .0
        for j,msg in enumerate(tr):
            event = URIRef(piece + '/track' + str(i).zfill(2) + '/event'+ str(j).zfill(4))
            # Add the event and timing info to the track
            g.add((track, mid.hasEvent, event))
            g.add((event, RDF.type, mid[msg_name[msg.type]]))
            rel_time = tick2second(msg.time, midifile.ticks_per_beat, tempo)
            abs_time += rel_time
            g.add((event, mid.relativeTime, Literal(rel_time)))
            g.add((event, mid.absoluteTime, Literal(abs_time)))
            # Message type specific processing
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            if msg.type == 'time_signature':
                g.add((event, mid['numerator'], Literal(msg.numerator)))
                g.add((event, mid['denominator'], Literal(msg.denominator)))
                g.add((event, mid['metronome'], Literal(msg.clocks_per_click)))
                g.add((event, mid['thirtyseconds'], Literal(msg.notated_32nd_notes_per_beat)))
                g.add((event, mid['tick'], Literal(msg.time)))
            if msg.type == 'program_change':
                g.add((event, mid['program'], mid_prog[str(msg.program)]))
                g.add((event, mid['channel'], Literal(msg.channel)))
                g.add((event, mid['tick'], Literal(msg.time)))
            if msg.type == 'set_tempo':
                g.add((event, mid['tempo'], Literal(msg.tempo)))
                g.add((event, mid['tick'], Literal(msg.time)))
            if msg.type == 'note_on' or msg.type == 'note_off':
                c = music21.pitch.Pitch()
                c.midi = int(msg.note)
                scale_degree = key.getScaleDegreeFromPitch(c.name)
                g.add((event, mid['note'], mid_note[str(msg.note)]))
                g.add((event, mid['velocity'], Literal(msg.velocity)))
                g.add((event, mid['channel'], Literal(msg.channel)))
                g.add((event, mid['tick'], Literal(msg.time)))
                g.add((event, mid['scaleDegree'], Literal(scale_degree)))
                # Processing of NoteEvent
                if msg.type == 'note_on':
                    active_notes[msg.note] = {"note_start" : event, "note_start_time" : abs_time}
                if msg.type == 'note_off':
                    if active_notes[msg.note] is not None:
                        note_start = active_notes[msg.note]["note_start"]
                        note_end = event
                        duration = abs_time - active_notes[msg.note]["note_start_time"]
                        note_event = URIRef(event + '/NoteEvent')
                        g.add((note_event, RDF.type, mid['NoteEvent']))
                        g.add((note_event, mid['noteStart'], note_start))
                        g.add((note_event, mid['noteEnd'], note_end))
                        g.add((note_event, mid['duration'], Literal(duration)))
                        active_notes[msg.note] = None

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
        print("Usage: {0} <midi input file> -f nquads|turtle|... [<rdf output file> [--gz]]".format(sys.argv[0]))
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
        print(dump.decode())

    exit(0)
