# Podcast Business Intelligence Platform

This project is a Streamlit-based business intelligence application for podcast growth, engagement, retention, monetization, subscriptions, and audience understanding. It brings together structured podcast data, a SQLite warehouse, SQL analysis, visual dashboards, and a dedicated data storytelling layer to help answer one practical question:

How is the podcast business performing, why is it happening, and what should the team do next?

## Project Goal

The platform is built to help a podcast business team:

- track listening and revenue performance
- understand which categories, episodes, countries, and platforms drive engagement
- identify what drives premium subscriptions
- analyze audience segments and demographic behavior
- turn raw metrics into narrative insights and action plans

## What The App Includes

The current Streamlit application includes four major pages:

1. Executive Dashboard
   Focuses on top-level business performance, subscription analysis, and business questions such as which categories or episodes drive premium subscriptions.

2. Data Storytelling
   Converts performance patterns into a narrative view with story events, momentum tracking, weak-point identification, and a prioritized action tracker.

3. Audience Insights
   Explains listener segments, highlights growth and risk cohorts, adds demographic analysis by age, gender, and geography, and provides root-cause driven recommendations.

4. SQL Explorer
   Helps users understand the warehouse schema, preview every table, and run starter or custom SQL queries against the project database.

## Business Questions This Project Answers

This project is designed to answer questions such as:

- How many active listeners do we have?
- How many listening minutes are we generating over time?
- What is the average completion rate?
- Which podcast categories drive the most listening?
- Which countries are strongest or weakest for engagement?
- What is the free vs premium subscription mix?
- Which countries and platforms have the best premium penetration?
- Which podcast categories drive premium subscriptions?
- Which episodes attract the highest number of premium listeners?
- Which audience segment is growing, at risk, or under-monetized?
- Which demographic groups show the strongest engagement and where are the monetization gaps?

## Data Sources

The project uses structured CSV datasets stored in the `data/` folder:

- `podcasts.csv`
- `episodes.csv`
- `listeners.csv`
- `listening_sessions.csv`
- `revenue.csv`
- `listener_segments.csv`

These datasets model the core podcast business entities:

- podcasts
- episodes
- listeners
- listening sessions
- revenue events
- audience segments

## Data Model

The SQLite database is created in [database/podcast.db](/Users/krutipatil/Documents/Podcast-Business-Intelligence-Platform-Growth-Engagement-Retention-Monetization-Analytics/database/podcast.db) using [setup_database.py](/Users/krutipatil/Documents/Podcast-Business-Intelligence-Platform-Growth-Engagement-Retention-Monetization-Analytics/setup_database.py).

Main relationships:

- `podcasts.podcast_id` -> `episodes.podcast_id`
- `episodes.episode_id` -> `sessions.episode_id`
- `listeners.listener_id` -> `sessions.listener_id`
- `episodes.episode_id` -> `revenue.episode_id`
- `listeners.listener_id` -> `listener_segments.listener_id`

## Data Cleaning And Standardization

This project uses already structured input files, so the cleaning process is focused on loading, standardizing, joining, and making the data analysis-safe inside the app.

### 1. Source ingestion

The raw CSV files are loaded with pandas in [setup_database.py](/Users/krutipatil/Documents/Podcast-Business-Intelligence-Platform-Growth-Engagement-Retention-Monetization-Analytics/setup_database.py) and written into SQLite tables using `to_sql(..., if_exists="replace")`.

This step standardizes the project into one queryable warehouse with stable table names:

- `podcasts`
- `episodes`
- `listeners`
- `sessions`
- `revenue`

### 2. Table normalization

The project normalizes the source files into relational business tables rather than analyzing CSV files directly. This is a key cleaning step because it creates consistent keys and reusable joins across dashboards.

Examples:

- podcast metadata is separated from episode metadata
- listener profile data is separated from session behavior
- revenue is stored independently at episode level

### 3. Date handling and time aggregation

The dashboards standardize time analysis using SQLite date functions such as `strftime('%Y-%m', ...)` to convert timestamps into monthly trends for:

- listening minutes
- revenue
- subscription signups

This makes the trend charts consistent across the app.

### 4. Null-safe analytics logic

Inside the Streamlit dashboards, empty results and null aggregates are handled safely using:

- `or 0` fallback logic for KPI values
- `fillna(0)` for time series and revenue series
- empty-data checks before rendering charts and tables

This prevents the dashboards from breaking when a query returns missing or sparse data.

### 5. Segment enrichment

The audience analysis merges `listener_segments.csv` with `listeners.csv` so that behavioral segments can be interpreted alongside demographics such as:

- age group
- country
- gender
- subscription type

This is an important enrichment step because segment IDs alone are not meaningful for business decisions.

### 6. Derived metrics for business analysis

Several cleaned or derived measures are calculated in the app layer:

- premium session share
- premium penetration by country
- premium share by platform
- premium listeners by category
- premium listeners by episode
- average minutes, sessions, and completion by audience segment

These derived fields convert raw operational data into decision-ready metrics.

### 7. Audience segmentation input

The project uses a prepared segmentation file, `listener_segments.csv`, which contains:

- `listener_id`
- `total_minutes`
- `avg_completion`
- `sessions`
- `segment`

This file acts as the cleaned feature set for audience analysis. The repository also includes a segmentation notebook/script path in `notebooks/`, indicating the segmentation workflow is part of the broader analytical pipeline.

## Feature Walkthrough

### Executive Dashboard

The Executive Dashboard is the command center for overall business performance.

It includes:

- KPI cards for active listeners, listening minutes, average completion, premium session share, and revenue
- monthly listening trend
- category engagement analysis
- country engagement analysis
- subscription mix and signup trend
- premium penetration by country
- premium share by platform
- executive business questions at the end of the page

The business questions section explicitly answers:

- which categories drive premium subscriptions
- which episodes drive premium subscriptions

### Data Storytelling

The Data Storytelling page is built to explain the business narrative, not just show charts.

It includes:

- storytelling KPIs
- listening momentum versus rolling baseline
- key story events
- driver analysis by category and geography
- revenue context
- action tracker

This page turns descriptive analytics into a narrative sequence:

1. What happened
2. Where the change came from
3. Why it matters
4. What should happen next

### Audience Insights

The Audience Insights page explains who the listeners are and how different audience groups behave.

It includes:

- segment scatter plot using listening depth, completion, and sessions
- chart interpretation guidance
- segment summary table
- growth segment analysis
- risk segment analysis
- opportunity segment analysis
- root-cause explanations
- recommended actions
- demographic insights by age, country, and gender
- premium penetration gaps by market

This page is designed to help a product, content, or growth team understand:

- which segment is most valuable
- which segment is at risk
- where growth can be accelerated
- where monetization is underperforming

### SQL Explorer

The SQL Explorer is not just a query editor. It is a guided data understanding tool.

It includes:

- a data dictionary for all warehouse tables
- full schema visibility
- row counts for each table
- table preview controls
- starter SQL templates
- custom SQL execution

This makes the project easier to explore for analysts, recruiters, interviewers, and business stakeholders.

## Data Storytelling Approach

The storytelling design in this project follows a business-first structure:

### What happened

The app identifies:

- peaks in listening volume
- declines in monthly performance
- engagement concentration by category and geography

### Why it happened

The app surfaces likely performance drivers such as:

- low-performing categories
- weak countries
- underperforming platforms
- risky audience cohorts
- low-penetration premium markets

### What to do next

The app converts those findings into action recommendations with:

- initiative description
- business reason
- target metric
- expected improvement target

This is important because the project is designed as a business intelligence product, not just a dashboard collection.

## Final Actionable Insights Produced By The Project

Across the dashboards, the app is built to produce final actions such as:

- double down on high-engagement categories that already over-index on premium listeners
- prioritize weak categories for content redesign, shorter formats, or stronger opening hooks
- scale user acquisition in top-performing countries with the largest listener base
- localize growth strategy in markets with low premium penetration
- improve premium conversion on the platforms with the best audience quality but weaker subscription share
- build age-specific content and campaign strategies for cohorts with low completion
- replicate formats and themes that overperform in the strongest audience segment
- increase session frequency for high-completion but lower-depth listener segments
- investigate large month-over-month drops by reviewing episode cadence, distribution timing, and format changes

## Repository Structure

```text
.
├── data/
├── database/
├── notebooks/
├── sql_queries/
├── streamlit_app/
│   ├── app.py
│   ├── executive_dashboard.py
│   ├── data_storytelling.py
│   ├── audience_dashboard.py
│   ├── sql_page.py
│   └── database.py
├── setup_database.py
├── requirements.txt
└── Readme.md
```

## Tech Stack

- Python
- Streamlit
- SQLite
- SQLAlchemy
- pandas
- Plotly
- scikit-learn

## How To Run The Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create the SQLite database

```bash
python setup_database.py
```

### 3. Run the Streamlit app

```bash
streamlit run streamlit_app/app.py
```

## Why This Project Is Strong For A Portfolio

This project demonstrates:

- business thinking, not just chart building
- end-to-end analytics workflow from CSV data to relational warehouse to dashboard
- SQL and Python working together
- KPI design for executive decision-making
- audience segmentation and demographic analysis
- subscription and monetization analysis
- storytelling and actionable business recommendations

It is especially relevant for roles in:

- business intelligence
- product analytics
- growth analytics
- media analytics
- content strategy analytics
- data analyst and analytics engineer portfolios

## Current State

The current version of the project has:

- Executive Dashboard
- Data Storytelling page
- Audience Insights with demographics
- SQL Explorer with full table coverage

Removed from the project:

- Tableau dashboard page
- AI assistant page

## Future Improvements

Possible next enhancements:

- stronger ETL validation checks before database load
- named audience segment labels instead of numeric segment IDs
- downloadable insight summaries
- cohort retention analysis
- episode-level conversion scoring
- alerting for sudden trend drops or monetization gaps

## Summary

This project is a complete Podcast Business Intelligence application that moves from raw structured podcast data to executive dashboards, audience insight generation, subscription analysis, and data storytelling. The key strength of the project is that it does not stop at reporting metrics. It explains performance, diagnoses likely causes, and recommends concrete business actions.
