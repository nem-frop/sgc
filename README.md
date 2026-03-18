# SG Courses Explorer

Interactive web app for exploring 581 Singapore tertiary courses, mapped to 15 academic domains and 146 majors.

Built as a proof of concept for browsing courses by field of study rather than by institution.

## Screenshot

Landing page with clickable domain cards → filtered course view grouped by institution.

## Setup

```bash
pip install -r requirements.txt
streamlit run explorer.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `explorer.py` as the main file
4. Deploy

## Files

| File | Purpose |
|---|---|
| `explorer.py` | Streamlit app (single file, ~800 lines) |
| `courses_tagged.csv` | 581 courses with domain/major tags, confidence scores, URLs |
| `domain_major_map.json` | Taxonomy: 15 domains → 146 majors, with bidirectional lookups |
| `requirements.txt` | Python dependencies (streamlit, pandas) |

## Features

- **Landing page** with clickable domain cards — click a domain to jump straight into filtered results
- **Domain checkboxes** with dynamic course counts (e.g., "Engineering (238)"), Select All / Clear All
- **Smart majors dropdown** — narrows options based on selected domains, shows counts per major
- **Institution type filters** — defaults to University + Arts Institution
- **Grouped by institution** — full names with abbreviations (e.g., "National University of Singapore (NUS)"), sorted NUS → NTU → SMU first
- **Expand/collapse** — 5 courses per institution by default, expand to see all
- **Color-coded pills** — domains in distinct colors, majors in orange
- **Hyperlinked course titles** — click to open programme page
- **Confidence badges** — High / Med / Low match quality indicator
- **Data quality tab** — match rates, charts by domain/institution, major coverage gaps analysis
- **Advanced search** — free-text title search, institution filter, flagged/unmatched toggles
- Custom orange/cream theme inspired by the Spark Careers colour palette

## Data

- **581 courses** across 14 institutions (6 universities, 5 polytechnics, ITE, LASALLE, NAFA)
- **71.1% major match rate**, 90.4% domain match rate
- **168 courses flagged** for human review (confidence < 0.7)
- Sources: MOE Course Finder, LASALLE and NAFA websites

## Tech

- Python 3.10+
- Streamlit
- Pandas
- No database — reads from CSV/JSON at startup
