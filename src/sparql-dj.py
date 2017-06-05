from rdf2midi import rdf2midi
from flask import Flask, request, send_from_directory, render_template, make_response
import requests


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def hello_world():
    # dump = midi2rdf('/Users/Albert/src/midi2rdf/examples/ghostbusters.mid')
    return render_template('sparql-dj.html')

@app.route('/midi/<path:path>')
def static_mid(path):
    return send_from_directory('midi', path)

@app.route('/convert/<hash>')
def convert(hash):
    print hash

    url = "http://virtuoso-midi.amp.ops.labs.vu.nl/sparql"
    query = "PREFIX mid: <http://purl.org/midi-ld/midi#> CONSTRUCT { <foo> a mid:Pattern ; mid:resolution ?res ; mid:format ?format . <foo> mid:hasTrack ?track . ?track a mid:Track . ?track mid:hasEvent ?event . ?event ?prop ?val . } WHERE { <http://purl.org/midi-ld/pattern/" + hash + "> mid:hasTrack ?track ; mid:resolution ?res ; mid:format ?format . ?track mid:hasEvent ?event . ?event ?prop ?val . }"
    data = {"query" : query}
    headers = {"Accept" : "text/turtle"}
    res = requests.get(url, params=data, headers=headers)

    with open('static/midi/' + hash + '.ttl', 'w') as dump:
        dump.write(res.text)

    rdf2midi('static/midi/' + hash + '.ttl', 'static/midi/' + hash + '.mid')
    return make_response('200')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8093, debug=True)
