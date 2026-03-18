# 🎙️ Autonomous Factory Assistant

An AI-powered voice analysis and structured intelligence extraction platform for factory environments.

This application allows factory operators to report maintenance issues using their voice. It automatically transcribes the audio, retrieves relevant historical maintenance context using RAG (Retrieval-Augmented Generation), and extracts structured intelligence using a local LLM to quickly diagnose issues and recommend actions.

## 🌟 Features

*   **Voice Reporting**: Upload or directly record audio reports of factory issues.
*   **Speech-to-Text**: Powered by `faster-whisper` for fast, accurate local transcriptions.
*   **Retrieval-Augmented Generation (RAG)**: Uses FAISS to index and retrieve historical maintenance logs, ensuring the AI has context on past issues.
*   **Structured Intelligence Extraction**: Uses Ollama (local LLM) to analyze the transcript and context to extract key information such as:
    *   Equipment Name
    *   Fault Severity
    *   Summary of the Issue
    *   Recommended Action
*   **Maintenance History Search**: Text-based semantic search to query past maintenance logs.
*   **Modern Dashboard**: A clean, sleek Streamlit UI with glassmorphism aesthetics.

## 🏗️ Architecture

The project consists of two main components:

1.  **Backend (FastAPI)**: Handles audio processing, FAISS vector database interactions, and LLM inference. Runs on port `8000`.
2.  **Frontend (Streamlit)**: Provides the user interface for operators to record audio, view analytics, and query historical data. Runs on port `8501`.

## 🛠️ Prerequisites

Before running the application, ensure you have the following installed:

*   **Python 3.8+**
*   **Ollama**: Must be running locally (default: `http://localhost:11434`). You must also have the required LLM model pulled (e.g., `llama3` or `mistral` depending on what `backend/llm.py` uses).

## 🚀 Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ShetPrajwal1/GenAI_Factory_Assistant.git
    cd GenAI_Factory_Assistant
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Running the Application

You can easily start both the backend and frontend at the same time using the provided shell script:

```bash
chmod +x run.sh
./run.sh
```

Alternatively, you can run them manually in separate terminal windows:

**Start the Backend:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Start the Frontend:**
```bash
streamlit run frontend/app.py
```

Open your browser and navigate to `http://localhost:8501`.

## 📂 Data Ingestion

Before using the Assistant effectively, you need to ingest some historical knowledge into the Vector Database.

1.  Open the Streamlit app.
2.  Go to the **System Ingestion** tab.
3.  Click on **Ingest Sample Knowledge (data/mock_logs.csv)**.
4.  The system will process the CSV file and update the FAISS index locally.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
