import os
import json
import requests
import pandas as pd
from mysql import connector
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")
SEASON = 2024
LEAGUE_ID = 39  # premier League

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

print("=" * 50)
print("Premier League Standings ETL Pipeline")
print("=" * 50)

# =====================
# EXTRACT
# =====================
print("\n[1/3] Extracting data from API-Football...")

url = "https://v3.football.api-sports.io/standings"
headers = {"x-apisports-key": API_KEY}
params = {"league": LEAGUE_ID, "season": SEASON}

response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    raise SystemExit(f"[ERROR] API request failed with status code {response.status_code}")

payload = response.json()
standings_data = payload["response"][0]["league"]["standings"][0]

print(f"[SUCCESS] Retrieved standings for {len(standings_data)} teams")

# =====================
# TRANSFORM
# =====================
print("\n[2/3] Transforming data...")

rows = []
column_names = [
    'season', 'position', 'team_id', 'team', 'played', 'won',
    'draw', 'lost', 'goals_for', 'goals_against', 'goal_diff', 'points', 'form'
]

for club in standings_data:
    season = SEASON
    position = club['rank']
    team_id = club['team']['id']
    team = club['team']['name']
    played = club['all']['played']
    won = club['all']['win']
    draw = club['all']['draw']
    lost = club['all']['lose']
    goals_for = club['all']['goals']['for']
    goals_against = club['all']['goals']['against']
    goal_diff = club['goalsDiff']
    points = club['points']
    form = club['form']

    tuple_of_club_records = (
        season, position, team_id, team, played, won, draw, lost,
        goals_for, goals_against, goal_diff, points, form
    )
    rows.append(tuple_of_club_records)

df = pd.DataFrame(rows, columns=column_names)
print(f"[SUCCESS] Transformed {len(df)} records")

# =====================
# LOAD
# =====================
print("\n[3/3] Loading data into MySQL...")

# connect to db
db_connection = connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

cur = db_connection.cursor()
print(f"Connected to MySQL database: {MYSQL_DATABASE}")

# verify table exists
sql_table = "standings"
cur.execute("SHOW TABLES LIKE %s", (sql_table,))

if cur.fetchone() is None:
    raise SystemExit(f"[ERROR] Table '{sql_table}' not found. Run schema.sql first.")

print(f"[SUCCESS] Table '{sql_table}' verified")

# UPSERT
table_cols = ['season', 'position', 'team_id', 'team', 'played', 'won', 'draw',
              'lost', 'goals_for', 'goals_against', 'goal_diff', 'points', 'form']

standings_df = df[table_cols]
standings_records_tuples = standings_df.itertuples(index=False, name=None)
list_of_standings_records_tuples = list(standings_records_tuples)

UPSERT_SQL = f"""
INSERT INTO {sql_table}
(season, position, team_id, team, played, won, draw, lost,
 goals_for, goals_against, goal_diff, points, form)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) AS src
ON DUPLICATE KEY UPDATE
    position = src.position,
    team = src.team,
    played = src.played,
    won = src.won,
    draw = src.draw,
    lost = src.lost,
    goals_for = src.goals_for,
    goals_against = src.goals_against,
    goal_diff = src.goal_diff,
    points = src.points,
    form = src.form;
"""

#UPSERT
no_of_rows = len(list_of_standings_records_tuples)

try:
    cur.executemany(UPSERT_SQL, list_of_standings_records_tuples)
    db_connection.commit()
    print(f"[SUCCESS] UPSERT completed for {no_of_rows} rows!")
except Exception as e:
    db_connection.rollback()
    print(f"[ERROR] Rolled back due to: {e}")
    raise
finally:
    cur.close()
    db_connection.close()

print("\n" + "=" * 50)
print("ETL Pipeline completed successfully!")
print("=" * 50)
