# WorldGames AI 🌍🏆
## Autonomous Global Sports & Traditional Games Research, Profile Generation & Publishing Platform

WorldGames AI is an autonomous, multi-agent AI engine designed to discover, research, profile, quality-audit, and publish comprehensive, 12-section definitive guides for every sport and traditional game played across the globe.

---

## 🏗️ Architecture Overview

The system is powered by **LangGraph**, **FastAPI**, **PostgreSQL**, and **NVIDIA NIM** (`nvidia/nemotron-3.5-bolt-e4b`), with multi-source data synthesis across **Wikipedia API**, **Wikidata**, and **Tavily Search**, paired with **Wikimedia Commons** for freely licensed action imagery.

```
       [START]
          │
    ┌─────▼────────────────────────────────────────┐
    │ Node 1: Topic Discovery                      │
    │ (10 Global Regions & 12 Sports Genres)       │
    └─────┬────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────────┐
    │ Node 2: Deduplication Gate                  │
    │ (Canonical Key & PostgreSQL Hashing)         │
    └─────┬───────────┬────────────────────────────┘
          │           │ (Duplicate)
          │           └────────────────────────────► [END]
          │ (Novel)
    ┌─────▼────────────────────────────────────────┐
    │ Node 3: Multi-Source Research                │
    │ (Wikipedia REST + Wikidata + Tavily)         │
    └─────┬────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────────┐
    │ Node 4: 12-Section Editorial Writer          │
    │ (1500+ Words with Field & Equipment Tables)  │
    └─────┬────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────────┐
    │ Node 5: SEO Optimization                     │
    │ (Slug, Meta Description, Search Keywords)    │
    └─────┬────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────────┐
    │ Node 6: Media Discovery                      │
    │ (Wikimedia Commons Attribution & Licensing)  │
    └─────┬────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────────┐
    │ Node 7: 11-Dimension Quality Gate            │
    │ (Score >= 8.0/10.0 to auto-publish)          │
    └─────┬───────────┬────────────────────────────┘
          │           │ (Score < 8.0)
          │           ▼
          │    ┌───────────────────────────────────┐
          │    │ Node 8: Targeted Revisions Loop   │
          │    │ (Iterative Polish & Re-Evaluation)│
          │    └──────┬────────────────────────────┘
          │           │
          │ (Passed)  ▼ (Revisions Exhausted)
    ┌─────▼───────────▼────────────────────────────┐
    │ Node 9: Publisher Service                    │
    │ (Persists, Invalidates Feed, Quota Tracking) │
    └─────┬────────────────────────────────────────┘
          │
        [END]
```

---

## 📋 12-Section Standard Guide Structure

Every generated game profile adheres to:
1. **Overview, Origins & Etymology**: Historical roots, founder culture, name origins.
2. **Core Objective & Fundamental Concept**: Primary win conditions and core philosophy.
3. **Playing Arena: Dimensions, Surface & Layout**: Pitch/court/board layout in structured Markdown tables.
4. **Equipment & Gear Specifications**: Weight, material, standard dimensions of ball, board, or protective gear.
5. **Team Composition & Player Roles**: Specific positions, designations, and player duties.
6. **Official Rules & Match Progression**: Toss, innings/quarters/periods, legal vs illegal maneuvers.
7. **Scoring System, Points & Winning Conditions**: Detailed points, technical fouls, overtime rules.
8. **Master Techniques, Skills & Tactical Strategies**: Key maneuvers, champion strategies, formations.
9. **Cultural Heritage, Rituals & Global Significance**: Rituals, chants, philosophical traditions.
10. **Premier Tournaments, Leagues & Legendary Figures**: World championships, hall-of-fame athletes.
11. **International Variations & Modern Evolution**: Regional adaptations, Olympic status, pro leagues.
12. **Getting Started Guide & Quick FAQs**: Beginner advice, starter drills, and common FAQs.

---

## 🚀 Quickstart & Diagnostics

### 1. Database & Config
Verify PostgreSQL connection and schema:
```powershell
python test_db.py
```

### 2. Diagnostics
- **LLM Connectivity**: `python test_nim.py`
- **Topic Discovery**: `python test_discovery.py`
- **Wikipedia & Search**: `python test_research.py`
- **Media Discovery**: `python test_images.py`
- **End-to-End Pipeline**: `python test_workflow.py`
- **API Endpoints**: `python test_api.py`

### 3. Running Backend
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
API Documentation will be available at: `http://127.0.0.1:8001/docs`

### 4. Background Automation Daemon
To continuously generate articles (target 200/day):
```powershell
python run_automation.py
```
