import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class InterviewerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open("resources/personas/interviewer_mark.json", "r", encoding='utf-8') as f:
            self.profile = json.load(f)

    def generate_question(self, context, history):
        """
        Generates the next interview probe using OpenAI's reasoning model.
        """
        system_prompt = f"""
        You are {self.profile['name']}, a {self.profile['role']}.
        Your background: {self.profile['background']}.
        Your style is {self.profile['personality']['communication_style']} and {self.profile['personality']['temperament']}.
        
        CRITICAL LIMITATION: {self.profile['limitations']}
        
        OBJECTIVE: {self.profile['objective']}
        
        Context of the interviewee: {context}
        
        Task: Conduct a qualitative interview. Ask one thoughtful, empathetic question or follow-up probe at a time. Do not ask multiple questions at once.
        """
        
        messages = [{"role": "system", "content": system_prompt}] + history
        
        response = self.client.chat.completions.create(
            model="gpt-5.2", # Leveraging frontier model from OpenAI
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content