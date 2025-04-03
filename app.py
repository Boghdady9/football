import os
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

from components.chatbot import FootballChatbot
from components.analysis_tool import FootballAnalysisTool
from utils.memory_manager import SharedMemory

# Load environment variables
load_dotenv()

# Initialize the Google API client correctly
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ Missing Google API Key. Please check your .env file or Streamlit secrets.")
else:
    genai.configure(api_key=api_key)  # ✅ Correct setup

# Load player data
def load_player_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Initialize shared memory
@st.cache_resource
def get_shared_memory():
    return SharedMemory()

def main():
    st.set_page_config(
        page_title="Football Analyst Chatbot",
        page_icon="⚽",
        layout="wide"
    )
    
    # Initialize session state variables
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = []
    if "team_analysis" not in st.session_state:
        st.session_state.team_analysis = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "chat"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "analysis_mode" not in st.session_state:
        st.session_state.analysis_mode = False
    if "selected_players" not in st.session_state:
        st.session_state.selected_players = []
    
    # Initialize components
    memory = get_shared_memory()
    data = load_player_data()
    analysis_tool = FootballAnalysisTool(genai, data, memory)  # Use genai directly
    chatbot = FootballChatbot(genai, data, memory)  # Use genai directly
    
    # Sidebar for player selection only (no analyze button)
    with st.sidebar:
        st.title("⚽ Football Analyst")
        st.subheader("Player Selection")
        analysis_tool.render_selector_only()  # Changed to not include the analyze button
        
        # Tab selection in sidebar
        st.subheader("Navigation")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Chat", use_container_width=True, 
                      type="primary" if st.session_state.active_tab == "chat" else "secondary"):
                st.session_state.active_tab = "chat"
                st.session_state.analysis_mode = False
                st.rerun()
        
        with col2:
            if st.button("Database", use_container_width=True,
                      type="primary" if st.session_state.active_tab == "database" else "secondary"):
                st.session_state.active_tab = "database"
                st.rerun()
    
    # Handle tab switching logic
    if hasattr(st.session_state, "start_analysis") and st.session_state.start_analysis:
        st.session_state.analysis_mode = True
        st.session_state.start_analysis = False
        st.rerun()
    
    # Choose what to display
    if st.session_state.active_tab == "database":
        st.title("Player Database")
        player_df = pd.DataFrame([
            {
                "Name": p.get("name", "Unknown"),
                "Age": p.get("age", "N/A"),
                "Position": p.get("position", "Unknown"),
                "Club": p.get("clubName", "Unknown")
            }
            for p in data.get("data", [])
        ])
        st.dataframe(player_df, use_container_width=True)
    
    elif st.session_state.analysis_mode:
        st.title("Analysis in Progress")
        analysis_tool.perform_streaming_analysis()
        
        if not st.session_state.selected_players:
            st.session_state.analysis_mode = False
            st.rerun()
    
    else:
        st.title("Football Analyst Chat")
        
        if not st.session_state.messages:
            st.info("👋 Type a message below to start chatting with the Football Analyst")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        player_count = len(st.session_state.selected_players)
        analyze_button_label = f"Analyze {player_count} Players" if player_count > 0 else "No Players Selected"
        
        if st.button(analyze_button_label, disabled=player_count == 0, type="primary"):
            st.session_state.start_analysis = True
            st.session_state.analysis_results = []
            st.session_state.team_analysis = None
            st.rerun()
        
        prompt = st.chat_input("Ask about players, teams, or analysis...")
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chatbot.generate_response(prompt)
                    st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
