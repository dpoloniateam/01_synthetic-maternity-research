import os
import json
from openai import OpenAI
from dotenv import dotenv_values

_env = dotenv_values(".env")
for k, v in _env.items():
    if v:
        os.environ[k] = v.strip('"').strip("'")

class InterviewerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open("src/resources/personas/interviewer_mark.json", "r", encoding='utf-8') as f:
            self.profile = json.load(f)

    def generate_question(self, context, history):
        """
        Generates the next interview probe using OpenAI's reasoning model.
        """
        system_prompt = f"""
        You are Mark, an internationally recognized academic innovation management and healthcare service design researcher. You are diplomatic, empathetic, and focus on emotions and equity. You are conducting ethnographic interviews with socially fragile pregnant women to uncover latent insights. 
        
        CRITICAL INSTRUCTION: As a man, you lack first-hand knowledge of pregnancy; you must approach the participant with humility and deep curiosity. Your goal is to move beyond surface-level Needs (the 'what') and uncover profound Insights (the 'why' and hidden truths). Do not offer logistical solutions. Ask open-ended 'Why' and 'How' questions to explore structural and emotional drivers.
        
        Context of the interviewee: {context}
        
        Task: Conduct a qualitative interview. Ask one thoughtful, empathetic question or follow-up probe at a time. Do not ask multiple questions at once.
        """
        
        messages = [{"role": "system", "content": system_prompt}] + history
        
        response = self.client.chat.completions.create(
            model=os.getenv("INTERVIEWER_MODEL", "gpt-4o-mini"), # Using cheap model for savings mode
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content, response.usage.prompt_tokens, response.usage.completion_tokens