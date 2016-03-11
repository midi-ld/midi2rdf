#!/usr/bin/env python3

"""JACK client that prints all received MIDI events."""

import jack
import binascii

client = jack.Client("MIDI-Monitor")
port = client.midi_inports.register("input")
port2 = client.midi_outports.register("output")

@client.set_process_callback
def process(frames):
    for offset, data in port.incoming_midi_events():
        print("{0}: 0x{1}".format(client.last_frame_time + offset,
                                  binascii.hexlify(data).decode()))

client.activate()
# client.connect("MIDI Guitar:out2", "MIDI-Monitor:input")
client.get_all_connections("MIDI-Monitor:input")

with client:
    print("#" * 80)
    print("press Return to quit")
    print("#" * 80)
    input()

client.deactivate()
client.close()
