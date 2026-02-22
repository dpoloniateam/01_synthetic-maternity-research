import os
import json
import datetime
from dotenv import dotenv_values
from src.agents.interviewer import InterviewerAgent
from src.utils.run_logger import InterviewLogger
import anthropic
import google.generativeai as genai
from openai import OpenAI

# Load environment variables
_env = dotenv_values(".env")
for k, v in _env.items():
    if v:
        os.environ[k] = v.strip('"').strip("'")

def run_synthetic_interview(persona_id, num_turns=5):
    """
    Orchestrates the conversation between Mark (Interviewer) and the selected Persona.
    """
    interviewer = InterviewerAgent()
    logger = InterviewLogger()
    
    # Load synthetic profiles
    with open("src/resources/personas/synthetic_profiles.json", "r", encoding='utf-8') as f:
        profiles = json.load(f)
        target_profile = next((p for p in profiles if p["id"] == persona_id), None)
        
    if not target_profile:
        print(f"Persona {persona_id} not found.")
        return

    history = []
    print(f"--- Starting Synthetic Interview ---")
    print(f"Interviewer: Mark (OpenAI gpt-5.2)")
    print(f"Participant: {target_profile['name']} ({target_profile['target_model']})")
    print(f"------------------------------------\n")
    
    for turn in range(num_turns):
        # 1. Interviewer (Mark) generates a question
        question, mark_in, mark_out = interviewer.generate_question(target_profile['attributes'], history)
        logger.log_interaction("openai", "gpt-5.2", history, question, mark_in, mark_out)
        
        history.append({"role": "user", "content": question})
        print(f"Mark: {question}\n")
        
        # 2. Persona responds (Routing to specific vendor API based on target_model)
        provider = target_profile['target_model'].split('/')[0]
        model_string = target_profile['target_model'].split('/')[1] 
        system_instruction = f"You are {target_profile['name']}, a {target_profile['type']}. Your attributes: {target_profile['attributes']}. Respond in the first person, naturally and conversationally. Do not break character."
        
        if provider == 'anthropic':
            client_ant = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            
            res = client_ant.messages.create(
                model=model_string, 
                max_tokens=600,
                system=system_instruction,
                messages=history # history already contains alternating user/assistant messages ending with the user's question
            )
            answer_text = res.content[0].text
            answer = f"[{target_profile['name']} - Anthropic Response]: {answer_text}"
            
            logger.log_interaction("anthropic", model_string, history, answer_text, res.usage.input_tokens, res.usage.output_tokens)
            
        elif provider == 'google':
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            
            # Format history for Gemini (roles must be 'user' or 'model')
            gemini_history = []
            for msg in history[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
                
            model = genai.GenerativeModel(
                model_name=model_string,
                system_instruction=system_instruction
            )
            
            chat = model.start_chat(history=gemini_history)
            res = chat.send_message(question)
            answer_text = res.text
            answer = f"[{target_profile['name']} - Google Response]: {answer_text}"
            
            try:
                in_tok = res.usage_metadata.prompt_token_count
                out_tok = res.usage_metadata.candidates_token_count
            except AttributeError:
                in_tok, out_tok = 0, 0
                
            logger.log_interaction("google", model_string, gemini_history + [{"role": "user", "parts": [question]}], answer_text, in_tok, out_tok)
            
        elif provider == 'xai':
            client_xai = OpenAI(
                api_key=os.environ.get("XAI_API_KEY"), # Assuming this is the variable in your .env
                base_url="https://api.x.ai/v1",
            )
            
            # Format history for xAI (OpenAI compatible)
            xai_messages = [{"role": "system", "content": system_instruction}] + history
            
            res = client_xai.chat.completions.create(
                model=model_string,
                messages=xai_messages,
                max_tokens=600
            )
            answer_text = res.choices[0].message.content
            answer = f"[{target_profile['name']} - xAI Response]: {answer_text}"
            
            logger.log_interaction("xai", model_string, xai_messages, answer_text, res.usage.prompt_tokens, res.usage.completion_tokens)
            
        else:
            answer = f"[{target_profile['name']}]: Generic fallback response."
            
        history.append({"role": "assistant", "content": answer})
        print(f"{target_profile['name']}: {answer}\n")
        
    # 3. Save the Audit Trail
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "data/transcripts"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, f"transcript_{persona_id}_{timestamp}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"persona": target_profile, "transcript": history}, f, indent=4)
        
    print(f"--- Interview Complete. Audit trail saved to {filename} ---")
    logger.save_logs()

if __name__ == "__main__":
    # Example: Run an interview with Sophia
    run_synthetic_interview("sophia_01")