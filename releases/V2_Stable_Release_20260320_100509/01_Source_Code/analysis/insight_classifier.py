import os
import glob
import json
from openai import OpenAI
from dotenv import dotenv_values

def get_latest_transcript():
    list_of_files = glob.glob('data/transcripts/transcript_*.json')
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def analyze_transcript():
    # Load environment variables robustly
    _env = dotenv_values(".env")
    for k, v in _env.items():
        if v:
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            os.environ[k] = v
            
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    latest_file = get_latest_transcript()
    
    if not latest_file:
        print("No transcripts found.")
        return
        
    print(f"Analyzing newest transcript: {latest_file}\n")
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    transcript_text = json.dumps(data.get("transcript", []), indent=2)

    prompt = f"""
You are an expert qualitative researcher and data coder. I will provide you with a transcript of an ethnographic interview. 

Your task is to carefully analyze the interviewer's probing strategy and the participant's responses. Extract key points (extractions) from the participant's responses and tag each extraction EXACTLY as either [NEED] or [INSIGHT] based on these strict theoretical rules:

NEEDS: Explicit statements of what users want or require. They are surface-level desires focusing on the 'what' (e.g., 'I need a faster computer' or 'I need a closer parking spot').

INSIGHTS: Deeper understandings that explain the motivations behind behaviors. They reveal hidden truths, structural tensions, and underlying reasons for user actions (the 'why').

For each extraction, provide:
- The Tag: [NEED] or [INSIGHT]
- Quote/Summary of the extraction

After extracting and tagging, you must:
1. Briefly evaluate the interviewer's probing strategy in this run. Was it successful in yielding Insights rather than Needs?
2. Format the output with a list of the Extractions.
3. Calculate and print the precise mathematical percentage of Insights versus Needs.

Transcript for Analysis:
{transcript_text}
"""

    print("Running classification via OpenAI API...\n")
    response = client.chat.completions.create(
        model="gpt-4o", # Using gpt-4o for fast and accurate classification logic
        messages=[{"role": "system", "content": "You are a qualitative data analysis assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    print("--- Insight Classification Results ---")
    result_text = response.choices[0].message.content
    print(result_text)
    
    with open("data/transcripts/classification_results.txt", "w", encoding="utf-8") as out:
        out.write(result_text)

if __name__ == "__main__":
    analyze_transcript()