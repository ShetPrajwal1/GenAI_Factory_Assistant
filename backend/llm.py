import requests
import json
import re

# Replace with your local host if running Ollama from another machine/container.
OLLAMA_BASE_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

def extract_structured_issue(transcript: str, retrieved_context: str = "") -> dict:
    """
    Sends the transcribed issue and relevant RAG context to a local LLM via Ollama.
    Requests structured JSON output summarizing the issue and determining severity.
    """
    
    prompt = f"""
You are an expert Senior Industrial Reliability Engineer. You analyze verbal reports from operators and output structured data.

Here is the audio transcript from the operator:
"{transcript}"

Here is the retrieved technical documentation and historical maintenance context. 
WARNING: This context is retrieved via vector search and might be for completely unrelated equipment if no exact match exists in the database.
"{retrieved_context}"

You must EXTRACT the requested information and provide a REAL-WORLD, highly technical standard operating procedure (SOP) to resolve the issue. 
Output EXACTLY ONE valid JSON object. Do not include any conversational text, do not wrap it in markdown code blocks. Just output the raw JSON string:

{{
    "equipment_name": "Specific machine or sub-assembly mentioned. Infer standard equipment if the transcript has typos or bad speech-to-text (e.g. 'Hydrolyca' -> 'Hydraulic System'). Output 'Unknown' if not mentioned.",
    "summary": "A highly technical root-cause analysis summary in 1-2 sentences regarding the issue.",
    "severity": "Low, Medium, High, or Critical (based strictly on production impact, safety, or environmental hazard).",
    "recommended_action": "Provide a detailed, professional-grade maintenance procedure. CRUCIAL INSTRUCTION: Evaluate if the historical context matches the equipment or issue in the transcript. If the context is for different equipment or an unrelated issue, completely IGNORE the context and write a customized SOP from scratch using your expert knowledge for the transcript's issue. Do NOT blindly copy an unrelated procedure. Your SOP must be directly relevant to the TRANSCRIPT. Include realistic steps (LOTO, specific diagnostics, tools) in a strict step-by-step list."
}}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",  # Encourage ollama to return structured json
        "options": {
            "temperature": 0.0  # Make responses deterministic and consistent
        }
    }
    
    try:
        response = requests.post(OLLAMA_BASE_URL, json=payload, timeout=45)
        response.raise_for_status()
        result = response.json()
        raw_text = result.get("response", "{}")
        
        # Robust JSON Parsing: In case Llama3 still outputs markdown wrappers like ```json ... ```
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            clean_json = json_match.group(0)
            return json.loads(clean_json)
        else:
            return json.loads(raw_text)
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama. Is it running on port 11434?")
        return {
            "equipment_name": "System Offline",
            "summary": "Cannot analyze: Local AI Engine (Ollama) is not running. Please start Ollama.",
            "severity": "Unknown",
            "recommended_action": "Start Ollama application and ensure `ollama run llama3` is completed.",
            "error": "ConnectionError"
        }
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return {
            "equipment_name": "Unknown",
            "summary": "Failed to parse the response from the LLM.",
            "severity": "Unknown",
            "recommended_action": "N/A",
            "error": str(e)
        }
