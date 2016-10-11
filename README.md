# midi2rdf

Suite of converters to transform MIDI files into RDF and backwards.

## Install

You need python 2.7. An updated version of [virtualenv](https://virtualenv.pypa.io/en/stable/) is adviced.

<pre>
git clone https://github.com/albertmeronyo/midi2rdf
cd midi2rdf
virtualenv .
source bin/activate
pip install -r requirements.txt
</pre>

## Usage

`python src/midi2rdf.py <midi-input-file> <rdf-output-file>`: convert a MIDI file to RDF (turtle serialization):

`python src/rdf2midi.py <rdf-input-file> <midi-output-file>`: convert that RDF file back to MIDI

### Other tools

`python src/midicat.py <midi-file>`: print human-readable MIDI commands

`python src/playrdf.sh`: play an RDF-converted MIDI file (requires [timidity](http://timidity.sourceforge.net/))

`python src/stream-midi-rdf.py`: print a stream of RDF triples coming from a virtual IAC device on the standard output. Can be used in combination with e.g. [MIDI Guitar](http://www.jamorigin.com/products/midi-guitar/)

## Background & Features

- Written as a proof-of-concept to represent digital music in Web interoperable ways
- Lossless conversion: MIDI files play the same after round-tripping to RDF

## Papers & References

- Please cite this work as: *Albert Meroño-Peñuela, Rinke Hoekstra. “The Song Remains the Same: Lossless Conversion and Streaming of MIDI to RDF and Back”. In: 13th Extended Semantic Web Conference (ESWC 2016), posters and demos track. May 29th — June 2nd, Heraklion, Crete, Greece (2016) ([PDF](https://www.albertmeronyo.org/wp-content/uploads/2016/04/ESWC2016_PD_paper_57.pdf))*
- [Blog post](http://www.snee.com/bobdc.blog/2016/08/converting-between-midi-and-rd.html) by [Bob DuCharme](http://www.snee.com/bob/)
- [Bring your MIDIs to the Dark Side](https://twitter.com/MikeLauruhn/status/738282161225236480)
