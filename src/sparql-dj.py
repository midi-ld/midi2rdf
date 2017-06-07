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

@app.route('/mashup')
def mashup():
    tracklist = ""
    for u in request.args.getlist('tracks[]'):
        tracklist += "<" + u + ">,"
    print tracklist

    pattern1 = "<http://purl.org/midi-ld/pattern/" + request.args.get('hash1') + ">"
    pattern2 = "<http://purl.org/midi-ld/pattern/" + request.args.get('hash2') + ">"

    print pattern1
    print pattern2


    url = "http://virtuoso-midi.amp.ops.labs.vu.nl/sparql"
    query ="PREFIX mid: <http://purl.org/midi-ld/midi#> CONSTRUCT { <newsong> a mid:Pattern ; mid:hasTrack ?track . <newsong> mid:format ?format . <newsong> mid:resolution ?resolution . ?track mid:hasEvent ?event . ?track a mid:Track . ?event a ?type . ?event ?property ?value . } WHERE { { " + pattern1 + " mid:hasTrack ?track . " + pattern1 + " mid:format ?format . " + pattern1 + " mid:resolution ?resolution . ?track mid:hasEvent ?event . ?event a ?type . ?event ?property ?value . FILTER (?track IN (" + tracklist + " <arbitrary>)) } UNION { " + pattern2 + " mid:hasTrack ?track . " + pattern2 + " mid:format ?format . " + pattern2 + " mid:resolution ?resolution . ?track mid:hasEvent ?event . ?event a ?type . ?event ?property ?value . FILTER (?track IN (" + tracklist + " <arbitrary>)) } }"

    print query

    data = {"query" : query}
    headers = {"Accept" : "text/turtle"}
    res = requests.get(url, params=data, headers=headers)

    with open('static/midi/mashup.ttl', 'w') as dump:
        dump.write(res.text)

    rdf2midi('static/midi/mashup.ttl', 'static/midi/mashup.mid')

    return make_response('200')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8093, debug=True)
