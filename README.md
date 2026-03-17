# SG Courses Explorer — Web App

Interactive Streamlit app for exploring Singapore tertiary courses mapped to domains and majors.

## Local Setup

```bash
pip install -r requirements.txt
streamlit run explorer.py
```

## Deploy to Streamlit Cloud

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `explorer.py` as the main file
4. Deploy

## Files

| File | Purpose |
|---|---|
| `explorer.py` | Streamlit app |
| `courses_tagged.csv` | Course data with domain/major tags |
| `domain_major_map.json` | Domain-major mapping for filters |
| `requirements.txt` | Python dependencies |

## Features

- Domain checkboxes with dynamic course counts
- Smart-filtering majors dropdown (narrows by selected domains)
- Grouped by institution (NUS/NTU/SMU first), max 5 per group with expand
- Pagination (15 courses per page)
- Color-coded domain and major pills
- Hyperlinked course titles to programme pages
- Confidence badges (High/Med/Low)
- Shortlist view
- Data quality tab with coverage gaps analysis
- Custom orange/cream theme
- Defaults to University + Arts University view
