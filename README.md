# midi2rdf

Suite of converters to transform MIDI files into RDF and backwards.

## Install

You need python 2.7. An updated version of [virtualenv](https://virtualenv.pypa.io/en/stable/) is adviced.

<pre>
git clone https://github.com/midi-ld/midi2rdf
cd midi2rdf
virtualenv .
source bin/activate
pip install -r requirements.txt
</pre>

## Usage

`python src/midi2rdf.py <midi-input-file> -f turtle|nquads|... [<rdf output file> [--gz]]`: convert a MIDI file to RDF (-f indicates your desired serialization; see https://rdflib.readthedocs.io/en/latest/faq.html#questions-about-serializing for options). Examples:

<pre>
python src/midi2rdf.py ghostbusters.mid -f turtle #prints MIDI as RDF Turtle in stdout
python src/midi2rdf.py ghostbusters.mid -f n3 ghostbusters.nt #dumps MIDI as RDF N-Triples to file
python src/midi2rdf.py ghostbusters.mid -f nquads ghostbusters.nq.gz --gz #dumps MIDI as RDF Nquads to gz compressed file
</pre>

`python src/rdf2midi.py <rdf-input-file> <midi-output-file>`: convert that RDF file back to MIDI. The serialization will be guessed from the <rdf-input-file> extension (so: name them carefully)

### Other tools

`python src/midicat.py <midi-file>`: print human-readable MIDI commands

`python src/playrdf.sh`: play an RDF-converted MIDI file (requires [timidity](http://timidity.sourceforge.net/))

`python src/stream-midi-rdf.py`: print a stream of RDF triples coming from a virtual IAC device on the standard output. Can be used in combination with e.g. [MIDI Guitar](http://www.jamorigin.com/products/midi-guitar/)

## Background & Features

- Interoperable representation of MIDI files: link their contents to annotations, other musical events (e.g. MusicXML), or to any related resource on the Web
- Lossless conversion: MIDI files play the same after round-tripping to RDF
- If you prefer to use a `cloud service' version (i.e. without installing anything), go [here](http://midi2rdf.amp.ops.labs.vu.nl/)

## Papers & References

- Please cite this work as: *Albert Meroño-Peñuela, Rinke Hoekstra. “The Song Remains the Same: Lossless Conversion and Streaming of MIDI to RDF and Back”. In: 13th Extended Semantic Web Conference (ESWC 2016), posters and demos track. May 29th — June 2nd, Heraklion, Crete, Greece (2016) ([PDF](https://www.albertmeronyo.org/wp-content/uploads/2016/04/ESWC2016_PD_paper_57.pdf))*
- [Blog post](http://www.snee.com/bobdc.blog/2016/08/converting-between-midi-and-rd.html) by [Bob DuCharme](http://www.snee.com/bob/)
- [Bring your MIDIs to the Dark Side](https://twitter.com/MikeLauruhn/status/738282161225236480)
