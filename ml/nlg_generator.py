import google.genai as genai
from config import Config
import os


class NLGGenerator:
    """Natural Language Generation using Google Gemini API"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.client = None
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model"""
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            return
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            # Use gemini-3.8-flash for text generation (newer model)
            self.model = 'gemini-3.8-flash'
            print("Gemini model initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            self.client = None
            self.model = None
    
    def generate_response(self, question, context, conversation_history=None):
        """
        Generate a natural language response using Gemini API
        
        Args:
            question: User's current question
            context: Relevant information retrieved from MongoDB (dict)
            conversation_history: List of previous Q&A pairs for context
            
        Returns:
            Generated response string, or None if generation fails
        """
        if not self.client or not self.model:
            return None
        
        try:
            # Build the prompt with context and conversation history
            prompt = self._build_prompt(question, context, conversation_history)
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            return None
            
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return None
    
    def _build_prompt(self, question, context, conversation_history):
        """
        Build a prompt for the LLM with context and conversation history
        
        Args:
            question: Current user question
            context: MongoDB context data
            conversation_history: Previous conversation
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "You are a helpful university assistant chatbot. Your role is to answer student questions naturally and conversationally.",
            "",
            "IMPORTANT RULES:",
            "1. Use ONLY the information provided in the context below. Do not invent or make up any university information.",
            "2. If the context doesn't contain the answer, say you don't have that information.",
            "3. Be conversational and natural in your responses.",
            "4. Consider the conversation history to understand follow-up questions.",
            "5. Keep responses concise but helpful.",
            "",
        ]
        
        # Add conversation history if available
        if conversation_history and len(conversation_history) > 0:
            prompt_parts.append("CONVERSATION HISTORY:")
            for i, entry in enumerate(conversation_history[-5:], 1):  # Last 5 exchanges
                prompt_parts.append(f"{i}. Student: {entry.get('question', '')}")
                prompt_parts.append(f"   Assistant: {entry.get('answer', '')}")
            prompt_parts.append("")
        
        # Add context from MongoDB
        prompt_parts.append("RELEVANT INFORMATION FROM UNIVERSITY DATABASE:")
        if context:
            if isinstance(context, dict):
                for key, value in context.items():
                    if value:
                        prompt_parts.append(f"{key}: {value}")
            else:
                prompt_parts.append(str(context))
        else:
            prompt_parts.append("No specific context available.")
        
        prompt_parts.append("")
        prompt_parts.append(f"CURRENT QUESTION: {question}")
        prompt_parts.append("")
        prompt_parts.append("Provide a natural, conversational response based on the information above:")
        
        return "\n".join(prompt_parts)
    
    def is_available(self):
        """Check if the NLG generator is available"""
        return self.client is not None and self.model is not None


# Global instance
nlg_generator = None


def get_nlg_generator():
    """Get or create the NLG generator instance"""
    global nlg_generator
    if nlg_generator is None:
        nlg_generator = NLGGenerator()
    return nlg_generator
