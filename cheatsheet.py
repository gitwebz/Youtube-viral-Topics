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
    /* Main styling */
    .main-header {
        font-size: 2.5rem;
        color: #FF0000;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .app-description {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: #333;
    }
    
    .result-card {
        background-color: #F9F9F9;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #FF0000;
        color: #333;
    }
    
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        background-color: #F0F0F0;
        border-radius: 10px;
        color: #333;
    }
    
    .metric {
        display: inline-block;
        margin-right: 1rem;
        padding: 0.3rem 0.6rem;
        background-color: #E3F2FD;
        border-radius: 5px;
        color: #333;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .section-header {
            font-size: 1.2rem;
        }
        
        .result-card {
            padding: 0.8rem;
        }
    }
    
    /* Fix text visibility */
    .stApp {
        color: #333;
    }
    
    /* Streamlit specific fixes */
    .stTextArea, .stNumberInput, .stSlider {
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<h1 class='main-header'>🔥 YouTube Viral Topics Tool</h1>", unsafe_allow_html=True)

# App Description Section
st.markdown("""
<div class="app-description">
    <h3>About This Tool</h3>
    <p>This tool helps you discover trending YouTube videos from smaller channels that are gaining traction. By analyzing viral content from channels with fewer subscribers, you can identify emerging trends and topics before they become mainstream.</p>
    
    <h3>How to Use</h3>
    <ol>
        <li><b>Enter Keywords:</b> Add relevant keywords or phrases (one per line) related to topics you want to explore</li>
        <li><b>Set Timeframe:</b> Choose how many recent days to search (1-30 days)</li>
        <li><b>Set Subscriber Threshold:</b> Maximum subscriber count for channels to include</li>
        <li><b>Fetch Data:</b> Click the button to find viral videos matching your criteria</li>
    </ol>
    
    <h3>Why Use This Tool</h3>
    <ul>
        <li>🔍 <b>Discover Emerging Trends:</b> Find viral content before it becomes mainstream</li>
        <li>📈 <b>Competitive Analysis:</b> See what's working for smaller channels</li>
        <li>💡 <b>Content Ideas:</b> Get inspiration for your own content strategy</li>
        <li>🎯 <b>Niche Exploration:</b> Identify underserved topics with growth potential</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.markdown("<h2 class='section-header'>🔧 Search Settings</h2>", unsafe_allow_html=True)

days = st.sidebar.slider("Days to Search:", min_value=1, max_value=30, value=5)
subscriber_threshold = st.sidebar.number_input("Max Subscriber Count:", min_value=0, value=3000, step=100)

st.sidebar.markdown("<h3 class='section-header'>📝 Keywords</h3>", unsafe_allow_html=True)
keywords_input = st.sidebar.text_area(
    "Enter keywords (one per line):",
    height=200,
    help="Add relevant keywords or phrases to search for"
)

# Sample keywords as placeholder
sample_keywords = """Affair Relationship Stories
Reddit Update
Reddit Relationship Advice
Reddit Cheating
AITA Update
Open Marriage
True Cheating Story
Reddit Marriage
Surviving Infidelity"""

if not keywords_input:
    st.sidebar.info("💡 Try these sample keywords:")
    st.sidebar.code(sample_keywords)

# Fetch Data Button
fetch_button = st.sidebar.button("🔍 Fetch Viral Videos", key="fetch_button")

# Main content area
if fetch_button:
    try:
        # Process keywords from user input
        keywords = [k.strip() for k in keywords_input.split("\n") if k.strip()]
        
        if not keywords:
            st.error("⚠️ Please enter at least one keyword")
            st.stop()
            
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Iterate over the list of keywords
        for i, keyword in enumerate(keywords):
            status_text.text(f"Searching for: {keyword}")
            progress_bar.progress((i + 1) / len(keywords))
            
            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }
            
            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()
            
            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                continue
                
            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]
            
            if not video_ids or not channel_ids:
                continue
                
            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()
            
            if "items" not in stats_data or not stats_data["items"]:
                continue
                
            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()
            
            if "items" not in channel_data or not channel_data["items"]:
                continue
                
            stats = stats_data["items"]
            channels = channel_data["items"]
            
            # Collect results
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))
                
                # Apply subscriber threshold filter
                if subs < subscriber_threshold:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        st.markdown(f"<h2 class='section-header'>📊 Results ({len(all_results)} videos found)</h2>", unsafe_allow_html=True)
        
        if all_results:
            # Sort results by views (descending)
            all_results = sorted(all_results, key=lambda x: x['Views'], reverse=True)
            
            for result in all_results:
                st.markdown(f"""
                <div class="result-card">
                    <h3>{result['Title']}</h3>
                    <p>{result['Description']}...</p>
                    <p><a href="{result['URL']}" target="_blank">🔗 Watch Video</a></p>
                    <div>
                        <span class="metric">👁️ {result['Views']:,} views</span>
                        <span class="metric">👥 {result['Subscribers']:,} subscribers</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"No results found for channels with fewer than {subscriber_threshold:,} subscribers.")
            
    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")

# Footer
st.markdown("""
<div class="footer">
    <p>Developed by <b>AbdQuex</b> | © {datetime.now().year}</p>
</div>
""", unsafe_allow_html=True)
