"""
Simple LLM client that works with both OpenAI and Gemini
No complex dependencies, just direct API calls
"""
import os
from typing import Optional


class LLMClient:
    """Simple unified client for OpenAI and Gemini"""
    
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if "gemini" in self.provider or "google" in self.provider:
            self._init_gemini()
        elif "openai" in self.provider:
            self._init_openai()
        elif "groq" in self.provider:
            self._init_groq()
    
    def _init_gemini(self):
        """Initialize Gemini client"""
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        # Extract model name without prefix
        model_name = self.model.replace("gemini/", "")
        self.client = genai.GenerativeModel(model_name)
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def _init_groq(self):
        """Initialize Groq client"""
        from groq import Groq
        self.client = Groq(api_key=self.api_key)
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from prompt"""
        try:
            if "gemini" in self.provider or "google" in self.provider:
                return self._generate_gemini(prompt, temperature)
            elif "openai" in self.provider:
                return self._generate_openai(prompt, temperature)
            elif "groq" in self.provider:
                return self._generate_groq(prompt, temperature)
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def _generate_gemini(self, prompt: str, temperature: float) -> str:
        """Generate with Gemini"""
        response = self.client.generate_content(
            prompt,
            generation_config={'temperature': temperature}
        )
        return response.text
    
    def _generate_openai(self, prompt: str, temperature: float) -> str:
        """Generate with OpenAI"""
        model_name = self.model.replace("openai/", "")
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _generate_groq(self, prompt: str, temperature: float) -> str:
        """Generate with Groq"""
        model_name = self.model.replace("groq/", "")
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content

