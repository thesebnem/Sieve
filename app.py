from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius

app = Flask(__name__)

user_filters = []
# 🔍 Song suggestions (autocomplete için)
SONG_SUGGESTIONS = [
    "bad guy",
    "shape of you",
    "believer",
    "blinding lights",
    "someone you loved",
    "faded",
    "starboy",
    "lovely"
]

# 🔑 API KEYS
CLIENT_ID = "8117d8088fd24c0ab80410a8078baaa7"
CLIENT_SECRET = "7e8b991eea70404fb610716e1dbbaf7d"
GENIUS_TOKEN = "pcvOoIKC6tiPatzl26KQw6dD6YIB-JbKR55JatJW7brz5aUxtEe2tKteD3eKyJrX"

# 🎵 Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# 🎤 Genius setup
genius = lyricsgenius.Genius(GENIUS_TOKEN, timeout=15)
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

def get_cover(song_name):
    try:
        data = sp.search(q=song_name, type="track", limit=1)
        items = data["tracks"]["items"]

        if not items:
            return "https://via.placeholder.com/60"

        return items[0]["album"]["images"][0]["url"]

    except:
        return "https://via.placeholder.com/60"

# 📜 MEMORY
history = []

# ⚠️ WORD LISTS
bad_words = ["fuck", "shit", "bitch", "asshole", "damn"]
negative_words = ["hate", "cry", "alone", "pain"]
romantic_words = [
    # İngilizce
    "love", "loves", "loving",
    "heart", "hearts",
    "baby", "darling", "honey",
    "kiss", "kissing",
    "lover", "romance", "romantic",
    "hug", "holding",
    "together", "forever",
    "need you", "want you", "miss you",
    "angel", "passion", "desire",
    "beautiful", "smile", "eyes", "soul",
    "dream", "dreaming",

    # Türkçe
    "aşk", "aşık",
    "sevgi", "seviyorum", "sevdim", "sevmek",
    "kalp", "kalbim", "kalbimde",
    "yar", "yârim",
    "sevgili", "sevgilim",
    "canım", "hayatım",
    "özledim", "özlemek", "özlüyorum",
    "gözlerin", "gözlerinle",
    "sarıl", "sarılmak", "sarıldım",
    "birlikte", "sonsuza",
    "ruh eşim",
    "tut elimden",
    "aşkım",
    "bir tanem",
    "tek aşkım",
    "seni seviyorum",
    "sana aşığım",
    "kalbimi",
    "kalbimde sen",
    "yanımda ol",
    "ellerin",
    "dudakların",
    "gülüşün",
    "hasret",
    "hasretin",
    "özlem",
    "özlemin",
    "yüreğim",
    "yüreğimde",
    "can özüm",
    "sensiz",
    "seninle",
    "yanındayım"
]

energy_words = [
    # İngilizce
    "energy", "power", "strong", "strength",
    "fight", "fighter", "battle", "warrior",
    "fire", "burn", "burning",
    "run", "running", "speed",
    "winner", "victory", "champion",
    "rise", "rise up",
    "never give up", "keep going",
    "wild", "crazy",
    "jump", "dance", "move",
    "loud", "scream", "shout",
    "beast", "unstoppable",
    "freedom", "alive",
    "explosion", "explode",

    # Türkçe
    "güç", "güçlü", "gücüm",
    "enerji", "enerjik",
    "ateş", "yan", "yanmak",
    "patla", "patlamak",
    "koş", "koşmak",
    "hız", "hızlı",
    "özgür", "özgürlük",
    "savaş", "savaşmak",
    "mücadele", "diren",
    "direnmek",
    "kazan", "kazanmak",
    "zafer", "şampiyon",
    "haydi", "hadi",
    "devam", "devam et",
    "yıkılma",
    "ayağa kalk",
    "yüksel", "yükselmek",
    "başarı",
    "gaza gel",
    "coşku", "coşmak",
    "hareket", "hareket et",
    "dans", "dans et",
    "bağır", "çığlık",
    "durma",
    "pes etme",
    "asla vazgeçme",
    "yenilmez",
    "zirve",
    "yüksek ses",
    "adrenalin"
]

sad_words = [
    # İngilizce
    "sad", "sadness",
    "cry", "crying", "cries",
    "alone", "lonely", "loneliness",
    "pain", "hurt", "hurting",
    "broken", "breakup",
    "lost", "loss",
    "tears", "tear",
    "goodbye", "farewell",
    "missing", "missed",
    "empty", "emptiness",
    "dark", "darkness",
    "regret", "regrets",
    "sorry",
    "heartbreak",
    "suffer", "suffering",
    "death", "dying",
    "cold", "rain",
    "forgotten",

    # Türkçe
    "üzgün", "üzüldüm", "üzülüyorum",
    "hüzün", "hüzünlü",
    "acı", "acıyor",
    "yalnız", "yalnızlık",
    "ağla", "ağlamak", "ağladım",
    "gözyaşı", "gözyaşları",
    "kırık", "kırıldım",
    "terk", "terk et",
    "ayrılık", "ayrıldık",
    "kaybettim", "kayboldu",
    "özlem", "hasret",
    "sensiz", "yoksun",
    "bittik", "bitti",
    "unutamadım", "unutmak",
    "pişman", "pişmanlık",
    "ölüm", "ölmek",
    "karanlık",
    "çaresiz", "çaresizlik",
    "suskun",
    "yalan",
    "keder",
    "dert", "dertler",
    "yaralı", "yaram",
    "yıkıldım",
    "mahvoldum",
    "kimsesiz",
    "hastayım",
    "gidemem",
    "gidiyorsun",
    "elveda",
    "hoşçakal",
    "kahroldum"
]

# 🎧 RECOMMENDATIONS
recommendations = {
    "happy": [
        "Blinding Lights - The Weeknd",
        "Levitating - Dua Lipa",
        "Dudu - Tarkan",
        "Yalan - Duman"
    ],
    "sad": [
        "Someone Like You - Adele",
        "Fix You - Coldplay",
        "Gülümse - Sezen Aksu"
    ],
    "energy": [
        "Believer - Imagine Dragons",
        "Till I Collapse - Eminem",
        "Susamam - Şanışer"
    ],
    "neutral": [
        "Heat Waves - Glass Animals",
        "Stay - The Kid LAROI",
        "Seni Dert Etmeler - Madrigal"
    ]
}

clean_playlist = []
chill_playlist = []
energy_playlist = []


# 🧠 ANALYZE
def analyze(text):

    text = text.lower()

    profanity = sum(text.count(w) for w in bad_words)

    words = text.split()

    romantic = sum(1 for w in words if w in romantic_words)
    energy = sum(1 for w in words if w in energy_words)
    sadness = sum(1 for w in words if w in sad_words)

    if profanity == 0:
        mood = "Temiz içerik"
        score = 80 - sadness * 5 + romantic * 2

    elif profanity <= 2:
        mood = "Orta içerik"
        score = 60 - sadness * 5 + romantic * 2

    else:
        mood = "Yoğun içerik"
        score = 40 - sadness * 5 + romantic * 2

    return {
        "profanity": profanity,
        "romantic": romantic,
        "energy": energy,
        "sadness": sadness,
        "mood": mood,
        "score": max(0, score)
    }

# 🌐 HOME ROUTE
@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    global user_filters

    if request.method == "POST":

        song = request.form.get("song", "").strip()

        filters = request.form.get("filters", "")
        if filters:
            user_filters = [f.strip().lower() for f in filters.split(",")]
        else:
            user_filters = []

        if song:

            history.append(song)

            data = sp.search(q=song, type="track", limit=1)

            if data["tracks"]["items"]:

                track = data["tracks"]["items"][0]

                song_name = track["name"]
                artist = track["artists"][0]["name"]
                cover = track["album"]["images"][0]["url"]

                preview = track.get("preview_url")
                spotify_url = track["external_urls"]["spotify"]

                # 🎤 LYRICS
                try:
                    song_data = genius.search_song(song_name, artist)
                    lyrics = song_data.lyrics if song_data else "Söz bulunamadı"
                except:
                    lyrics = "Söz yüklenemedi"

                # 🚫 FILTER CHECK
                if user_filters and any(word in lyrics.lower() for word in user_filters):

                    result = {
                        "song": "Bu şarkı filtrelendi",
                        "artist": "-",
                        "lyrics": "Kullanıcı filtresine takıldı",
                        "profanity": 0,
                        "mood": "Blocked",
                        "score": 0,
                        "preview": None,
                        "spotify_url": None,
                        "recommendations": [
    {
        "name": song,
        "cover": get_cover(song)
    }
    for song in recommendations[vibe_key]
]
                    }

                    return render_template("index.html", result=result, history=history)

                # 🎧 ANALYZE
                analysis = analyze(lyrics)

                profanity = analysis["profanity"]
                mood = analysis["mood"]
                score = analysis["score"]
                romantic = analysis["romantic"]
                energy = analysis["energy"]
                sadness = analysis["sadness"]

                # 🎯 VIBE
                if score > 80:
                    vibe_key = "happy"
                elif mood == "Yoğun içerik":
                    vibe_key = "energy"
                elif score < 50:
                    vibe_key = "sad"
                else:
                    vibe_key = "neutral"

                suggestions = recommendations[vibe_key]

                # 🎧 RESULT
                result = {
                    "song": song_name,
                    "artist": artist,
                    "cover": cover,
                    "lyrics": lyrics,
                    "profanity": profanity,
                    "mood": mood,
                    "score": score,
                    "preview": preview,
                    "spotify_url": spotify_url,
                    "recommendations": [
    {
        "name": song,
        "cover": get_cover(song)
    }
    for song in suggestions
],
                    "romantic": romantic,
                    "energy": energy,
                    "sadness": sadness,
                }

            else:

                result = {
                    "song": "Bulunamadı",
                    "artist": "-",
                    "lyrics": "",
                    "profanity": 0,
                    "mood": "Yok",
                    "score": 0,
                    "preview": None,
                    "spotify_url": None,
                    "recommendations": []
                }

    return render_template(
        "index.html",
        result=result,
        history=history
    )


# 🔍 SUGGEST
SONG_SUGGESTIONS = [
    "bad guy",
    "shape of you",
    "believer",
    "blinding lights",
    "someone you loved",
    "faded",
    "starboy",
    "lovely"
]

@app.route("/suggest")
def suggest():
    q = request.args.get("q", "").lower()
    results = [s for s in SONG_SUGGESTIONS if q in s.lower()]
    return {"results": results}


# 🚀 START
if __name__ == "__main__":
    print("FLASK START")
    app.run(debug=True)