CREATE DATABASE IF NOT EXISTS premier_league_db;
USE premier_league_db;

-- reate table
CREATE TABLE IF NOT EXISTS standings (
    season INT NOT NULL,
    position INT NOT NULL,
    team_id INT NOT NULL,
    team VARCHAR(100) NOT NULL,
    played INT NOT NULL,
    won INT NOT NULL,
    draw INT NOT NULL,
    lost INT NOT NULL,
    goals_for INT NOT NULL,
    goals_against INT NOT NULL,
    goal_diff INT NOT NULL,
    points INT NOT NULL,
    form VARCHAR(5) NOT NULL,
    PRIMARY KEY (season, team_id),
    UNIQUE KEY uniq_season_position (season, position)
);

-- ============================================
-- UPSERT QUERY (Used in Python code)
-- ============================================
-- This query is executed by the Python ETL pipeline
-- It inserts new records or updates existing ones based on (season, team_id)
--
-- INSERT INTO standings
-- (season, position, team_id, team, played, won, draw, lost,
--  goals_for, goals_against, goal_diff, points, form)
-- VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) AS src
-- ON DUPLICATE KEY UPDATE
--     position = src.position,
--     team = src.team,
--     played = src.played,
--     won = src.won,
--     draw = src.draw,
--     lost = src.lost,
--     goals_for = src.goals_for,
--     goals_against = src.goals_against,
--     goal_diff = src.goal_diff,
--     points = src.points,
--     form = src.form;
