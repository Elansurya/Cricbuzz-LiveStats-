import streamlit as st
import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# PAGE CONFIGURATION

st.set_page_config(
    page_title="🏏 Cricbuzz LiveStats Pro",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS STYLING

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Orbitron:wght@400;700;900&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00ff88 !important;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f3a 100%);
        border-right: 2px solid #00ff88;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #1e2749 0%, #2a3359 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #00ff88;
        box-shadow: 0 8px 32px rgba(0, 255, 136, 0.2);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 255, 136, 0.4);
    }
    
    .match-card {
        background: linear-gradient(135deg, #2a1a4a 0%, #3a2a5a 100%);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
    }
    
    .query-card {
        background: linear-gradient(135deg, #1e2749 0%, #2a3359 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border-left: 5px solid #00ff88;
        box-shadow: 0 8px 32px rgba(0, 255, 136, 0.2);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
        color: #0a0e27;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #00cc6a 0%, #00ff88 100%);
        box-shadow: 0 8px 25px rgba(0, 255, 136, 0.6);
        transform: translateY(-2px);
    }
    
    [data-testid="stMetricValue"] {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2rem !important;
    }
    
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #ff6b6b;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 8px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    .score-display {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        color: #00ff88;
        text-shadow: 0 0 30px rgba(0, 255, 136, 0.8);
    }
    
    .success-box {
        background: rgba(0, 255, 136, 0.1);
        border-left: 4px solid #00ff88;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .error-box {
        background: rgba(255, 107, 107, 0.1);
        border-left: 4px solid #ff6b6b;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .query-result {
        background: rgba(0, 255, 136, 0.05);
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .level-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 10px;
    }
    
    .badge-beginner {
        background: #4CAF50;
        color: white;
    }
    
    .badge-intermediate {
        background: #FF9800;
        color: white;
    }
    
    .badge-advanced {
        background: #F44336;
        color: white;
    }
    
    .stats-box {
        background: linear-gradient(135deg, #2a1a4a 0%, #3a2a5a 100%);
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        border: 2px solid #00ff88;
        box-shadow: 0 5px 20px rgba(0, 255, 136, 0.3);
    }
    
    .stats-number {
        font-size: 3rem;
        font-weight: 900;
        color: #00ff88;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
    }
    
    .stats-label {
        font-size: 1rem;
        color: #b0b0b0;
        margin-top: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# DATABASE CONNECTION

def get_db_connection():
    """Establish database connection with error handling"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Elan@2004",
            database="cricbuzz_livestats",
            auth_plugin="mysql_native_password"
        )
        return connection
    except Error as e:
        st.error(f"❌ Database connection error: {str(e)}")
        return None

def execute_query(query, params=None):
    """Execute SELECT query and return results with proper error handling"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params if params else ())
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        st.error(f"❌ Query Error: {str(e)}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

# API FUNCTIONS

def fetch_live_matches():
    """Fetch live matches from Cricbuzz API"""
    try:
        url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
        headers = {
            "x-rapidapi-key": "f89fb231camsh9b1750dca1ff012p183143jsn40f147002743",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

# HOME PAGE

def home_page():
    """Home page with project overview"""
    st.markdown("<h1 style='text-align: center;'>🏏 CRICBUZZ LIVESTATS PRO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #00ff88;'>Real-Time Cricket Analytics & Advanced SQL Database</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Database status check
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM players")
            player_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            st.markdown(f"""
            <div class="success-box">
                <h4>✅ Database Connected Successfully</h4>
                <p>Database: <strong>cricbuzz_livestats</strong></p>
                <p>Players in Database: <strong>{player_count}</strong></p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <h4>⚠️ Database Warning</h4>
                <p>{str(e)}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-box">
            <h4>❌ Database Connection Failed</h4>
            <p>Please check MySQL connection settings</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>⚡ Live Matches</h3>
            <p>Real-time cricket scores</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>📊 Player Stats</h3>
            <p>Complete player database</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>🔍 25 SQL Queries</h3>
            <p>Beginner to Advanced</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <h3>🛠️ CRUD Operations</h3>
            <p>Manage player data</p>
        </div>
        """, unsafe_allow_html=True)

# LIVE MATCHES PAGE

def live_matches_page():
    """Display live cricket matches"""
    st.markdown("<h1>🔴 LIVE MATCHES</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    with st.spinner("Fetching live matches..."):
        data = fetch_live_matches()
    
    if data:
        try:
            if 'typeMatches' in data:
                match_count = 0
                for type_match in data['typeMatches']:
                    if 'seriesMatches' in type_match:
                        for series in type_match['seriesMatches']:
                            if 'seriesAdWrapper' in series:
                                series_info = series['seriesAdWrapper']
                                series_name = series_info.get('seriesName', 'Unknown Series')
                                
                                st.markdown(f"### 🏆 {series_name}")
                                
                                if 'matches' in series_info:
                                    for match in series_info['matches']:
                                        if 'matchInfo' in match:
                                            match_info = match['matchInfo']
                                            match_score = match.get('matchScore', {})
                                            
                                            match_count += 1
                                            
                                            team1 = match_info.get('team1', {}).get('teamName', 'Team 1')
                                            team2 = match_info.get('team2', {}).get('teamName', 'Team 2')
                                            venue_info = match_info.get('venueInfo', {})
                                            
                                            st.markdown(f"""
                                            <div class="match-card">
                                                <h4><span class="live-indicator"></span>{match_info.get('matchDesc', 'Match')}</h4>
                                                <p><strong>Teams:</strong> {team1} vs {team2}</p>
                                                <p><strong>Venue:</strong> {venue_info.get('ground', 'N/A')}, {venue_info.get('city', 'N/A')}</p>
                                                <p><strong>Status:</strong> {match_info.get('status', 'In Progress')}</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                            
                                            if match_score:
                                                col1, col2 = st.columns(2)
                                                
                                                with col1:
                                                    if 'team1Score' in match_score:
                                                        team1_score = match_score['team1Score']
                                                        inngs1 = team1_score.get('inngs1', {})
                                                        st.markdown(f"""
                                                        <div class="stat-card">
                                                            <h4>{team1}</h4>
                                                            <p class="score-display">{inngs1.get('runs', 0)}/{inngs1.get('wickets', 0)}</p>
                                                            <p>Overs: {inngs1.get('overs', 0)}</p>
                                                        </div>
                                                        """, unsafe_allow_html=True)
                                                
                                                with col2:
                                                    if 'team2Score' in match_score:
                                                        team2_score = match_score['team2Score']
                                                        inngs1 = team2_score.get('inngs1', {})
                                                        st.markdown(f"""
                                                        <div class="stat-card">
                                                            <h4>{team2}</h4>
                                                            <p class="score-display">{inngs1.get('runs', 0)}/{inngs1.get('wickets', 0)}</p>
                                                            <p>Overs: {inngs1.get('overs', 0)}</p>
                                                        </div>
                                                        """, unsafe_allow_html=True)
                                            
                                            st.markdown("---")
                
                if match_count == 0:
                    st.info("🏏 No live matches currently. Check back during match hours!")
            else:
                st.warning("⚠️ No match data available")
        except Exception as e:
            st.error(f"❌ Error parsing match data: {str(e)}")
    else:
        st.error("❌ Unable to fetch live matches. Please try again later.")

# PLAYER STATS PAGE

def player_stats_page():
    """All players statistics"""
    st.markdown("<h1>📊 ALL PLAYERS</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        countries = execute_query("SELECT DISTINCT country FROM players ORDER BY country")
        country_list = ["All"] + [c['country'] for c in countries] if countries else ["All"]
        selected_country = st.selectbox("🌍 Filter by Country", country_list)
    
    with col2:
        roles = ["All", "Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
        selected_role = st.selectbox("🎯 Filter by Role", roles)
    
    with col3:
        sort_options = {
            "Player Name": "player_name",
            "Total Runs": "total_runs",
            "Total Wickets": "total_wickets",
            "Batting Average": "batting_average",
            "Centuries": "centuries"
        }
        selected_sort = st.selectbox("📊 Sort by", list(sort_options.keys()))
        sort_by = sort_options[selected_sort]
    
    # Build query
    query = "SELECT * FROM players WHERE 1=1"
    if selected_country != "All":
        query += f" AND country = '{selected_country}'"
    if selected_role != "All":
        query += f" AND playing_role = '{selected_role}'"
    query += f" ORDER BY {sort_by} DESC"
    
    results = execute_query(query)
    if results and len(results) > 0:
        df = pd.DataFrame(results)
        
        # Display summary metrics
        st.markdown("### 📈 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Players", len(results))
        with col2:
            total_runs = sum([r.get('total_runs', 0) or 0 for r in results])
            st.metric("Combined Runs", f"{total_runs:,}")
        with col3:
            total_wickets = sum([r.get('total_wickets', 0) or 0 for r in results])
            st.metric("Combined Wickets", f"{total_wickets:,}")
        with col4:
            total_centuries = sum([r.get('centuries', 0) or 0 for r in results])
            st.metric("Total Centuries", total_centuries)
        
        st.markdown("---")
        
        # Display the data table
        st.markdown("### 📋 Player Details")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Player Data (CSV)",
            csv,
            "players_data.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.info("No players found matching the selected filters.")

# SQL ANALYTICS PAGE - ALL 25 QUERIES WITH TABLE ANSWERS

def sql_queries_page():
    """Complete 25 SQL queries with beautiful table UI"""
    st.markdown("<h1 style='text-align: center;'>🔍 SQL ANALYTICS - 25 QUERIES</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #00ff88;'>PDF Questions with Table Answers</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Summary Statistics
    st.markdown("### 📊 Query Collection Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">25</div>
            <div class="stats-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">8</div>
            <div class="stats-label">Beginner Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">8</div>
            <div class="stats-label">Intermediate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">9</div>
            <div class="stats-label">Advanced</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ALL 25 QUERIES
    all_queries = [
        {
            "id": "Q1",
            "name": "All Players from India",
            "query": """SELECT player_name AS 'Full Name', playing_role AS 'Playing Role', 
                        batting_style AS 'Batting Style', bowling_style AS 'Bowling Style'
                        FROM players WHERE country = 'India' ORDER BY player_name""",
            "desc": "Display all Indian players with basic information",
            "level": "Beginner"
        },
        {
            "id": "Q2",
            "name": "Players by Role",
            "query": """SELECT playing_role AS 'Playing Role', COUNT(*) AS 'Number of Players'
                        FROM players GROUP BY playing_role ORDER BY COUNT(*) DESC""",
            "desc": "Count players grouped by their playing role",
            "level": "Beginner"
        },
        {
            "id": "Q3",
            "name": "Top 10 Run Scorers",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        total_runs AS 'Total Runs'
                        FROM players WHERE total_runs > 0 
                        ORDER BY total_runs DESC LIMIT 10""",
            "desc": "Top 10 players with highest runs",
            "level": "Beginner"
        },
        {
            "id": "Q4",
            "name": "Top 10 Wicket Takers",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        total_wickets AS 'Total Wickets'
                        FROM players WHERE total_wickets > 0 
                        ORDER BY total_wickets DESC LIMIT 10""",
            "desc": "Top 10 players with most wickets",
            "level": "Beginner"
        },
        {
            "id": "Q5",
            "name": "Players by Country",
            "query": """SELECT country AS 'Country', COUNT(*) AS 'Number of Players'
                        FROM players GROUP BY country 
                        ORDER BY COUNT(*) DESC""",
            "desc": "Number of players from each country",
            "level": "Beginner"
        },
        {
            "id": "Q6",
            "name": "Wicket-keepers Only",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        total_runs AS 'Total Runs'
                        FROM players WHERE playing_role = 'Wicket-keeper' 
                        ORDER BY total_runs DESC""",
            "desc": "All wicket-keepers sorted by runs",
            "level": "Beginner"
        },
        {
            "id": "Q7",
            "name": "Players with Centuries",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        centuries AS 'Centuries', total_runs AS 'Total Runs'
                        FROM players WHERE centuries > 0 
                        ORDER BY centuries DESC""",
            "desc": "Players who have scored centuries",
            "level": "Beginner"
        },
        {
            "id": "Q8",
            "name": "Right-handed Batsmen",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        total_runs AS 'Total Runs', batting_style AS 'Batting Style'
                        FROM players WHERE batting_style LIKE '%Right%' 
                        ORDER BY total_runs DESC LIMIT 15""",
            "desc": "Top 15 right-handed batsmen",
            "level": "Beginner"
        },
        {
            "id": "Q9",
            "name": "All-rounders Performance",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        total_runs AS 'Total Runs', total_wickets AS 'Total Wickets', 
                        (total_runs + total_wickets * 20) AS 'Performance Score'
                        FROM players WHERE playing_role = 'All-rounder' 
                        ORDER BY (total_runs + total_wickets * 20) DESC""",
            "desc": "All-rounders ranked by performance score",
            "level": "Intermediate"
        },
        {
            "id": "Q10",
            "name": "High Batting Averages",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        batting_average AS 'Batting Average', total_runs AS 'Total Runs'
                        FROM players WHERE batting_average > 40 
                        ORDER BY batting_average DESC""",
            "desc": "Players with batting average over 40",
            "level": "Intermediate"
        },
        {
            "id": "Q11",
            "name": "Players with 5+ Centuries",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        centuries AS 'Centuries', fifties AS 'Fifties', total_runs AS 'Total Runs'
                        FROM players WHERE centuries >= 5 
                        ORDER BY centuries DESC""",
            "desc": "Players with at least 5 centuries",
            "level": "Intermediate"
        },
        {
            "id": "Q12",
            "name": "Best Economy Rates",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        economy_rate AS 'Economy Rate', total_wickets AS 'Total Wickets'
                        FROM players WHERE economy_rate IS NOT NULL 
                        ORDER BY economy_rate ASC LIMIT 10""",
            "desc": "Top 10 bowlers with best economy rate",
            "level": "Intermediate"
        },
        {
            "id": "Q13",
            "name": "Left-handed Players",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        batting_style AS 'Batting Style', total_runs AS 'Total Runs'
                        FROM players WHERE batting_style LIKE '%Left%' 
                        ORDER BY total_runs DESC""",
            "desc": "All left-handed players",
            "level": "Intermediate"
        },
        {
            "id": "Q14",
            "name": "Players with Best Bowling",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        best_bowling AS 'Best Bowling', total_wickets AS 'Total Wickets'
                        FROM players WHERE best_bowling IS NOT NULL 
                        ORDER BY total_wickets DESC LIMIT 10""",
            "desc": "Top 10 bowlers with their best figures",
            "level": "Intermediate"
        },
        {
            "id": "Q15",
            "name": "Experienced Players (30+ Fifties)",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        fifties AS 'Fifties', centuries AS 'Centuries', total_runs AS 'Total Runs'
                        FROM players WHERE fifties >= 30 
                        ORDER BY fifties DESC""",
            "desc": "Players with 30 or more fifties",
            "level": "Intermediate"
        },
        {
            "id": "Q16",
            "name": "All-rounders with Balance",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        total_runs AS 'Total Runs', total_wickets AS 'Total Wickets', 
                        (total_runs + total_wickets * 20) AS 'Performance Score'
                        FROM players WHERE playing_role = 'All-rounder' 
                        AND total_runs > 0 AND total_wickets > 0 
                        ORDER BY (total_runs + total_wickets * 20) DESC LIMIT 10""",
            "desc": "Top 10 balanced all-rounders",
            "level": "Intermediate"
        },
        {
            "id": "Q17",
            "name": "Batting Average by Role",
            "query": """SELECT playing_role AS 'Playing Role', COUNT(*) AS 'Number of Players', 
                        ROUND(AVG(batting_average), 2) AS 'Average Batting Average'
                        FROM players WHERE batting_average IS NOT NULL 
                        GROUP BY playing_role ORDER BY AVG(batting_average) DESC""",
            "desc": "Average batting average for each role",
            "level": "Advanced"
        },
        {
            "id": "Q18",
            "name": "Country Performance",
            "query": """SELECT country AS 'Country', COUNT(*) AS 'Players', 
                        SUM(total_runs) AS 'Total Runs', SUM(total_wickets) AS 'Total Wickets'
                        FROM players GROUP BY country HAVING COUNT(*) >= 2 
                        ORDER BY SUM(total_runs) DESC""",
            "desc": "Team statistics for countries with 2+ players",
            "level": "Advanced"
        },
        {
            "id": "Q19",
            "name": "Top All-format Players",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        format AS 'Format', total_runs AS 'Total Runs', total_wickets AS 'Total Wickets'
                        FROM players WHERE format IN ('Test', 'ODI', 'T20I') 
                        ORDER BY total_runs DESC LIMIT 15""",
            "desc": "Top 15 players across all formats",
            "level": "Advanced"
        },
        {
            "id": "Q20",
            "name": "Bowling Average Analysis",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        bowling_average AS 'Bowling Average', total_wickets AS 'Total Wickets'
                        FROM players WHERE bowling_average IS NOT NULL AND total_wickets > 0 
                        ORDER BY bowling_average ASC LIMIT 10""",
            "desc": "Top 10 bowlers with best bowling average",
            "level": "Advanced"
        },
        {
            "id": "Q21",
            "name": "Century Makers by Country",
            "query": """SELECT country AS 'Country', SUM(centuries) AS 'Total Centuries', 
                        COUNT(*) AS 'Number of Players'
                        FROM players GROUP BY country 
                        ORDER BY SUM(centuries) DESC""",
            "desc": "Total centuries scored by each country",
            "level": "Advanced"
        },
        {
            "id": "Q22",
            "name": "Economy Rate by Format",
            "query": """SELECT format AS 'Format', ROUND(AVG(economy_rate), 2) AS 'Average Economy', 
                        COUNT(*) AS 'Number of Players'
                        FROM players WHERE economy_rate IS NOT NULL 
                        GROUP BY format ORDER BY AVG(economy_rate) ASC""",
            "desc": "Average economy rate per format",
            "level": "Advanced"
        },
        {
            "id": "Q23",
            "name": "High Impact Players",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        total_runs AS 'Total Runs', total_wickets AS 'Total Wickets', 
                        (COALESCE(centuries, 0) * 100 + COALESCE(fifties, 0) * 50 + 
                        COALESCE(total_wickets, 0) * 20) AS 'Impact Score'
                        FROM players 
                        ORDER BY (COALESCE(centuries, 0) * 100 + COALESCE(fifties, 0) * 50 + 
                        COALESCE(total_wickets, 0) * 20) DESC LIMIT 15""",
            "desc": "Top 15 players by impact score",
            "level": "Advanced"
        },
        {
            "id": "Q24",
            "name": "Players with Best Strike Rate",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        strike_rate AS 'Strike Rate', total_runs AS 'Total Runs'
                        FROM players WHERE strike_rate IS NOT NULL AND total_runs > 1000 
                        ORDER BY strike_rate DESC LIMIT 10""",
            "desc": "Top 10 players with best strike rate (min 1000 runs)",
            "level": "Advanced"
        },
        {
            "id": "Q25",
            "name": "Comprehensive Player Ranking",
            "query": """SELECT player_name AS 'Player Name', country AS 'Country', 
                        playing_role AS 'Role', total_runs AS 'Total Runs', 
                        total_wickets AS 'Total Wickets', centuries AS 'Centuries', 
                        ROUND((COALESCE(total_runs, 0) * 0.5 + COALESCE(total_wickets, 0) * 15 + 
                        COALESCE(centuries, 0) * 100), 2) AS 'Overall Score'
                        FROM players 
                        ORDER BY (COALESCE(total_runs, 0) * 0.5 + COALESCE(total_wickets, 0) * 15 + 
                        COALESCE(centuries, 0) * 100) DESC LIMIT 20""",
            "desc": "Top 20 players by comprehensive ranking",
            "level": "Advanced"
        }
    ]
    
    # Filter selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        filter_option = st.selectbox(
            "📚 Select Query Category",
            ["🔢 View All (Q1-Q25)", "🟢 Beginner (8 queries)", "🟡 Intermediate (8 queries)", "🔴 Advanced (9 queries)"]
        )
    
    with col2:
        show_sql = st.checkbox("Show SQL", value=True)
    
    if "Beginner" in filter_option:
        filtered_queries = [q for q in all_queries if q["level"] == "Beginner"]
        st.info("🟢 **Beginner Level**: Basic SELECT, WHERE, ORDER BY (8 queries)")
    elif "Intermediate" in filter_option:
        filtered_queries = [q for q in all_queries if q["level"] == "Intermediate"]
        st.info("🟡 **Intermediate Level**: Complex filtering, calculations (8 queries)")
    elif "Advanced" in filter_option:
        filtered_queries = [q for q in all_queries if q["level"] == "Advanced"]
        st.info("🔴 **Advanced Level**: Aggregations, GROUP BY, HAVING (9 queries)")
    else:
        filtered_queries = all_queries
        st.info("🔢 **All 25 Queries**: Complete collection in order (Q1-Q25)")
    
    st.markdown("---")
    
    # Execute All Button
    if st.button("▶️ EXECUTE ALL QUERIES BELOW", type="primary", use_container_width=True):
        st.session_state.execute_all = True
    
    st.markdown("---")
    
    # Display each query
    for idx, query_info in enumerate(filtered_queries):
        badge_class = f"badge-{query_info['level'].lower()}"
        
        with st.expander(f"**{query_info['id']}: {query_info['name']}** - {query_info['desc']}", expanded=False):
            
            # Display badges
            st.markdown(f"""
            <div class="query-card">
                <span class="level-badge {badge_class}">{query_info['level']}</span>
                <span class="level-badge badge-advanced">{query_info['id']}</span>
                <h3 style='color: #00ff88; margin-top: 10px;'>{query_info['name']}</h3>
                <p style='color: #b0b0b0;'>📝 {query_info['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show SQL if enabled
            if show_sql:
                st.code(query_info["query"], language="sql")
            
            # Execute button
            if st.button(f"▶️ Execute {query_info['id']}", key=f"exec_{query_info['id']}", use_container_width=True):
                st.session_state[f"show_{query_info['id']}"] = True
            
            # Show results if executed
            if st.session_state.get(f"show_{query_info['id']}", False) or st.session_state.get('execute_all', False):
                with st.spinner(f"Executing {query_info['id']}..."):
                    results = execute_query(query_info["query"])
                    
                    if results and len(results) > 0:
                        df = pd.DataFrame(results)
                        
                        st.markdown(f"""
                        <div class="query-result">
                            <p style='color: #00ff88; font-weight: 600;'>
                                ✅ Query executed successfully!
                            </p>
                            <p style='color: #b0b0b0;'>
                                📊 <strong>{len(results)} rows</strong> × <strong>{len(df.columns)} columns</strong>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display Table
                        st.dataframe(df, use_container_width=True, hide_index=True, height=400)
                        
                        # Download button
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            f"📥 Download {query_info['id']} Results (CSV)",
                            csv,
                            f"{query_info['id']}_{query_info['name'].replace(' ', '_')}.csv",
                            "text/csv",
                            key=f"download_{query_info['id']}"
                        )
                    else:
                        st.warning(f"⚠️ No results found for {query_info['id']}")
            
            st.markdown("---")
    
    # Reset Button
    if st.session_state.get('execute_all', False):
        if st.button("🔄 Reset All Queries", use_container_width=True):
            for query_info in all_queries:
                if f"show_{query_info['id']}" in st.session_state:
                    del st.session_state[f"show_{query_info['id']}"]
            st.session_state.execute_all = False
            st.rerun()

# CRUD OPERATIONS
def crud_operations_page():
    """CRUD operations with error handling"""
    st.markdown("<h1>🛠️ DATABASE MANAGEMENT (CRUD)</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"])
    
    conn = get_db_connection()
    if not conn:
        st.error("❌ Database connection failed")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    # CREATE
    with tab1:
        st.subheader("➕ Add New Player")
        
        with st.form("add_player"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Player Name *")
                country = st.text_input("Country *")
                role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
                bat_style = st.selectbox("Batting Style", ["Right-handed", "Left-handed"])
                bowl_style = st.text_input("Bowling Style")
            
            with col2:
                total_runs = st.number_input("Total Runs", min_value=0, value=0)
                total_wickets = st.number_input("Total Wickets", min_value=0, value=0)
                centuries = st.number_input("Centuries", min_value=0, value=0)
                fifties = st.number_input("Fifties", min_value=0, value=0)
                format_type = st.selectbox("Format", ["Test", "ODI", "T20I"])
            
            if st.form_submit_button("✅ Add Player", use_container_width=True):
                if name and country:
                    try:
                        query = """
                        INSERT INTO players 
                        (player_name, country, playing_role, batting_style, bowling_style, 
                         total_runs, total_wickets, centuries, fifties, format)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(query, (name, country, role, bat_style, bowl_style,
                                             total_runs, total_wickets, centuries, fifties, format_type))
                        conn.commit()
                        st.success(f"✅ Player '{name}' added successfully!")
                        st.balloons()
                    except Error as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Name and Country are required")
    
    # READ
    with tab2:
        st.subheader("📖 View Players")
        
        search = st.text_input("🔍 Search by Name or Country")
        
        query = "SELECT * FROM players"
        if search:
            query += f" WHERE player_name LIKE '%{search}%' OR country LIKE '%{search}%'"
        query += " ORDER BY player_name LIMIT 100"
        
        try:
            cursor.execute(query)
            players = cursor.fetchall()
            
            if players:
                df = pd.DataFrame(players)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"📊 Showing {len(players)} players")
            else:
                st.info("No players found")
        except Error as e:
            st.error(f"❌ Error: {str(e)}")
    
    # UPDATE
    with tab3:
        st.subheader("✏️ Update Player")
        
        try:
            cursor.execute("SELECT player_id, player_name, country FROM players ORDER BY player_name")
            players = cursor.fetchall()
            
            if players:
                options = {f"{p['player_name']} ({p['country']})": p['player_id'] for p in players}
                selected = st.selectbox("Select Player to Update", list(options.keys()))
                player_id = options[selected]
                
                cursor.execute("SELECT * FROM players WHERE player_id = %s", (player_id,))
                current = cursor.fetchone()
                
                if current:
                    with st.form("update_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("Name", value=current['player_name'])
                            new_runs = st.number_input("Runs", value=int(current.get('total_runs', 0) or 0))
                        
                        with col2:
                            new_wickets = st.number_input("Wickets", value=int(current.get('total_wickets', 0) or 0))
                            new_centuries = st.number_input("Centuries", value=int(current.get('centuries', 0) or 0))
                        
                        if st.form_submit_button("💾 Update Player", use_container_width=True):
                            try:
                                query = "UPDATE players SET player_name=%s, total_runs=%s, total_wickets=%s, centuries=%s WHERE player_id=%s"
                                cursor.execute(query, (new_name, new_runs, new_wickets, new_centuries, player_id))
                                conn.commit()
                                st.success("✅ Player updated successfully!")
                                st.rerun()
                            except Error as e:
                                st.error(f"❌ Error: {str(e)}")
        except Error as e:
            st.error(f"❌ Error: {str(e)}")
    
    # DELETE
    with tab4:
        st.subheader("🗑️ Delete Player")
        st.warning("⚠️ This action cannot be undone!")
        
        try:
            cursor.execute("SELECT player_id, player_name, country FROM players ORDER BY player_name")
            players = cursor.fetchall()
            
            if players:
                options = {f"{p['player_name']} ({p['country']})": p['player_id'] for p in players}
                selected = st.selectbox("Select Player to Delete", list(options.keys()))
                player_id = options[selected]
                
                if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                    try:
                        cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
                        conn.commit()
                        st.success("✅ Player deleted successfully!")
                        st.rerun()
                    except Error as e:
                        st.error(f"❌ Error: {str(e)}")
        except Error as e:
            st.error(f"❌ Error: {str(e)}")
    
    cursor.close()
    conn.close()

# MAIN APPLICATION

def main():
    # Initialize session state
    if 'execute_all' not in st.session_state:
        st.session_state.execute_all = False
    
    # Sidebar navigation
    st.sidebar.markdown("<h1 style='text-align: center;'>🏏 NAVIGATION</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Pages",
        ["🏠 Home", "🔴 Live Matches", "📊 Player Stats", "🔍 SQL Analytics", "🛠️ CRUD"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
**Database:** cricbuzz_livestats  
**API:** Cricbuzz RapidAPI  
**Queries:** All 25 Working  
**Status:** ✅ Production Ready
    """)
    
    # Route to appropriate page
    if page == "🏠 Home":
        home_page()
    elif page == "🔴 Live Matches":
        live_matches_page()
    elif page == "📊 Player Stats":
        player_stats_page()
    elif page == "🔍 SQL Analytics":
        sql_queries_page()
    elif page == "🛠️ CRUD":
        crud_operations_page()

if __name__ == "__main__":

    main()
