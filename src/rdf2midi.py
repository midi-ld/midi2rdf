#!/usr/bin/env python

import midi
import rdflib
from rdflib import Namespace, Graph, RDF, RDFS, URIRef, Literal, util
import ast
import sys
from unidecode import unidecode

def rdf2midi(input_filename, output_filename):
    mid_uri = URIRef("http://purl.org/midi-ld/midi#")
    mid = Namespace(mid_uri)

    # Read the input RDF file
    g = Graph()
    g.parse(input_filename, format=util.guess_format(input_filename))

    # Initialize the MIDI file
    p_resolution = 96
    p_format = 1
    for s,p,o in g.triples((None, mid.resolution, None)):
        p_resolution = int(o)
    for s,p,o in g.triples((None, mid['format'], None)):
        p_format = int(o)

    pattern = midi.Pattern(resolution=p_resolution, format=p_format)

    # Retrieve the tracks
    for s,p,o in sorted(g.triples((None, RDF.type, mid.Track))):
        # print 'processing track {}'.format(s)
        track = midi.Track()
        pattern.append(track)
        # Retrieve all events on this track
        for x,y,z in sorted(g.triples((s, mid.hasEvent, None))):
            # print 'processing event {}'.format(z)
            event_type = g.value(subject=z, predicate=RDF.type)
            if event_type == mid.NoteOnEvent:
                tick = None
                channel = None
                velocity = None
                pitch = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.velocity):
                    velocity = int(p)
                for p in g.objects(z, mid.note):
                    pitch = int(p.split('/')[-1])

                # if tick is None or channel is None or velocity is None or pitch is None:
                #     print "tick {} channel {} velocity {} pitch {}".format(tick,channel,velocity,pitch)
                #     print z
                on = midi.NoteOnEvent(tick=tick, channel=channel, velocity=velocity, pitch=pitch)
                track.append(on)
            elif event_type == mid.NoteOffEvent:
                tick = None
                channel = None
                pitch = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.note):
                    pitch = int(p.split('/')[-1])

                # if tick is None or channel is None or pitch is None:
                #     print "tick {} channel {} pitch {}".format(tick,channel,pitch)
                #     print z
                off = midi.NoteOffEvent(tick=tick, channel=channel, pitch=pitch)
                track.append(off)
            elif event_type == mid.EndOfTrackEvent:
                tick = None
                channel = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                # if tick is None or channel is None:
                #     print "tick {} channel {}".format(tick,channel)
                #     print z
                eot = midi.EndOfTrackEvent(tick=tick, channel=channel)
                track.append(eot)
            elif event_type == mid.PortEvent:
                tick = None
                channel = None
                data = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.data):
                    data = ast.literal_eval(p)
                # if tick is None or channel is None or data is None:
                #     print "tick {} channel {} data {}".format(tick,channel,data)
                #     print z
                pe = midi.PortEvent(tick=tick, channel=channel, data=data)
                track.append(pe)
            elif event_type == mid.ControlChangeEvent:
                tick = None
                channel = None
                control = None
                value = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.control):
                    control = int(p)
                for p in g.objects(z, mid.value):
                    value = int(p)
                # if tick is None or channel is None or control is None or value is None:
                #     print "tick {} channel {} control {} value {}".format(tick,channel,control,value)
                #     print z
                cc = midi.ControlChangeEvent(tick=tick, channel=channel, control=control, value=value)
                track.append(cc)
            elif event_type == mid.ProgramChangeEvent:
                tick = None
                channel = None
                value = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.program):
                    value = int(p.split('/')[-1])
                # if tick is None or channel is None or value is None:
                #     print "tick {} channel {} value {}".format(tick,channel,value)
                #     print z
                pce = midi.ProgramChangeEvent(tick=tick, channel=channel, value=value)
                track.append(pce)
            elif event_type == mid.SequencerSpecificEvent:
                tick = None
                channel = None
                data = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.data):
                    data = ast.literal_eval(p)
                # if tick is None or channel is None or data is None:
                #     print "tick {} channel {} data {}".format(tick,channel,data)
                #     print z
                sse = midi.SequencerSpecificEvent(tick=tick, channel=channel, data=data)
                track.append(sse)
            elif event_type == mid.TrackNameEvent:
                # Super ugly patch
                tick = None
                channel = None
                text = None
                data = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                # for p in g.objects(z, mid.text):
                #     text = str(p)
                for p in g.objects(z, RDFS.label):
                    text = str(unidecode(p))
                    data = [ord(t) for t in text]
                # for p in g.objects(z, mid.data):
                #     data = ast.literal_eval(p)
                # if tick is None or channel is None or text is None or data is None:
                #     print "tick {} channel {} text {} data {}".format(tick,channel,text,data)
                #     print z
                tne = midi.TrackNameEvent(tick=tick, channel=channel, text=text, data=data)
                # tne = midi.TrackNameEvent(tick=tick, channel=channel, text=text)
                track.append(tne)
            elif event_type == mid.SetTempoEvent:
                tick = None
                channel = None
                bpm = None
                mpqn = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.bpm):
                    bpm = float(p)
                for p in g.objects(z, mid.mpqn):
                    mpqn = int(p)
                # if tick is None or channel is None or bpm is None or mpqn is None:
                #     print "tick {} channel {} bpm {} mpqn {}".format(tick,channel,bpm,mpqn)
                #     print z
                ste = midi.SetTempoEvent(tick=tick, channel=channel, bpm=bpm, mpqn=mpqn)
                track.append(ste)
            elif event_type == mid.KeySignatureEvent:
                tick = None
                channel = None
                alternatives = None
                minor = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.alternatives):
                    alternatives = int(p)
                for p in g.objects(z, mid.minor):
                    minor = int(p)
                # if tick is None or channel is None or alternatives is None or minor is None:
                #     print "tick {} channel {} alternatives {} minor {}".format(tick,channel,alternatives,minor)
                #     print z
                kse = midi.KeySignatureEvent(tick=tick, channel=channel, alternatives=alternatives, minor=minor)
                track.append(kse)
            elif event_type == mid.TimeSignatureEvent:
                tick = None
                channel = None
                numerator = None
                denominator = None
                metronome = None
                thirtyseconds = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.numerator):
                    numerator = int(p)
                for p in g.objects(z, mid.denominator):
                    denominator = int(p)
                for p in g.objects(z, mid.metronome):
                    metronome = int(p)
                for p in g.objects(z, mid.thirtyseconds):
                    thirtyseconds = int(p)
                # if tick is None or channel is None or numerator is None or denominator is None or metronome is None or thirtyseconds is None:
                #     print "tick {} channel {} numerator {} denominator {} metronome {} thirtyseconds {}".format(tick,channel,numerator,denominator,metronome,thirtyseconds)
                #     print z
                tse = midi.TimeSignatureEvent(tick=tick, channel=channel, numerator=numerator, denominator=denominator, metronome=metronome, thirtyseconds=thirtyseconds)
                track.append(tse)
            elif event_type == mid.TextMetaEvent:
                tick = None
                channel = None
                text = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                # for p in g.objects(z, mid.text):
                #     text = str(p)
                for p in g.objects(z, RDFS.label):
                    text = str(unidecode(p))
                # if tick is None or channel is None or text is None:
                #     print "tick {} channel {} text {}".format(tick,channel,text)
                #     print z
                tme = midi.TextMetaEvent(tick=tick, channel=channel, text=text)
                track.append(tme)
            elif event_type == mid.SmpteOffsetEvent:
                tick = None
                data = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.data):
                    data = ast.literal_eval(p)
                # if tick is None or data is None:
                #     print "tick {} data {}".format(tick,data)
                #     print z
                sme = midi.SmpteOffsetEvent(tick=tick, data=data)
            elif event_type == mid.ChannelPrefixEvent:
                tick = None
                data = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.data):
                    data = ast.literal_eval(p)
                # if tick is None or data is None:
                #     print "tick {} data {}".format(tick,data)
                #     print z
                cpe = midi.ChannelPrefixEvent(tick=tick, data=data)
            elif event_type == mid.SysexEvent:
                tick = None
                channel = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                # if tick is None or channel is None:
                #     print "tick {} channel {}".format(tick,channel)
                #     print z
                se = midi.SysexEvent(tick=tick, channel=channel)
            elif event_type == mid.PitchWheelEvent:
                tick = None
                channel = None
                pitch = None
                for p in g.objects(z, mid.tick):
                    tick = int(p)
                for p in g.objects(z, mid.channel):
                    channel = int(p)
                for p in g.objects(z, mid.pitch):
                    pitch = int(p)

                # if tick is None or channel is None or pitch is None:
                #     print "tick {} channel {} pitch {}".format(tick,channel,pitch)
                #     print z
                pwe = midi.PitchWheelEvent(tick=tick, channel=channel, pitch=pitch)

            else:
                print "BIG ERROR, EVENT {0} TYPE UNMANAGED".format(event_type)

    midi.write_midifile(output_filename, pattern)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: {0} <rdf input file> <midi output file>".format(sys.argv[0])
        exit(2)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    rdf2midi(input_filename, output_filename)
