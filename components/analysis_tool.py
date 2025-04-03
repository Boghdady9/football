import streamlit as st
import pandas as pd
import uuid
import time

class FootballAnalysisTool:
    def __init__(self, client, data, memory):
        self.client = client
        self.data = data
        self.memory = memory
        
        # Extract player data
        self.players = data.get("data", [])
        
        # Group players by position
        self.positions = self._group_players_by_position()
    
    def _group_players_by_position(self):
        """Group players by their positions"""
        positions = {}
        
        for player in self.players:
            position = player.get("position", "Unknown")
            if position not in positions:
                positions[position] = []
            
            positions[position].append(player)
        
        return positions
    
    def render_selector_only(self):
        """Render only the player selection UI without analyze button"""
        st.write("Select players to analyze:")
        
        # Add "Select All" checkbox
        select_all = st.checkbox("Select All")
        
        # Create position groups
        all_selected_players = []
        
        # Handle goalkeepers
        gk_selected = st.checkbox("GKs")
        
        if gk_selected or select_all:
            st.markdown("### Goalkeepers")
            gk_players = []
            if "حارس" in self.positions:
                gk_players.extend(self.positions.get("حارس", []))
            if "Goalkeeper" in self.positions:
                gk_players.extend(self.positions.get("Goalkeeper", []))
                
            for player in gk_players:
                player_selected = st.checkbox(
                    f"{player['name']} ({player.get('age', 'N/A')})",
                    value=select_all or gk_selected,
                    key=f"gk_{player.get('id', player['name'])}"
                )
                
                if player_selected:
                    all_selected_players.append(player)
        
        # Identify defense positions - define outside of conditional
        defense_positions = [pos for pos in self.positions.keys() if 
                           any(term in str(pos).lower() for term in 
                              ["دفاع", "ظهير", "defence", "defender", "back"])]
        
        # Handle defenders
        def_selected = st.checkbox("Defence")
        
        if def_selected or select_all:
            st.markdown("### Defenders")
            
            for pos in defense_positions:
                st.markdown(f"**{pos}:**")
                
                for player in self.positions.get(pos, []):
                    player_selected = st.checkbox(
                        f"{player['name']} ({player.get('age', 'N/A')})",
                        value=select_all or def_selected,
                        key=f"def_{player.get('id', player['name'])}"
                    )
                    
                    if player_selected:
                        all_selected_players.append(player)
        
        # Handle all other positions
        other_positions = [pos for pos in self.positions.keys() if 
                          pos not in ["حارس", "Goalkeeper"] and 
                          pos not in defense_positions]
        
        for position in other_positions:
            pos_selected = st.checkbox(position)
            
            if pos_selected or select_all:
                st.markdown(f"### {position} Players")
                
                for player in self.positions.get(position, []):
                    player_selected = st.checkbox(
                        f"{player['name']} ({player.get('age', 'N/A')})",
                        value=select_all or pos_selected,
                        key=f"{position}_{player.get('id', player['name'])}"
                    )
                    
                    if player_selected:
                        all_selected_players.append(player)
        
        # Store selected players in session state for the button in main chat area
        st.session_state.selected_players = all_selected_players
    
    def perform_streaming_analysis(self):
        """Perform analysis with streaming output in the main content area"""
        if not st.session_state.selected_players:
            return
        
        selected_players = st.session_state.selected_players
        
        # Create a placeholder for streaming output
        analysis_container = st.empty()
        progress_bar = st.progress(0)
        
        # Create a container for displaying results as they come in
        results_container = st.container()
        
        # Initialize analysis results if needed
        if "analysis_results" not in st.session_state:
            st.session_state.analysis_results = []
        
        # Count of players already analyzed
        analyzed_count = len(st.session_state.analysis_results)
        
        # If we already have some results but not all, continue from where we left off
        remaining_players = selected_players[analyzed_count:]
        
        if remaining_players:
            analysis_container.info(f"Analyzing {len(remaining_players)} remaining players...")
            
            for i, player in enumerate(remaining_players):
                # Update progress
                current_progress = (analyzed_count + i) / len(selected_players)
                progress_bar.progress(current_progress)
                
                # Show thinking animation
                analysis_container.info(f"Analyzing player {analyzed_count + i + 1} of {len(selected_players)}: {player['name']} ({player['position']})")
                
                # Simulate analysis thinking with dots
                for dots in [".  ", ".. ", "..."]:
                    analysis_container.info(f"Analyzing player {analyzed_count + i + 1} of {len(selected_players)}: {player['name']} ({player['position']}) {dots}")
                    time.sleep(0.3)
                
                # Generate analysis
                analysis = self._analyze_player(player)
                
                if analysis:
                    # Update shared memory
                    self._update_memory(player, analysis)
                    
                    # Add to results
                    result = {
                        "name": player.get("name", "Unknown"),
                        "position": player.get("position", "Unknown"),
                        "analysis": analysis
                    }
                    
                    st.session_state.analysis_results.append(result)
                    
                    # Show current analysis
                    analysis_container.success(f"Analysis complete for {player['name']}")
                    
                    # Add analysis to chat history instead of displaying separately
                    user_message = f"Analyze player: {player['name']} ({player['position']})"
                    
                    if "messages" not in st.session_state:
                        st.session_state.messages = []
                    
                    # Add "user request" and "assistant response" to chat history
                    st.session_state.messages.append({"role": "user", "content": user_message})
                    st.session_state.messages.append({"role": "assistant", "content": analysis})
                    
                    # Display in results container as well
                    with results_container:
                        with st.chat_message("user"):
                            st.markdown(user_message)
                        with st.chat_message("assistant"):
                            st.markdown(analysis)
                
                # Small delay between players
                time.sleep(0.5)
            
            # Analysis complete for all players
            progress_bar.progress(1.0)
            analysis_container.success(f"Analysis complete for all {len(selected_players)} players!")
            
            # Generate team analysis if multiple players
            if len(selected_players) > 1:
                analysis_container.info("Generating team analysis...")
                
                for dots in [".  ", ".. ", "..."]:
                    analysis_container.info(f"Generating team analysis {dots}")
                    time.sleep(0.3)
                
                team_analysis = self._generate_team_analysis(selected_players)
                
                if team_analysis:
                    st.session_state.team_analysis = team_analysis
                    analysis_container.success("Team analysis complete!")
                    
                    # Add team analysis to chat history
                    team_request = f"Analyze team composition for selected {len(selected_players)} players"
                    
                    st.session_state.messages.append({"role": "user", "content": team_request})
                    st.session_state.messages.append({"role": "assistant", "content": team_analysis})
                    
                    # Display in results container
                    with results_container:
                        with st.chat_message("user"):
                            st.markdown(team_request)
                        with st.chat_message("assistant"):
                            st.markdown(team_analysis)
            
            # Clear selected players to indicate we're done
            st.session_state.selected_players = []
            st.session_state.analysis_mode = False
            
            # Add a button to return to chat
            if st.button("Return to Chat"):
                st.rerun()
    
    def _analyze_player(self, player):
        """Analyze an individual player using LLM"""
        # Construct analysis prompt
        analysis_prompt = f"""
        Analyze this football player's data considering age and performance metrics:
        
        Player: {player['name']}
        Age: {player['age']}
        Position: {player['position']}
        Performance Data: {player['performanceData']}
        
        Consider:
        1. Age-appropriate performance expectations
        2. Position-specific requirements
        3. Standout metrics and areas for improvement
        4. Development potential based on age
        
        Provide analysis in this format:
        - Overall Assessment
        - Key Strengths (2-3 points)
        - Development Areas (2-3 points)
        - Age-Specific Recommendations
        """
        
        try:
            completion = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"parts": [{"text": analysis_prompt}]}]
            )
            return completion.text
        except Exception as e:
            st.error(f"Error analyzing player {player['name']}: {str(e)}")
            return None
    
    def _generate_team_analysis(self, players):
        """Generate comprehensive team analysis using LLM"""
        # Count position distribution
        position_distribution = {}
        for player in players:
            pos = player.get("position", "Unknown")
            position_distribution[pos] = position_distribution.get(pos, 0) + 1
        
        team_analysis_prompt = f"""
        Analyze this football team based on the following player data:
        
        Players Analyzed: {len(players)}
        Position Distribution: {position_distribution}
        
        Individual Players:
        {self._format_players_for_prompt(players)}
        
        Provide:
        1. Overall team composition assessment
        2. Key strengths and gaps
        3. Age distribution insights
        4. Development recommendations
        5. Position coverage analysis
        
        Focus on practical, actionable insights.
        """
        
        try:
            completion = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"parts": [{"text": team_analysis_prompt}]}]
            )
            
            # Update memory with team insights
            team_analysis = completion.text
            self.memory.add_team_insight(team_analysis)
            
            return team_analysis
        except Exception as e:
            st.error(f"Error generating team analysis: {str(e)}")
            return None
    
    def _format_players_for_prompt(self, players):
        """Format players data for LLM prompt"""
        return "\n".join([
            f"- {player.get('name', 'Unknown')} ({player.get('age', 'N/A')}): {player.get('position', 'Unknown')}"
            for player in players
        ])
    
    def _update_memory(self, player, analysis):
        """Update shared memory with player analysis"""
        player_info = {
            'id': player.get('id', str(uuid.uuid4())),
            'name': player.get('name', 'Unknown'),
            'position': player.get('position', 'Unknown'),
            'age': player.get('age', 'N/A'),
            'analysis_summary': analysis
        }
        
        self.memory.add_analyzed_player(player_info)