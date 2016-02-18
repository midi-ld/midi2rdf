import midi
import sys

if len(sys.argv) != 2:
    print "Usage: {0} <midi file>".format(sys.argv[0])
    exit(2)

infile = sys.argv[1]
pattern = midi.read_midifile(infile)
print pattern
exit(0)
