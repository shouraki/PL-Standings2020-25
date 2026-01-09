# Premier League Standings ETL Pipeline

## Architecture 
<img width="1374" height="1322" alt="image" src="https://github.com/user-attachments/assets/25a3b638-ebf4-4ed5-bd86-a96aaa5d7eb2" />

## Overview
This project builds an ETL pipeline that extracts live Premier League standings from the API-Football service and loads them into a MySQL database. The pipeline uses UPSERT logic to handle both new inserts and updates, allowing it to be run repeatedly as the season progresses without creating duplicate records.

The objective was to build a functional data pipeline that:
- Extracts data from a REST API
- Transforms JSON into structured format
- Loads data into a relational database with proper update logic

This pipeline can be extended to track historical seasons, multiple leagues, or serve as the backend for a sports analytics dashboard.

## Tools & Technologies
- Python 3
- API-Football (API-Sports)
- Pandas
- Requests
- MySQL
- mysql-connector-python
- python-dotenv
- Jupyter Notebook

## Data Pipeline

API → Transform → MySQL

**Extract**
Live standings data fetched from API-Football for Premier League (League ID: 39, 2024 season)

**Transform**
JSON response parsed and converted into a Pandas DataFrame containing:
- Team position and ID
- Matches played, won, drawn, lost
- Goals for, goals against, goal difference
- Total points and recent form (last 5 matches)

**Load**
Data loaded into MySQL using UPSERT logic. The pipeline checks if a record exists based on `(season, team_id)` and either inserts or updates accordingly.

## UPSERT Logic

The pipeline uses MySQL's `ON DUPLICATE KEY UPDATE` to handle data updates:

```sql
INSERT INTO standings (season, position, team_id, team, played, won, draw, lost,
                       goals_for, goals_against, goal_diff, points, form)
VALUES (...) AS src
ON DUPLICATE KEY UPDATE
    position = src.position,
    team = src.team,
    played = src.played,
    ...
```

This ensures the same team record is updated rather than duplicated when the pipeline runs multiple times.

## Project Approach

This project focuses on building a working ETL pipeline using real API data rather than static datasets. The emphasis was on implementing proper data engineering practices:
- API integration with authentication
- Data transformation and validation
- Database connection management
- UPSERT logic to prevent duplicates

The pipeline is designed to be run periodically (daily or weekly) to keep standings data current.

## Future Enhancements

- Extend to multiple leagues (La Liga, Bundesliga, Serie A)
- Add historical season data (2020-2025)
- Automate pipeline execution with cron or Airflow
- Build dashboard in Tableau or Power BI
- Add logging and error monitoring
- Push data to cloud warehouse (BigQuery, Snowflake)
