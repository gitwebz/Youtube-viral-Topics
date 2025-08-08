import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyCAApgwcHLDCzTA0MJkw7MRFU6bDaJ3Wd4"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Custom CSS for better UI
st.markdown("""
<style>
    body, .stApp {
        color: #222 !important;
        background-color: #ffffff !important;
    }

    .main-header {
        font-size: 2.5rem;
        color: #d32f2f;
        text-align: center;
        margin-bottom: 1rem;
    }

    .section-header {
        font-size: 1.5rem;
        color: #1565c0;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .app-description {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: #222;
    }

    .result-card {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #ccc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        color: #222;
    }

    .result-card h3 {
        margin: 0 0 0.5rem;
        color: #111;
    }

    .metric {
        display: inline-block;
        margin-right: 1rem;
        padding: 0.25rem 0.5rem;
        background-color: #bbdefb;
        border-radius: 5px;
        color: #111;
    }

    .footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.9rem;
        color: #444;
        padding: 1rem;
        border-top: 1px solid #ccc;
    }

    a {
        color: #0d47a1 !important;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-header'>🔥 YouTube Viral Topics Tool</div>", unsafe_allow_html=True)

# Description
st.markdown("""
<div class="app-description">
    <p>Discover trending YouTube videos from smaller channels to catch emerging trends before they go mainstream. Perfect for content creators, marketers, and trend watchers.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("🔧 Configure Search")
days = st.sidebar.slider("Search videos from last (days):", 1, 30, 7)
subscriber_threshold = st.sidebar.number_input("Max Subscribers:", 0, value=3000, step=100)
keywords_input = st.sidebar.text_area("Keywords (one per line):", height=150)
fetch_button = st.sidebar.button("🔍 Fetch Videos")

# Suggest example keywords
if not keywords_input:
    st.sidebar.markdown("**Example keywords:**")
    st.sidebar.code("""Reddit Relationship
Reddit AITA
Cheating Stories
Open Marriage
Affair Update""")

if fetch_button:
    try:
        keywords = [k.strip() for k in keywords_input.splitlines() if k.strip()]
        if not keywords:
            st.error("⚠️ Please enter at least one keyword.")
            st.stop()

        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        all_results = []
        progress_bar = st.progress(0)
        status = st.empty()

        for i, keyword in enumerate(keywords):
            status.text(f"Searching for: {keyword}")
            progress_bar.progress((i + 1) / len(keywords))

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            r = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            videos = r.json().get("items", [])

            if not videos:
                continue

            video_ids = [v["id"]["videoId"] for v in videos]
            channel_ids = [v["snippet"]["channelId"] for v in videos]

            stats_r = requests.get(YOUTUBE_VIDEO_URL, params={"part": "statistics", "id": ",".join(video_ids), "key": API_KEY})
            channel_r = requests.get(YOUTUBE_CHANNEL_URL, params={"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY})

            stats_data = stats_r.json().get("items", [])
            channel_data = channel_r.json().get("items", [])

            for v, vs, cs in zip(videos, stats_data, channel_data):
                views = int(vs["statistics"].get("viewCount", 0))
                subs = int(cs["statistics"].get("subscriberCount", 0))
                if subs <= subscriber_threshold:
                    all_results.append({
                        "Title": v["snippet"].get("title", "N/A"),
                        "Description": v["snippet"].get("description", "")[:200],
                        "URL": f"https://youtube.com/watch?v={v['id']['videoId']}",
                        "Views": views,
                        "Subscribers": subs
                    })

        progress_bar.empty()
        status.empty()

        if all_results:
            all_results.sort(key=lambda x: x['Views'], reverse=True)
            st.markdown(f"<div class='section-header'>📊 Top {len(all_results)} Videos</div>", unsafe_allow_html=True)
            for r in all_results:
                st.markdown(f"""
                <div class='result-card'>
                    <h3>{r['Title']}</h3>
                    <p>{r['Description']}...</p>
                    <a href="{r['URL']}" target="_blank">🔗 Watch Video</a>
                    <div style="margin-top: 0.5rem;">
                        <span class="metric">👁️ {r['Views']:,} views</span>
                        <span class="metric">👥 {r['Subscribers']:,} subs</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"No results found under {subscriber_threshold:,} subscribers.")

    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.markdown(f"""
<div class="footer">
    Developed by <b>AbdQuex</b> | © {datetime.now().year} | <a href="https://abdquex.online" target="_blank">abdquex.online</a>
</div>
""", unsafe_allow_html=True)
