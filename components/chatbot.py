import streamlit as st
import google.generativeai as genai

class FootballChatbot:
    def __init__(self, data, memory):
        self.data = data
        self.memory = memory
    
    def generate_response(self, prompt):
        """Generate a response using the Gemini model with context from memory"""
        # Create context from memory
        analyzed_players = self.memory.get("analyzed_players", [])
        team_insights = self.memory.get("team_insights", [])
        
        # Add current analysis results if available
        analysis_context = ""
        if hasattr(st.session_state, "analysis_results") and st.session_state.analysis_results:
            analysis_context += "\nRecent analysis results:\n"
            for result in st.session_state.analysis_results:
                analysis_context += f"- Analysis of {result['name']} ({result['position']})\n"
        
        if hasattr(st.session_state, "team_analysis") and st.session_state.team_analysis:
            analysis_context += "\nRecent team analysis is also available.\n"
        
        # Create context from memory
        memory_context = ""
        if analyzed_players:
            memory_context += "Previously analyzed players:\n"
            for player in analyzed_players:
                memory_context += f"- {player['name']} ({player['position']})\n"
        
        if team_insights:
            memory_context += "\nTeam insights:\n"
            for insight in team_insights:
                memory_context += f"- {insight}\n"
        
        # Create system prompt
        system_prompt = """
        You are an expert football analyst specializing in player development and team composition analysis.
        Be wise, friendly, and helpful in your responses without introducing yourself.
        Provide practical, age-appropriate insights and recommendations.
        Consider both individual potential and team-wide patterns.
        Maintain a balanced perspective between immediate performance and long-term development.
        Your knowledge comes from previously analyzed players and insights in the shared memory.
        """
        
        # Add chat history context for continuity
        chat_history = ""
        if "messages" in st.session_state and len(st.session_state.messages) > 0:
            last_messages = st.session_state.messages[-4:] if len(st.session_state.messages) > 4 else st.session_state.messages
            chat_history = "\nRecent conversation:\n"
            for msg in last_messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                chat_history += f"{role}: {msg['content']}\n"
        
        # Combine context, system prompt, and user query
        full_prompt = f"{system_prompt}\n\n{analysis_context}\n{memory_context}\n{chat_history}\n\nUser query: {prompt}"
        
        try:
            # Use genai to generate content
            response = genai.generate_text(
                model="gemini-2.0-flash",
                prompt=full_prompt
            )
            return response.text
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
