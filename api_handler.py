import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class CricbuzzAPI:
    """Handler for Cricbuzz Cricket API"""
    
    def __init__(self):
        self.api_key = os.getenv('CRICBUZZ_API_KEY', '')
        self.api_host = os.getenv('CRICBUZZ_API_HOST', 'cricbuzz-cricket.p.rapidapi.com')
        self.base_url = f"https://{self.api_host}"
        
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }
    
    def _make_request(self, endpoint):
        """Make API request with error handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from API"}
    
    def get_matches_list(self, match_type="recent"):
        """
        Get list of matches
        match_type: 'recent', 'live', 'upcoming'
        """
        endpoint = f"matches/v1/{match_type}"
        return self._make_request(endpoint)
    
    def get_match_info(self, match_id):
        """Get detailed match information"""
        endpoint = f"mcenter/v1/{match_id}/info"
        return self._make_request(endpoint)
    
    def get_live_score(self, match_id):
        """Get live score for a match"""
        endpoint = f"mcenter/v1/{match_id}"
        return self._make_request(endpoint)
    
    def get_scorecard(self, match_id):
        """Get detailed scorecard"""
        endpoint = f"mcenter/v1/{match_id}/scard"
        return self._make_request(endpoint)
    
    def get_commentary(self, match_id):
        """Get match commentary"""
        endpoint = f"mcenter/v1/{match_id}/comm"
        return self._make_request(endpoint)
    
    def get_player_info(self, player_id):
        """Get player information"""
        endpoint = f"stats/v1/player/{player_id}"
        return self._make_request(endpoint)
    
    def get_rankings(self, format_type="test"):
        """
        Get player rankings
        format_type: 'test', 'odi', 't20'
        """
        endpoint = f"stats/v1/rankings/{format_type}"
        return self._make_request(endpoint)
    
    def get_series_list(self, series_type="international"):
        """
        Get series list
        series_type: 'international', 'league', 'domestic', 'women'
        """
        endpoint = f"series/v1/{series_type}"
        return self._make_request(endpoint)
    
    def get_series_info(self, series_id):
        """Get series information"""
        endpoint = f"series/v1/{series_id}"
        return self._make_request(endpoint)
    
    def get_news_list(self):
        """Get latest cricket news"""
        endpoint = "news/v1/index"
        return self._make_request(endpoint)
    
    def get_teams_list(self):
        """Get list of international teams"""
        endpoint = "teams/v1/international"
        return self._make_request(endpoint)
    
    def get_team_info(self, team_id):
        """Get team information"""
        endpoint = f"teams/v1/{team_id}"
        return self._make_request(endpoint)
    
    def test_connection(self):
        """Test API connection"""
        try:
            result = self.get_matches_list("recent")
            if "error" in result:
                return False, result["error"]
            return True, "API connection successful!"
        except Exception as e:
            return False, f"API test failed: {str(e)}"

api = CricbuzzAPI()

