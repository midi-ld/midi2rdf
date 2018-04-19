#!/bin/bash

# upload-midi-ld.sh: Uploads MIDI LD data to endpoint via SPARQL

if [ $# -lt 2 ]
  then
    echo "Usage: upload-midi-ld.sh <midi-rdf-ntriples-file> <endpoint-uri>"
    exit 0
fi

curl -s -o /dev/null -X POST -H'Content-Type: application/sparql-update' -d"INSERT DATA { GRAPH <http://virtuoso-midi.amp.ops.labs.vu.nl/none> { $(cat $1) } }" $2
