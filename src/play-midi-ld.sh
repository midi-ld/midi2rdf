#!/bin/bash

# play-midi-ld.sh: Plays a MIDI of the MIDI LD cloud by URI with timidity

if [ $# -eq 0 ]
  then
    echo "Usage: play-midi-ld.sh <MIDI-LD-URI>"
    exit 0
fi


curl -s -X GET -G --header "Accept: text/turtle" "http://localhost:8001/api/midi-ld/queries/pattern_graph" --data-urlencode "pattern=$1" > api.ttl
./rdf2midi.py api.ttl api.mid
timidity api.mid
rm api.mid
