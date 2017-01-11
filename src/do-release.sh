#!/bin/bash

# Full conversion to nq.gz
find 130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive\[6_19_15\] -type f -name "*.mid" | parallel nice python /home/amp/src/midi2rdf/src/midi2rdf-bulk.py {} {}.nq

# Move nq files to same directory structure
find 130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive\[6_19_15\] -type f -name "*.nq.gz" -exec cp --parents \{\} 2016-11-21 \;

cd 2016-11-21

# Archive the whole thing
tar czf midi-ld.tar.gz 130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive\[6_19_15\]

# Text events
cp ../midi-text.csv midi-text-20161121.csv
gzip midi-text-20161121.csv

# Edit changelog
emacs changelog
