import streamlit as st
import requests
import os
from io import BytesIO

# Default backend URL
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Voice-Based Maintenance Assistant", 
    page_icon="🎙️",
    layout="wide"
)
st.markdown("""
    <style>
    /* Glassmorphism styling for standard Streamlit containers */
    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e293b);
    }
    
    /* Modern Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 4px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94a3b8;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00FFAA;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 255, 170, 0.1) !important;
        color: #00FFAA !important;
        border-bottom: 2px solid #00FFAA;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Primary Button Style */
    .stButton > button {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #0F172A;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 15px rgba(0, 255, 170, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 255, 170, 0.5);
        color: #0F172A;
        border: none;
    }
    
    /* Input Elements */
    .stTextInput > div > div > input, .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white;
    }
    
    /* Info/Warning/Success Boxes */
    div[data-testid="stAlert"] {
        border-radius: 12px;
        backdrop-filter: blur(5px);
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Data container for structured intelligence */
    .intelligence-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #F8FAFC; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 0;'>🎙️ Autonomous Factory Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 1.1rem; margin-bottom: 2rem;'>AI-powered voice analysis and structured intelligence extraction</p>", unsafe_allow_html=True)

# Check Backend Health Note
try:
    requests.get(f"{BACKEND_URL}/docs", timeout=2)
except Exception:
    st.warning("⚠️ Backend API (FastAPI) seems unreachable. Ensure it is running on port 8000.")

# Check Ollama Health
try:
    requests.get("http://localhost:11434/", timeout=2)
except Exception:
    st.error("⚠️ Local AI Engine (Ollama) is not running! The system will fail to extract structured intelligence from transcripts. Please start the Ollama application.")

# -- UI Tabs
tab1, tab2, tab3 = st.tabs(["Analyze Voice Report", "Maintenance History Search", "System Ingestion"])

with tab1:
    st.header("Analyze Voice Report")
    
    # Audio Input Method
    input_method = st.radio("Provide an Audio Report:", ["Upload Audio File", "Record Audio (Requires HTTPS/Localhost)"])
    
    audio_bytes = None
    filename = "upload.wav"
    
    if input_method == "Upload Audio File":
        uploaded_file = st.file_uploader("Upload an audio file (e.g. .wav, .mp3, .flac)", type=["wav", "mp3", "flac", "ogg", "m4a"])
        if uploaded_file is not None:
            audio_bytes = uploaded_file.read()
            filename = uploaded_file.name
            st.audio(audio_bytes, format='audio/wav')
    else:
        # Streamlit's audio_input allows recording directly from the browser
        audio_value = st.audio_input("Record a voice note")
        if audio_value:
            audio_bytes = audio_value.read()
            filename = "recorded_audio.wav"
            
    if st.button("Process Audio") and audio_bytes:
        with st.spinner("Processing... Transcribing via Whisper, Querying FAISS for Context, Extracting JSON via Ollama..."):
            
            files = {'file': (filename, audio_bytes, 'audio/wav')}
            response = requests.post(f"{BACKEND_URL}/process-audio", files=files)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", "")
                analysis = result.get("analysis", {})
                context = result.get("retrieved_context", "")
                
                # --- Layout for Results ---
                st.success("Analysis Complete!")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Operator Transcript")
                    st.info(f'"{transcript}"')
                    
                    st.subheader("Retrieved Context (RAG)")
                    st.write(context)
                
                with col2:
                    st.subheader("Structured Intelligence")
                    
                    
                    # Severity formatting
                    sev_color = "#00FFAA"
                    if "High" in analysis.get("severity", "") or "Critical" in analysis.get("severity", ""):
                        sev_color = "#FF4B4B"
                    elif "Medium" in analysis.get("severity", ""):
                        sev_color = "#FFAA00"
                        
                    st.markdown(f'''
                    <div class="intelligence-card">
                        <strong style="color: #94A3B8">Equipment:</strong> <span style="font-size: 1.1rem;">{analysis.get('equipment_name', 'N/A')}</span><br><br>
                        <strong style="color: #94A3B8">Severity:</strong> <span style="color:{sev_color}; font-weight:bold; font-size: 1.1rem;">{analysis.get('severity', 'N/A')}</span><br><br>
                        <strong style="color: #94A3B8">Summary:</strong> <span style="font-size: 1.1rem;">{analysis.get('summary', 'N/A')}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.subheader("Recommended Action")
                    st.warning(analysis.get("recommended_action", "N/A"))
                    
                    # Performance Metrics Box
                    metrics = result.get("metrics")
                    if metrics:
                        st.markdown(f'''
                        <div style="background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px; margin-top: 20px; font-family: monospace; color: #94A3B8;">
                            Transcription Time: {metrics.get("transcription", 0)}s<br>
                            Retrieval Time: {metrics.get("retrieval", 0)}s<br>
                            LLM Time: {metrics.get("llm", 0)}s
                        </div>
                        ''', unsafe_allow_html=True)
                    
            else:
                st.error(f"Failed to process: {response.text}")


with tab2:
    st.header("Search Maintenance History")
    query = st.text_input("Enter search query (e.g., 'crane leaking oil'):")
    
    if st.button("Search History") and query:
        with st.spinner("Searching FAISS Index..."):
            response = requests.post(f"{BACKEND_URL}/query-history", json={"query": query})
            
            if response.status_code == 200:
                context = response.json().get("context", "")
                st.info(context)
            else:
                st.error("Failed to query history.")


with tab3:
    st.header("Ingest Historical Logs")
    st.write("Before the RAG pipeline works, we need to ingest historical maintenance files into the FAISS vector database.")
    
    if st.button("Ingest Sample Knowledge (data/mock_logs.csv)"):
        with st.spinner("Ingesting rows, generating embeddings, updating FAISS..."):
            response = requests.post(f"{BACKEND_URL}/ingest-data?filename=data/mock_logs.csv")
            if response.status_code == 200:
                st.success("Successfully ingested data into the Vector DB.")
            else:
                st.error(f"Failed to ingest: {response.text}. Does data/mock_logs.csv exist?")
