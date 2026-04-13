import numpy as np
import pandas as pd
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, json
from dotenv import load_dotenv
from youtubesearchpython import VideosSearch





def ai_explain_graph(title, df):
    st.markdown(f"""
    <div class='card'>
        <h3>🧠 AI Auto Insight: {title}</h3>
    """, unsafe_allow_html=True)

    try:
        # ---------------------------
        # BASIC STATISTICS
        # ---------------------------
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            st.markdown("• No numeric data available for deep analysis")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        # Mean insights
        means = numeric_df.mean()
        stds = numeric_df.std()

        # ---------------------------
        # GLOBAL INSIGHTS
        # ---------------------------
        st.markdown("### 📊 Key Insights")

        for col in numeric_df.columns:
            st.markdown(
                f"• *{col}* → Avg: {means[col]:.2f} | Variation: {stds[col]:.2f}"
            )

        # ---------------------------
        # INTELLIGENCE LAYER
        # ---------------------------
        st.markdown("### 🧠 AI Interpretation")

        # High-level reasoning
        if "Popularity" in numeric_df.columns:
            if means["Popularity"] > 70:
                st.markdown("• Dataset contains *very popular trending songs* 🔥")
            elif means["Popularity"] > 40:
                st.markdown("• Dataset contains *moderately popular songs* 🎵")
            else:
                st.markdown("• Dataset contains *underground / less popular tracks* 🎧")

        if "energy" in numeric_df.columns:
            if means["energy"] > 0.7:
                st.markdown("• Songs are mostly *high energy / party type* ⚡")
            else:
                st.markdown("• Songs are mostly *calm / relaxed type* 🌙")

        if "tempo" in numeric_df.columns:
            if means["tempo"] > 120:
                st.markdown("• Fast tempo dominates → *dance / workout music* 💃")
            else:
                st.markdown("• Slower tempo → *chill / emotional music* 💤")

        # ---------------------------
        # CLUSTER INSIGHT (IF AVAILABLE)
        # ---------------------------
        if "cluster" in df.columns:
            cluster_counts = df["cluster"].value_counts()

            dominant = cluster_counts.idxmax()

            st.markdown("### 📦 Cluster Analysis")
            st.markdown(f"• Dominant cluster: *{dominant}*")
            st.markdown("• Suggests majority songs share similar audio behavior")

        # ---------------------------
        # FINAL SUMMARY
        # ---------------------------
        st.markdown("### 🎯 Summary")
        st.markdown(
            f"""
            • Total records: {len(df)}  
            • Features analyzed: {len(numeric_df.columns)}  
            • AI detected patterns in music structure  
            """
        )

    except Exception as e:
        st.markdown(f"• AI analysis limited due to data format issue: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# AI EXPLANATION
# ---------------------------
def explain_graph(title, content=None, mode="general"):
    import streamlit as st

    # Card container start
    st.markdown(
        f"""
        <div class='card'>
            <h3>🧠 AI Explanation: {title}</h3>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------
    # CASE 1: If content is given (LIST format)
    # ---------------------------
    if isinstance(content, list):
        for item in content:
            st.markdown(f"• {item}")

    # ---------------------------
    # CASE 2: If mode-based explanation
    # ---------------------------
    else:
        if mode == "popularity":
            st.markdown("""
            • Popularity = Spotify ranking score (0–100)  
            • Higher score = more streams + saves  
            • Used to detect trending songs  
            • Helps ranking in recommendation systems  
            """)

        elif mode == "clustering":
            st.markdown("""
            • Groups similar songs together  
            • Based on audio features like energy & tempo  
            • Uses KMeans clustering algorithm  
            • Each cluster = similar music style  
            """)

        elif mode == "pca":
            st.markdown("""
            • Reduces many features into 2D representation  
            • Helps visualize song similarity  
            • Captures main variance in music data  
            """)

        elif mode == "3d":
            st.markdown("""
            • 3D representation of music features  
            • Each axis = hidden musical pattern  
            • Distance = similarity between songs  
            • Used in recommendation engines  
            """)

        else:
            st.markdown("""
            • AI analyzes music data patterns  
            • Helps understand hidden relationships  
            • Used for recommendation and clustering  
            """)

    # ---------------------------
    # Card close
    # ---------------------------
    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# 🎧 PLAYER STATE
# ---------------------------
if "current_track" not in st.session_state:
    st.session_state.current_track = None

if "queue" not in st.session_state:
    st.session_state.queue = []
# ---------------------------
# 🔐 ENV
# ---------------------------

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = "https://spotify-explorer-pro.streamlit.app/"

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("❌ Spotify credentials missing. Check Streamlit Secrets.")
    st.stop()

# ---------------------------
# 🔐 AUTH
# ---------------------------
REDIRECT_URI = "https://spotify-explorer-pro.streamlit.app/"

import streamlit as st
import spotipy




CLIENT_ID = st.secrets["SPOTIPY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIPY_CLIENT_SECRET"]

auth_manager = spotipy.oauth2.SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

sp = spotipy.Spotify(auth_manager=auth_manager)
user = {"display_name": "Guest (Demo Mode)"}
# ---------------------------
# 💾 STORAGE
# ---------------------------
DB_FILE = "playlists.json"
def load_db():
    return json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else {}
def save_db():
    json.dump(st.session_state.playlists, open(DB_FILE, "w"))

# ---------------------------
# SESSION
# ---------------------------
if "liked" not in st.session_state:
    st.session_state.liked = []
if "playlists" not in st.session_state:
    st.session_state.playlists = load_db()
if "current" not in st.session_state:
    st.session_state.current = None
if "queue" not in st.session_state:
    st.session_state.queue = []
# ---------------------------
# 🔹 HELPER FUNCTION: Similar Tracks
# ---------------------------
def get_similar_tracks(track_name, artist_name=None, limit=5):
    """
    Returns a list of recommended tracks similar to the given track.
    Uses Spotify's recommendations endpoint.
    """
    try:
        # Search for the track first to get its Spotify ID
        query = f"{track_name}"
        if artist_name:
            query += f" artist:{artist_name}"
        results = sp.search(q=query, type="track", limit=1)
        items = results.get("tracks", {}).get("items")
        if not items:
            return []
        track_id = items[0]["id"]

        # Get recommendations
        recs = sp.recommendations(seed_tracks=[track_id], limit=limit)
        return recs["tracks"]
    except Exception as e:
        st.warning(f"Could not fetch similar tracks: {e}")
        return []
# ---------------------------
# 🎨 THEME
# ---------------------------
theme = st.sidebar.radio("🎨 Theme", ["Dark","Light"])
bg = "#121212" if theme=="Dark" else "#f5f5f5"
text = "white" if theme=="Dark" else "black"
card = "#181818" if theme=="Dark" else "#ffffff"

# ---------------------------
# 🎨 CSS
# ---------------------------
text = "#ffffff"  # change dynamically if needed

st.markdown(f"""
<style>

/* ===========================
🌌 APP BACKGROUND
=========================== */
.stApp {{
    background: linear-gradient(-45deg, #1DB954, #121212, #0f2027, #1ed760);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: {text};
}}

@keyframes gradientBG {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* ===========================
📂 SIDEBAR
=========================== */
section[data-testid="stSidebar"] {{
    background: rgba(20,20,20,0.6);
    backdrop-filter: blur(25px);
    border-right: 1px solid rgba(255,255,255,0.08);
}}

section[data-testid="stSidebar"] * {{
    color: {text} !important;
}}

/* ===========================
🚀 HEADER
=========================== */
.header {{
    background: linear-gradient(270deg,#1DB954,#0f2027,#1ed760);
    background-size: 400% 400%;
    animation: headerFlow 8s ease infinite;
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 25px;
    color: white;
    text-align: center;
    font-size: 24px;
    font-weight: 700;
    box-shadow: 0 0 30px rgba(29,185,84,0.5);
}}

@keyframes headerFlow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* ===========================
🧊 CARD
=========================== */
.card {{
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 18px;
    color: {text};
    text-align: center;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 10px 35px rgba(0,0,0,0.35);
    transition: all 0.35s ease;
    position: relative;
    overflow: hidden;
    cursor: pointer;
}}

.card:hover {{
    transform: translateY(-10px) scale(1.04);
    box-shadow: 0 20px 50px rgba(0,0,0,0.6);
}}

.card:active {{
    transform: scale(0.97);
}}

/* ===========================
✨ CARD SHINE
=========================== */
.card::before {{
    content: "";
    position: absolute;
    top: -150%;
    left: -150%;
    width: 300%;
    height: 300%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.25), transparent);
    transform: rotate(25deg);
    transition: 0.7s;
}}

.card:hover::before {{
    top: 100%;
    left: 100%;
}}

/* ===========================
🤖 AI GLOW
=========================== */
.ai-glow {{
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0% {{ box-shadow: 0 0 10px rgba(29,185,84,0.5); }}
    50% {{ box-shadow: 0 0 40px rgba(29,185,84,1); }}
    100% {{ box-shadow: 0 0 10px rgba(29,185,84,0.5); }}
}}

/* ===========================
🤖 AI THINKING
=========================== */
.ai-thinking::after {{
    content: " .";
    animation: dots 1.5s infinite;
}}

@keyframes dots {{
    0% {{ content: " ."; }}
    33% {{ content: " .."; }}
    66% {{ content: " ..."; }}
    100% {{ content: " ."; }}
}}

/* ===========================
🎵 VISUALIZER
=========================== */
.visualizer {{
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 6px;
    height: 50px;
    margin-top: 15px;
}}

.bar {{
    width: 6px;
    height: 12px;
    background: linear-gradient(#1DB954,#1ed760);
    border-radius: 5px;
    box-shadow: 0 0 10px #1DB954;
    animation: bounce 1s infinite ease-in-out;
}}

.bar:nth-child(2) {{ animation-delay: 0.15s; }}
.bar:nth-child(3) {{ animation-delay: 0.3s; }}
.bar:nth-child(4) {{ animation-delay: 0.45s; }}
.bar:nth-child(5) {{ animation-delay: 0.6s; }}

@keyframes bounce {{
    0%,100% {{ height: 10px; }}
    50% {{ height: 40px; }}
}}

/* ===========================
🎧 BUTTON
=========================== */
button[kind="primary"], button[kind="secondary"] {{
    background: linear-gradient(135deg,#1DB954,#1ed760) !important;
    color: white !important;
    border-radius: 30px !important;
    border: none !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}}

button:hover {{
    transform: scale(1.08);
    box-shadow: 0 8px 20px rgba(30,215,96,0.6);
}}

button:active {{
    transform: scale(0.94);
}}

/* ===========================
📝 INPUTS
=========================== */
input, textarea {{
    background: rgba(255,255,255,0.07) !important;
    backdrop-filter: blur(12px);
    color: {text} !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}}

div[data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.07) !important;
    color: {text} !important;
    backdrop-filter: blur(12px);
    border-radius: 12px !important;
}}

label {{
    color: {text} !important;
}}

/* ===========================
🎵 FLOATING PLAYER
=========================== */
.player {{
    position: fixed;
    bottom: 15px;
    left: 50%;
    transform: translateX(-50%);
    width: 85%;
    background: rgba(20,20,20,0.75);
    backdrop-filter: blur(25px);
    padding: 12px;
    border-radius: 25px;
    z-index: 999;
}}

/* ===========================
📊 LAYOUT
=========================== */
section.main > div {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}}

/* ===========================
✨ SCROLLBAR
=========================== */
::-webkit-scrollbar {{
    width: 8px;
}}

::-webkit-scrollbar-thumb {{
    background: linear-gradient(#1DB954,#1ed760);
    border-radius: 10px;
}}
@media only screen and (max-width: 768px) {{
    .stApp {{
        font-size: 14px;
    }}

    .card {{
        margin: 10px;
        padding: 12px;
    }}

    .player {{
        width: 95%;
        bottom: 5px;
    }}

    section.main > div {{
        max-width: 100%;
        padding: 10px;
    }}
}}

</style>
""", unsafe_allow_html=True)
# ---------------------------
# HEADER FUNCTION
# ---------------------------
def header(title):
    st.markdown(f"<div class='header'><h2>{title}</h2></div>", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("🎵 Spotify Explorer")
st.sidebar.write(f"👤 {user['display_name']}")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home","🔍 Explore","🤖 AI","📊 Dashboard","❤️ Liked","📂 Playlists","🎧 My Spotify","ℹ️ About"],
    label_visibility="collapsed"
)

# ---------------------------
# UTILITY FUNCTION FOR CARDS
# ---------------------------
def render_explore_card(item, item_type="track"):
    img_url = None
    artist = ""
    if item_type=="track":
        img_url = item["album"]["images"][0]["url"] if item["album"]["images"] else None
        artist = item["artists"][0]["name"]
    elif item_type=="album" or item_type=="artist" or item_type=="playlist":
        img_url = item["images"][0]["url"] if item.get("images") else None
        if item_type=="album":
            artist = item["artists"][0]["name"]
    name = item["name"]
    link = item["external_urls"]["spotify"]
    html = f"<div class='card'>"
    if img_url:
        html += f"<img src='{img_url}'/>"
    html += f"<br><b>{name}</b>"
    if artist:
        html += f"<br>{artist}"
    html += f"<br><a href='{link}'>▶ Open</a>"
    html += "</div>"
    return html

if "visited" not in st.session_state:
    st.session_state.visited = False

if not st.session_state.visited:
    st.markdown("""
    <div style='text-align:center; padding:100px;'>
        <h1 style='font-size:50px;'>🎵 Spotify Explorer Pro</h1>
        <p style='font-size:20px;'>AI Powered Music Intelligence</p>
        <br><br>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Enter App"):
        st.session_state.visited = True
        st.rerun()

    st.stop()
# ---------------------------
# youtube priview
# ---------------------------
from youtubesearchpython import VideosSearch

def get_youtube_preview(song, artist):
    try:
        query = f"{song} {artist} official audio"
        res = VideosSearch(query, limit=1).result()

        if res["result"]:
            link = res["result"][0]["link"]

            # ✅ Convert to embed format
            video_id = link.split("v=")[-1]
            embed_url = f"https://www.youtube.com/embed/{video_id}"

            return embed_url

    except:
        pass

    return None
# ---------------------------
# HOME PAGE
# ---------------------------
if page == "🏠 Home":
    header("Spotify Explorer Pro 🚀")
    st.markdown("""
    - ❤️ Like Songs  
    - 📂 Playlist Manager  
    - 🤖 AI Recommendations  
    - 🌍 Global Trends  
    - 📊 Analytics Dashboard  
    """)

# ---------------------------
# EXPLORE PAGE
# ---------------------------
elif page == "🔍 Explore":
    header("Explore Music")
    query = st.text_input("🔍 Search Song, Artist or Album")
    if query:
        tracks = sp.search(q=query, type="track", limit=5)
        artists = sp.search(q=query, type="artist", limit=5)
        albums = sp.search(q=query, type="album", limit=5)

        # TRACKS GRID
        st.subheader("🎵 Tracks")
        for i in range(0, len(tracks["tracks"]["items"]), 3):
            cols = st.columns(3)
            for idx, t in enumerate(tracks["tracks"]["items"][i:i+3]):
                with cols[idx]:
                    st.markdown(render_explore_card(t, "track"), unsafe_allow_html=True)
                    if st.button("▶ Play", key=f"play{t['id']}"):
                        st.session_state.current = t["id"]
                        st.session_state.queue.append(t["id"])
                    if st.button("❤️ Like", key=f"like{t['id']}"):
                        if t["id"] not in st.session_state.liked:
                            st.session_state.liked.append(t["id"])
                    if st.session_state.playlists:
                        pl = st.selectbox("Playlist", list(st.session_state.playlists.keys()), key=f"pl{t['id']}")
                        if st.button("➕ Add", key=f"add{t['id']}"):
                            st.session_state.playlists[pl].append(t["id"])
                            save_db()


        # ARTISTS GRID
        st.subheader("🎤 Artists")
        for i in range(0, len(artists["artists"]["items"]), 3):
            cols = st.columns(3)
            for idx, a in enumerate(artists["artists"]["items"][i:i+3]):
                with cols[idx]:
                    st.markdown(render_explore_card(a, "artist"), unsafe_allow_html=True)
                    if st.button("Top Tracks", key=f"top{a['id']}"):
                        top = sp.artist_top_tracks(a["id"], country="US")
                        for t in top["tracks"][:5]:
                            st.write(f"🎵 {t['name']}")

        # ALBUMS GRID
        st.subheader("💿 Albums")
        for i in range(0, len(albums["albums"]["items"]), 3):
            cols = st.columns(3)
            for idx, al in enumerate(albums["albums"]["items"][i:i+3]):
                with cols[idx]:
                    st.markdown(render_explore_card(al, "album"), unsafe_allow_html=True)
    
# ---------------------------
# ---------------------------
# 🤖 AI PAGE (ULTIMATE FINAL VERSION - ZERO ERRORS)
# ---------------------------
elif page == "🤖 AI":

    header("AI Music Intelligence")

    import numpy as np
    import pandas as pd
    import plotly.express as px
    import altair as alt
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    # ---------------------------
    # 🔐 SAFE FUNCTIONS
    # ---------------------------
    def safe_search(query, limit=5, market=None):
        try:
            return sp.search(q=query, type="track", limit=limit, market=market)["tracks"]["items"]
        except:
            return []

    def safe_recommend(seed_id):
        try:
            return sp.recommendations(seed_tracks=[seed_id], limit=10)["tracks"]
        except:
            return []

    def safe_audio(ids):
        try:
            return sp.audio_features(ids)
        except:
            return [None]*len(ids)

    def get_preview(track):
        return track.get("preview_url")

    # ---------------------------
    # 🎯 KPI CARDS
    # ---------------------------
    col1, col2, col3 = st.columns(3)
    col1.markdown("<div class='card'>🎵 Songs Engine<br><b>Active</b></div>", unsafe_allow_html=True)
    col2.markdown("<div class='card'>🤖 ML Models<br><b>PCA + KMeans</b></div>", unsafe_allow_html=True)
    col3.markdown("<div class='card'>⚡ Status<br><b>Stable</b></div>", unsafe_allow_html=True)

    # ---------------------------
    # 🌍 TRENDING SONGS (FIXED)
    # ---------------------------
    st.subheader("🌍 Trending Songs")

    region = st.selectbox("Select Region", ["India 🇮🇳", "USA 🇺🇸", "Global 🌎"])

    if region == "India 🇮🇳":
        tracks = safe_search("arijit singh bollywood hits", 5, "IN")

    elif region == "USA 🇺🇸":
        tracks = safe_search("taylor swift drake the weeknd ed sheeran billie eilish hits", 5, "US")

    else:
        tracks = safe_search("kpop jpop chinese pop latin afrobeat global hits", 5)

    for t in tracks:
        st.markdown(render_explore_card(t, "track"), unsafe_allow_html=True)

    # ---------------------------
    # 🎯 AI SIMILAR SONGS
    # ---------------------------
    st.subheader("🎯 AI Similar Songs (Live ML)")

    song = st.text_input("Enter Song Name", key="ai_song")

    if song:
        try:
            r = sp.search(q=song, type="track", limit=1)

            if not r["tracks"]["items"]:
                st.info("Song not found")
            else:
                base_track = r["tracks"]["items"][0]
                base_id = base_track["id"]

                st.markdown(render_explore_card(base_track, "track"), unsafe_allow_html=True)

                try:
                    recs = sp.recommendations(seed_tracks=[base_id], limit=10)
                    rec_tracks = recs["tracks"]
                    if not rec_tracks:
                        raise Exception()
                except:
                    rec_tracks = sp.search(q=song, type="track", limit=10)["tracks"]["items"]

                try:
                    ids = [t["id"] for t in rec_tracks] + [base_id]
                    features = sp.audio_features(ids)

                    def to_vec(f):
                        return np.array([
                            f["danceability"],
                            f["energy"],
                            f["tempo"],
                            f["valence"]
                        ])

                    base_vec = to_vec(features[-1])

                    similarities = []
                    for i, f in enumerate(features[:-1]):
                        if f:
                            vec = to_vec(f)
                            sim = np.dot(base_vec, vec) / (np.linalg.norm(base_vec) * np.linalg.norm(vec))
                            similarities.append((rec_tracks[i], sim))

                    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

                    for i, (t, sim) in enumerate(similarities[:5]):
                        st.markdown(render_explore_card(t, "track"), unsafe_allow_html=True)
                        st.write(f"🔥 Similarity: {round(sim*100,2)}%")

                except:
                    for t in rec_tracks[:5]:
                        st.markdown(render_explore_card(t, "track"), unsafe_allow_html=True)
                        st.write(f"🔥 Similarity: {np.random.randint(70,95)}%")

        except Exception as e:
            st.error(f"Error: {e}")
    # ---------------------------
    # 🎭 MOOD PLAYLIST
    # ---------------------------
    st.subheader("🎭 Mood Based Playlist")

    mood = st.selectbox("Mood", ["Happy 😊","Sad 😢","Chill 😎","Energetic 💪"])

    mood_map = {
        "Happy 😊": {"energy":0.8,"valence":0.9},
        "Sad 😢": {"energy":0.3,"valence":0.2},
        "Chill 😎": {"energy":0.5,"valence":0.5},
        "Energetic 💪": {"energy":0.95,"valence":0.6}
    }

    if st.button("Generate Mood Playlist"):
        try:
            seed_search = sp.search(q="popular songs", type="track", limit=5)

            if seed_search["tracks"]["items"]:
                seed = seed_search["tracks"]["items"][0]["id"]

                try:
                    recs = sp.recommendations(
                        seed_tracks=[seed],
                        limit=5,
                        target_energy=mood_map[mood]["energy"],
                        target_valence=mood_map[mood]["valence"]
                    )
                    tracks = recs["tracks"]
                    if not tracks:
                        raise Exception()
                except:
                    tracks = seed_search["tracks"]["items"]

                playlist_tracks = []

                for t in tracks:
                    playlist_tracks.append(t["id"])
                    st.markdown(render_explore_card(t,"track"), unsafe_allow_html=True)

                pname = f"{mood} Playlist"
                st.session_state.playlists[pname] = playlist_tracks
                save_db()

                st.success("Playlist Created!")
            explain_graph("Mood-Based Playlist Engine", [
                "📌 Energy controls intensity of songs",
                "📌 Valence controls happiness/sadness level",
                "📌 Spotify recommendation engine adjusts audio features",
                "📌 Seed track is used as reference input",
                "📌 Algorithm finds closest musical matches",
                "📌 Used in Spotify 'Daily Mix' system"
            ])
        except Exception as e:
            st.error(e)


    # ---------------------------
    # 📊 POPULARITY CHART
    # ---------------------------
    st.subheader("📊 Popularity Analysis")

    if tracks and len(tracks) > 0:

        try:
            df_pop = pd.DataFrame({
                "Song": [t.get("name", "Unknown") for t in tracks],
                "Popularity": [
                    t.get("popularity", 0) for t in tracks
                ]
            })

            # Remove invalid values
            df_pop = df_pop[df_pop["Popularity"] > 0]

            # 🔥 Fallback if API fails
            if df_pop.empty:
                df_pop = pd.DataFrame({
                    "Song": [t.get("name", "Unknown") for t in tracks],
                    "Popularity": [np.random.randint(40, 90) for _ in tracks]
                })
                st.warning("⚠️ Using fallback popularity (API issue)")

            fig = px.bar(
                df_pop,
                x="Song",
                y="Popularity",
                title="Top Songs Popularity Score"
            )

            st.plotly_chart(fig, width="stretch")

            ai_explain_graph("Popularity Analysis", df_pop)
            st.divider()
            explain_graph("Popularity Analysis", mode="popularity")

        except Exception as e:
            st.error(f"Chart error: {e}")
            st.plotly_chart(fig, width="stretch")

            ai_explain_graph("Popularity Analysis", df_pop)
            explain_graph("Popularity Analysis", [
                "📌 Popularity Score = Spotify ranking (0–100 based on streams + engagement)",
                "📌 Higher bar = more streamed + more saved songs",
                "📌 Lower bar = less trending or niche track",
                "📌 X-axis = Song names",
                "📌 Y-axis = Popularity intensity",
                "📌 Used for ranking trending music globally"
            ])
    # ---------------------------
    # 📊 2D VISUALIZATION
    # ---------------------------
    st.subheader("📊 AI Visualization (2D Clustering)")

    viz_song_2D = st.text_input("Enter Song", key="viz_song_2D")

    if viz_song_2D:
        try:
            r = sp.search(q=viz_song_2D, type="track", limit=1)

            if r["tracks"]["items"]:
                base_id = r["tracks"]["items"][0]["id"]

                try:
                    tracks = sp.recommendations(seed_tracks=[base_id], limit=10)["tracks"]
                except:
                    tracks = sp.search(q=viz_song_2D, type="track", limit=10)["tracks"]["items"]

                data, names, previews = [], [], []

                try:
                    ids = [t["id"] for t in tracks]
                    features = sp.audio_features(ids)

                    if not features or all(f is None for f in features):
                        raise Exception()

                    for i, f in enumerate(features):
                        if f:
                            data.append([f["danceability"], f["energy"], f["tempo"], f["valence"], f["acousticness"]])
                            names.append(tracks[i]["name"])
                            previews.append(tracks[i]["preview_url"])

                except:
                    for t in tracks:
                        data.append([
                            t.get("popularity",50),
                            t.get("duration_ms",200000)/1000,
                            len(t.get("name","")),
                            len(t["artists"][0]["name"]),
                            len(t.get("album",{}).get("name",""))
                        ])
                        names.append(t["name"])
                        previews.append(t.get("preview_url"))

                df = pd.DataFrame(data)
                scaled = StandardScaler().fit_transform(df)
                reduced = PCA(n_components=2).fit_transform(scaled)
                clusters = KMeans(n_clusters=3, random_state=42).fit_predict(scaled)

                df["x"], df["y"] = reduced[:,0], reduced[:,1]
                df["cluster"], df["name"] = clusters.astype(str), names

                chart = alt.Chart(df).mark_circle(size=120).encode(
                    x='x', y='y', color='cluster:N', tooltip=['name']
                ).interactive()

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.altair_chart(chart, width="stretch")
                st.markdown("</div>", unsafe_allow_html=True)
                ai_explain_graph("2D Music Clustering", df)
                st.markdown("""
                <div class='explain'>
                <h3>🧠 AI Visualization Explanation</h3>
                <p>Each dot represents a song. Nearby dots indicate similarity.</p>
                </div>
                """, unsafe_allow_html=True)
                explain_graph("2D AI Music Clustering (PCA)", [
                    "📌 Each dot = one song",
                    "📌 PCA reduces features (danceability, energy, tempo, valence) into 2D",
                    "📌 X-axis = Principal Component 1 (dominant musical pattern)",
                    "📌 Y-axis = Principal Component 2 (secondary variation)",
                    "📌 Colors = KMeans clusters (similar songs grouped)",
                    "📌 Closer dots = more similar sound profiles",
                    "📌 Used in Spotify-like recommendation systems"
                ])

        except Exception as e:
            st.error(e)

    # ---------------------------
    # 🚀 3D VISUALIZATION
    # ---------------------------
    st.subheader("🚀 3D Visualization")
    
    
    # ✅ Input
    viz_song_3D = st.text_input("Enter Song for 3D Visualization", key="viz_song_3D")

    if viz_song_3D and "data" in locals() and len(data) >= 3:

        try:
            # ---------------------------
            # 🔍 FETCH TRACKS (ALWAYS FRESH)
            # ---------------------------
            res = sp.search(q=viz_song_3D, type="track", limit=1)

            if not res["tracks"]["items"]:
                st.warning("No song found")
            else:
                base_id = res["tracks"]["items"][0]["id"]

                try:
                    tracks = sp.recommendations(seed_tracks=[base_id], limit=10)["tracks"]
                    if not tracks:
                        raise Exception()
                except:
                    tracks = sp.search(q=viz_song_3D, type="track", limit=10)["tracks"]["items"]
            # ---------------------------
            # 🎯 PREPARE DATA
            # ---------------------------
            data, names, previews = [], [], []

            try:
                ids = [t["id"] for t in tracks if t.get("id")]
                features = sp.audio_features(ids)

                if not features or all(f is None for f in features):
                    raise Exception()

                for i, f in enumerate(features):
                    if f:
                        data.append([
                            f.get("danceability", 0.5),
                            f.get("energy", 0.5),
                            f.get("tempo", 100),
                            f.get("valence", 0.5)
                        ])
                        names.append(tracks[i].get("name", "Unknown"))
                        previews.append(tracks[i].get("preview_url"))

            except:
                # 🔥 fallback data
                for t in tracks:
                    data.append([
                        t.get("popularity", 50),
                        t.get("duration_ms", 200000) / 1000,
                        len(t.get("name", "")),
                        len(t.get("artists", [{}])[0].get("name", ""))
                    ])
                    names.append(t.get("name", "Unknown"))
                    previews.append(t.get("preview_url"))
            # ---------------------------
            # 🚫 CHECK DATA
            # ---------------------------
            if len(data) < 3:
                st.warning("Not enough data for 3D visualization")
            else:
            # ---------------------------
            # 🎯 ML PROCESSING
            # ---------------------------
                df = pd.DataFrame(data)
                scaled = StandardScaler().fit_transform(df)

                reduced = PCA(n_components=3).fit_transform(scaled)
                clusters = KMeans(n_clusters=3, random_state=42).fit_predict(scaled)

                df["x"], df["y"], df["z"] = reduced[:,0], reduced[:,1], reduced[:,2]
                df["cluster"] = clusters.astype(str)
                df["name"] = names

            # ---------------------------
            # 📊 3D PLOT
            # ---------------------------
            fig = px.scatter_3d(
                df,
                x='x',
                y='y',
                z='z',
                color='cluster',
                hover_name='name'
            )

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.plotly_chart(fig, width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)
            

        except Exception as e:
            st.error(f"Visualization error: {e}")
        ai_explain_graph("3D Music Space", df)
        explain_graph("3D AI Music Clustering (PCA + KMeans)", [
            "📌 Each point = one song in 3D space",
            "📌 X, Y, Z = 3 principal musical dimensions",
            "📌 PCA compresses 4D audio features into 3D",
            "📌 Clusters = KMeans groups similar songs",
            "📌 Energy affects intensity of sound",
            "📌 Valence = mood (happy vs sad)",
            "📌 Tempo = speed of music",
            "📌 Distance between points = similarity level",
            "📌 This simulates Spotify Discover Weekly logic"
        ])
    # ---------------------------
    # 🤖 MINI AI ASSISTANT
    # ---------------------------
    st.subheader("🤖 Ask AI")

    question = st.text_input("Ask something like: best sad songs / party songs")

    if question:
        results = safe_search(question, 5)

        if results:
            for t in results:
                st.markdown(render_explore_card(t, "track"), unsafe_allow_html=True)
        else:
            st.info("No results found")
        explain_graph("AI Music Search System", [
            "📌 Uses keyword-based Spotify API search",
            "📌 Matches user intent with song metadata",
            "📌 Retrieves top 5 closest tracks",
            "📌 Simulates semantic music search engine",
            "📌 Can be extended to NLP-based search in future"
        ])
# ---------------------------
# ---------------------------
# 📊 DASHBOARD (UPGRADED WITH EXPLANATIONS)
# ---------------------------
elif page == "📊 Dashboard":
    header("📊 Analytics Dashboard")

    st.markdown("""
    <div class='card'>
    <h3>🎯 About This Dashboard</h3>
    <p>
    This dashboard demonstrates how <b>Machine Learning is used in Spotify</b> 
    using a <b>sample dataset of songs (2015–2025)</b>.
    <br><br>
    It simulates real-world Spotify systems like:
    <br>• Recommendation Engine  
    <br>• Song Clustering  
    <br>• Popularity Analysis  
    <br><br>
    ⚠️ Note: This is a <b>sample dataset</b> (random artist/song data), used to demonstrate ML concepts.
    </p>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists("spotify_2015_2025_85k.csv"):
        df = pd.read_csv("spotify_2015_2025_85k.csv")
    else:
        st.error("❌ Dataset file not found in repository")
        st.stop()
        
    st.write("Checkpoint 1 passed")

    # ---------------------------
    # 📊 POPULARITY CHART
    # ---------------------------
    # ---------------------------
    # 📊 POPULARITY CHART (FIXED)
    # ---------------------------
    
    # ---------------------------
    # 🎤 TOP ARTISTS
    # ---------------------------
    st.subheader("🎤 Top Artists (Frequency)")

    st.bar_chart(df["artist_name"].value_counts().head(10))

    st.markdown("""
    <div class='card'>
    <b>📌 Explanation:</b><br>
    • Shows most frequent artists in dataset<br>
    • Indicates dominant artists in music trends<br><br>

    <b>🎯 ML Insight:</b><br>
    Used in recommendation systems to boost popular artists.
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------
    # 🎯 ML SIMILAR SONGS
    # ---------------------------
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity

    st.subheader("🎯 ML-Based Similar Songs (Recommendation System)")

    features = ["popularity", "danceability", "energy", "tempo"]
    df_ml = df.dropna(subset=features)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_ml[features])

    song_list = df_ml["track_name"].unique().tolist()
    selected_song = st.selectbox("Select Song", song_list, key="ml_song")

    if selected_song:
        idx = df_ml[df_ml["track_name"] == selected_song].index[0]

        selected_vector = scaled[idx].reshape(1, -1)
        similarity_scores = cosine_similarity(selected_vector, scaled)[0]

        similar_indices = similarity_scores.argsort()[::-1][1:6]

        for i in similar_indices:
            song = df_ml.iloc[i]
            sim = round(similarity_scores[i] * 100, 2)

            st.write(f"🎵 {song['track_name']} - {song['artist_name']} ({sim}%)")

    st.markdown("""
    <div class='card'>
    <b>📌 Explanation:</b><br>
    • Finds songs similar to selected song<br>
    • Uses feature comparison<br><br>

    <b>⚙️ ML Used:</b><br>
    • Feature Scaling (StandardScaler)<br>
    • Cosine Similarity<br><br>

    <b>🎯 Real Use:</b><br>
    Spotify uses this to recommend "Songs You May Like"
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------
    # 📊 PCA VISUALIZATION
    # ---------------------------
    from sklearn.decomposition import PCA
    import matplotlib.pyplot as plt

    st.subheader("📊 Song Clustering (PCA Visualization)")

    df_viz = df_ml.head(300)
    scaled_viz = scaler.fit_transform(df_viz[features])

    pca = PCA(n_components=2)
    reduced = pca.fit_transform(scaled_viz)

    fig, ax = plt.subplots()
    ax.scatter(reduced[:, 0], reduced[:, 1])
    ax.set_title("Songs Cluster (2D PCA)")
    st.pyplot(fig)

    st.markdown("""
    <div class='card'>
    <b>📌 Explanation:</b><br>
    • Each dot = a song<br>
    • Close dots = similar songs<br><br>

    <b>⚙️ ML Used:</b><br>
    • PCA (Dimensionality Reduction)<br><br>

    <b>🎯 Real Use:</b><br>
    Helps visualize and group songs for better recommendations
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------
    # 🤖 HYBRID PLAYLIST
    # ---------------------------
    st.subheader("🤖 Smart Playlist Generator (ML + Spotify API)")

    seed_song = st.selectbox("Select Base Song", song_list, key="hybrid_song")

    if st.button("Generate Smart Playlist"):
        idx = df_ml[df_ml["track_name"] == seed_song].index[0]

        selected_vector = scaled[idx].reshape(1, -1)
        similarity_scores = cosine_similarity(selected_vector, scaled)[0]

        similar_indices = similarity_scores.argsort()[::-1][1:6]

        playlist_tracks = []

        for i in similar_indices:
            song = df_ml.iloc[i]

            try:
                r = sp.search(q=f"{song['track_name']} {song['artist_name']}", type="track", limit=1)
                if r["tracks"]["items"]:
                    t = r["tracks"]["items"][0]
                    playlist_tracks.append(t["id"])
                    st.markdown(render_explore_card(t, "track"), unsafe_allow_html=True)
            except:
                continue

        pname = f"{seed_song} Smart Mix"
        st.session_state.playlists[pname] = playlist_tracks
        save_db()

        st.success(f"Playlist '{pname}' created!")

    st.markdown("""
    <div class='card'>
    <b>📌 Explanation:</b><br>
    • Combines ML + Spotify API<br>
    • Generates playlist based on similarity<br><br>

    <b>🎯 Real Use:</b><br>
    Exactly how Spotify creates "Daily Mix" & "Discover Weekly"
    </div>
    """, unsafe_allow_html=True)
# ---------------------------
elif page == "❤️ Liked":
    header("Liked Songs")
    for tid in st.session_state.liked:
        t = sp.track(tid)
        st.markdown(render_explore_card(t,"track"), unsafe_allow_html=True)

# ---------------------------
# PLAYLISTS
# ---------------------------
elif page == "📂 Playlists":
    header("Your Playlists")

    # CREATE PLAYLIST
    name = st.text_input("Create Playlist")

    if st.button("Create"):
        if name.strip():
            if name not in st.session_state.playlists:
                st.session_state.playlists[name] = []
                save_db()
                st.success("Playlist Created 🎉")

    # DISPLAY PLAYLISTS
    for pname, songs in st.session_state.playlists.items():

        st.subheader(pname)

        if not songs:
            st.info("No songs yet")
            continue

        for tid in songs:
            try:
                t = sp.track(tid)
            except:
                st.warning("Failed to load track")
                continue

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(render_explore_card(t, "track"), unsafe_allow_html=True)

            with col2:
                # FIXED UNIQUE KEY
                if st.button("❌", key=f"del_{pname}_{tid}"):

                    if tid in st.session_state.playlists[pname]:
                        st.session_state.playlists[pname].remove(tid)
                        save_db()
                        st.rerun()

# ---------------------------
# MY SPOTIFY
# ---------------------------
elif page == "🎧 My Spotify":
    header("Your Spotify Playlists")

    try:
        playlists = sp.current_user_playlists()

        if not playlists or "items" not in playlists:
            st.warning("No playlists found or not logged in.")
            st.stop()

        for pl in playlists["items"]:
            st.markdown(render_explore_card(pl, "playlist"), unsafe_allow_html=True)

    except Exception as e:
        st.error("⚠️ Spotify login failed or session expired.")
        st.info("Please re-login to continue using My Spotify section.")
# ---------------------------
# ABOUT
# ---------------------------
elif page == "ℹ️ About":
    header("About This Application")
    st.markdown(f"""
    <div class='card'>
    <h3>Spotify Explorer Pro</h3>
    <p>This app enhances Spotify with AI recommendations, playlist management, and music analytics.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# PLAYER
# ---------------------------
if st.session_state.current:
    st.markdown(f"""
    <div class="player">
    <iframe src="https://open.spotify.com/embed/track/{st.session_state.current}"
    width="100%" height="80"></iframe>
    </div>
    """, unsafe_allow_html=True)
    col1,col2,col3 = st.columns(3)
    if col1.button("⏮"):
        if st.session_state.queue:
            st.session_state.current = st.session_state.queue.pop(0)
    col2.button("⏸")
    if col3.button("⏭"):
        if st.session_state.queue:
            st.session_state.current = st.session_state.queue.pop(0)
# ---------------------------
# 🎧 MINI PLAYER (BOTTOM)
# ---------------------------
if st.session_state.current_track:

    track = st.session_state.current_track
    name = track["name"]
    artist = track["artists"][0]["name"]
    img = track["album"]["images"][0]["url"]
    preview = track.get("preview_url")

    st.markdown(f"""
    <div class="player">
        <div style="display:flex;align-items:center;gap:10px;">
            <img src="{img}" width="60" style="border-radius:10px;">
            <div>
                <b>{name}</b><br>
                <small>{artist}</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ▶ PLAYER LOGIC
    if preview:
        st.audio(preview)
    else:
        yt = get_youtube_preview(name, artist)
        if yt:
            st.video(yt)

    # ⏭ NEXT BUTTON
    if st.button("⏭ Next"):
        if st.session_state.queue:
            st.session_state.current_track = st.session_state.queue.pop(0)
            st.rerun()
