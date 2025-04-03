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

# Initialize the Google API client
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

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
        # Initialize with an empty message list (no greeting)
        st.session_state.messages = []
    if "analysis_mode" not in st.session_state:
        st.session_state.analysis_mode = False
    if "selected_players" not in st.session_state:
        st.session_state.selected_players = []
    
    # Initialize components
    memory = get_shared_memory()
    data = load_player_data()
    analysis_tool = FootballAnalysisTool(client, data, memory)
    chatbot = FootballChatbot(client, data, memory)
    
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
    
    # Handle tab switching logic without using actual Streamlit tabs
    # Check if we need to start analysis or continue in analysis mode
    if hasattr(st.session_state, "start_analysis") and st.session_state.start_analysis:
        st.session_state.analysis_mode = True
        st.session_state.start_analysis = False
        st.rerun()
    
    # Based on active_tab and analysis_mode, choose what to display
    if st.session_state.active_tab == "database":
        # Database tab content
        st.title("Player Database")
        # Display all players in a searchable table
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
        # Analysis mode content
        st.title("Analysis in Progress")
        analysis_tool.perform_streaming_analysis()
        
        # When analysis is complete, switch back to chat mode
        if not st.session_state.selected_players:
            st.session_state.analysis_mode = False
            st.rerun()
    
    else:
        # Chat mode content - simple top-to-bottom approach
        st.title("Football Analyst Chat")
        
        # Display user-friendly placeholder text if no messages yet
        if not st.session_state.messages:
            st.info("👋 Type a message below to start chatting with the Football Analyst")
        
        # Display chat messages in chronological order (oldest at top, newest at bottom)
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Analyze button
        player_count = len(st.session_state.selected_players)
        analyze_button_label = f"Analyze {player_count} Players" if player_count > 0 else "No Players Selected"
        
        if st.button(analyze_button_label, disabled=player_count == 0, type="primary"):
            # Start analysis mode
            st.session_state.start_analysis = True
            # Clear previous results
            st.session_state.analysis_results = []
            st.session_state.team_analysis = None
            st.rerun()
        
        # Chat input at the ROOT LEVEL - not inside any container
        prompt = st.chat_input("Ask about players, teams, or analysis...")
        
        # Handle chat responses
        if prompt:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chatbot.generate_response(prompt)
                    st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
