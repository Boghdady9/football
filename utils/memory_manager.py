class SharedMemory:
    """
    Shared memory class to maintain state between chatbot and analysis tool
    """
    def __init__(self):
        self.memory = {
            'analyzed_players': [],
            'team_insights': [],
            'position_distribution': {},
            'age_patterns': []
        }
    
    def add_analyzed_player(self, player_info):
        """Add a player to analyzed players list"""
        # Check if player already exists
        player_ids = [p.get('id') for p in self.memory['analyzed_players']]
        if player_info.get('id') in player_ids:
            # Update existing player
            for i, player in enumerate(self.memory['analyzed_players']):
                if player.get('id') == player_info.get('id'):
                    self.memory['analyzed_players'][i] = player_info
                    break
        else:
            # Add new player
            self.memory['analyzed_players'].append(player_info)
            
            # Update position distribution
            pos = player_info.get('position', 'Unknown')
            self.memory['position_distribution'][pos] = self.memory['position_distribution'].get(pos, 0) + 1
    
    def add_team_insight(self, insight):
        """Add a team insight to memory"""
        if insight not in self.memory['team_insights']:
            self.memory['team_insights'].append(insight)
    
    def get(self, key, default=None):
        """Get a value from memory"""
        return self.memory.get(key, default)
    
    def set(self, key, value):
        """Set a value in memory"""
        self.memory[key] = value
    
    def clear(self):
        """Clear memory"""
        self.memory = {
            'analyzed_players': [],
            'team_insights': [],
            'position_distribution': {},
            'age_patterns': []
        }