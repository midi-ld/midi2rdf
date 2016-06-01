
#!/bin/bash

source ../bin/activate
python rdf2midi.py $1 $1.mid
timidity $1.mid 2> /dev/null
