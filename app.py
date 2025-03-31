from flask import Flask, render_template, request
import requests

app = Flask(__name__)

DISCOGS_API_KEY = "WGntzCWnmIBNKDEtoqcp"
DISCOGS_SECRET = "YhslOxfRtHXRVZNZwXlBxrCRUYFfgZTB"
DISCOGS_BASE_URL = "https://api.discogs.com"

HEADERS = {
    "User-Agent": "Vinylpedia/1.0"
}

# Función para buscar vinilos por artista en Discogs
def search_vinyls(artist_name):
    url = f"{DISCOGS_BASE_URL}/database/search?q={artist_name}&type=release&format=Vinyl&key={DISCOGS_API_KEY}&secret={DISCOGS_SECRET}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        vinyls = []
        for vinyl in results:
            vinyls.append({
                "id": vinyl.get("id"),
                "title": vinyl.get("title", "Sin título"),
                "cover_image": vinyl.get("cover_image", "https://via.placeholder.com/200")
            })
        return vinyls
    
    return []

# Función para obtener detalles de un vinilo específico
def get_vinyl_details(vinyl_id):
    url = f"{DISCOGS_BASE_URL}/releases/{vinyl_id}?key={DISCOGS_API_KEY}&secret={DISCOGS_SECRET}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "id": data.get("id"),
            "title": data.get("title", "Sin título"),
            "artist": ', '.join([a['name'] for a in data.get("artists", [])]),
            "cover_image": data.get("images", [{}])[0].get("uri", "https://via.placeholder.com/200"),
            "label": ', '.join([l['name'] for l in data.get("labels", [])]),
            "format": ', '.join(data.get("formats", [{}])[0].get("descriptions", [])),
            "country": data.get("country", "Desconocido"),
            "release_year": data.get("year", "Desconocido"),
            "genre": ', '.join(data.get("genres", [])),
            "style": ', '.join(data.get("styles", [])),
            "description": data.get("notes", "Sin descripción"),
            "tracklist": [
                {"position": t.get("position", ""), "title": t.get("title", ""), "duration": t.get("duration", "Desconocido")}
                for t in data.get("tracklist", [])
            ],
            "discogs_url": data.get("uri", ""),
            "videos": [
                {"title": v.get("title", "Ver video"), "url": v.get("uri", "#")}
                for v in data.get("videos", [])
            ]
        }
    
    return None

@app.route('/')
def index():
    artist_name = request.args.get('artist', '')
    results = search_vinyls(artist_name) if artist_name else []
    return render_template('index.html', results=results)

@app.route('/vinyl/<int:vinyl_id>')
def vinyl_detail(vinyl_id):
    vinyl = get_vinyl_details(vinyl_id)
    if not vinyl:
        return "Vinilo no encontrado", 404
    return render_template('vinyl_detail.html', vinyl=vinyl)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

