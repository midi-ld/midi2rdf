# Adapted from https://audiodestrukt.wordpress.com/2013/06/23/midi-programming-in-python/
import sys, pygame, pygame.midi
from rdflib import Graph, Namespace, Literal, RDF
import uuid

# set up pygame
pygame.init()
pygame.midi.init()

# initialize rdf graph
g = Graph()
# Namespaces
mid = Namespace("http://example.org/midi/")
pattern_id = uuid.uuid4()
m = Namespace("http://example.org/midi/" + str(pattern_id) + "/")

g.bind('mid', mid)

# list all midi devices
for x in range( 0, pygame.midi.get_count() ):
    print pygame.midi.get_device_info(x)

# open a specific midi device
inp = pygame.midi.Input(0)

# run the event loop
while True:
    if inp.poll():
        # no way to find number of messages in queue
        # so we just specify a high max value
        e = inp.read(1000)
        el = eval(str(e))
        # Format is [[status,data1,data2,data3],timestamp],...]
        # status = midi event (144 is NoteOn, 128 is NoteOff)
        # data1 = pitch
        # data2 = velocity
        # data3 = channel
        # Loop over other possible simultaneous events
        for event in el:
            status = None
            if event[0][0] == 144:
                status = "NoteOnEvent"
            elif event[0][0] == 128:
                status = "NoteOffEvent"
            else:
                print "BIG ERROR, unexpected event type"
            pitch = event[0][1]
            velocity = event[0][2]
            channel = event[0][3]
            timestamp = event[1]
            #print status, pitch, velocity, channel, timestamp
            # Creating triples!
            track_id = uuid.uuid4()
            event = m['track' + str(track_id) + '/event' + str(uuid.uuid4())]
            g.add((event, RDF.type, mid[status]))
            g.add((event, mid.tick, Literal(timestamp)))
            g.add((event, mid.channel, Literal(channel)))
            g.add((event, mid.pitch, Literal(pitch)))
            g.add((event, mid.velocity, Literal(velocity)))
            for s,p,o in g.triples((None, None, None)):
                print g.qname(s),g.qname(p),o,'.'
            g = Graph()



    # wait 10ms - this is arbitrary, but wait(0) still resulted
    # in 100% cpu utilization
    pygame.time.wait(10)
