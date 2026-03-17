"""Courses Explorer — Singapore tertiary courses mapped to domains and majors."""

import json
import os

import pandas as pd
import streamlit as st

# ────────────────────────────────────────────────────────────────
# Constants & colours
# ────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = BASE_DIR  # Data files are in the same directory as the app

PRIMARY_ORANGE = "#FF9820"
LIGHT_ORANGE = "#FFAF3F"
CREAM_BG = "#FFF7EB"
GOLD_ACCENT = "#FFEAC6"
DARK_TEXT = "#262626"

DOMAIN_COLORS = {
    "Architecture and Planning": "#8B5CF6",
    "Arts and Design": "#EC4899",
    "Biological Sciences": "#10B981",
    "Business and Economics": "#F59E0B",
    "Communication": "#3B82F6",
    "Education": "#6366F1",
    "Engineering": "#EF4444",
    "History and Philosophy": "#8B5E3C",
    "Language and Area Studies": "#14B8A6",
    "Legal Studies": "#6B7280",
    "Mathematics and Computer Science": "#2563EB",
    "Medicine Sciences": "#DC2626",
    "Physical and Environment Sciences": "#059669",
    "Politics and Social Studies": "#7C3AED",
    "Veterinary and Agriculture Sciences": "#65A30D",
}

INST_TYPE_LABELS = {
    "university": "University",
    "polytechnic": "Polytechnic",
    "ite": "ITE",
    "arts": "Arts Institution",
}

INST_SORT_ORDER = {
    "NUS": 0, "NTU": 1, "SMU": 2, "SIT": 3, "SUSS": 4, "SUTD": 5,
    "NYP": 6, "NP": 7, "RP": 8, "SP": 9, "TP": 10,
    "ITE": 11,
    "LASALLE": 12, "NAFA": 13,
}

COURSES_PER_GROUP = 5

# ────────────────────────────────────────────────────────────────
# CSS injection
# ────────────────────────────────────────────────────────────────

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;500;600;700&family=Work+Sans:wght@400;500;600;700&display=swap');

    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stToolbar"] {{visibility: hidden;}}
    header[data-testid="stHeader"] {{display: none !important;}}
    .stApp > [data-testid="stAppViewContainer"] {{
        padding-top: 0 !important;
    }}
    .block-container {{
        padding-top: 1rem !important;
    }}

    /* Base typography */
    .stApp {{
        font-family: 'Work Sans', sans-serif;
    }}
    h1, h2, h3 {{
        font-family: 'Bricolage Grotesque', serif !important;
        color: {DARK_TEXT} !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {CREAM_BG};
        padding-top: 0.5rem;
    }}
    [data-testid="stSidebar"] .stCheckbox label p {{
        font-family: 'Work Sans', sans-serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Work Sans', sans-serif;
        color: {DARK_TEXT};
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom-color: {PRIMARY_ORANGE} !important;
        color: {PRIMARY_ORANGE} !important;
    }}

    /* Metrics */
    [data-testid="stMetric"] {{
        background-color: white;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid {PRIMARY_ORANGE};
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    [data-testid="stMetricValue"] {{
        color: {PRIMARY_ORANGE};
        font-family: 'Bricolage Grotesque', serif !important;
    }}

    /* Expander styling */
    [data-testid="stExpander"] {{
        border: none !important;
        background-color: transparent !important;
    }}
    [data-testid="stExpander"] summary {{
        font-family: 'Work Sans', sans-serif;
        font-size: 13px;
        color: #6B7280;
    }}

    /* Button styling */
    .stButton > button {{
        font-family: 'Work Sans', sans-serif !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }}

    /* Links */
    a:hover {{
        color: {PRIMARY_ORANGE} !important;
    }}

    /* Prevent sidebar from being collapsed */
    [data-testid="stSidebarCollapseButton"] {{
        display: none !important;
    }}
</style>
"""


# ────────────────────────────────────────────────────────────────
# Data loading
# ────────────────────────────────────────────────────────────────


@st.cache_data
def load_data():
    df = pd.read_csv(
        os.path.join(OUTPUT_DIR, "courses_tagged.csv"), encoding="utf-8-sig"
    )
    df = df.fillna("")
    with open(os.path.join(OUTPUT_DIR, "domain_major_map.json"), encoding="utf-8") as f:
        mapping = json.load(f)
    return df, mapping


def count_courses_per_domain(df):
    counts = {}
    for domains_str in df["matched_domains"]:
        if domains_str:
            for d in str(domains_str).split("|"):
                d = d.strip()
                if d:
                    counts[d] = counts.get(d, 0) + 1
    return counts


def count_courses_per_major(df):
    counts = {}
    for majors_str in df["matched_majors"]:
        if majors_str:
            for m in str(majors_str).split("|"):
                m = m.strip()
                if m:
                    counts[m] = counts.get(m, 0) + 1
    return counts


# ────────────────────────────────────────────────────────────────
# HTML rendering helpers
# ────────────────────────────────────────────────────────────────


def make_pill(text, color):
    return (
        f'<span style="display:inline-block;background-color:{color}15;'
        f"color:{color};border:1px solid {color}35;padding:2px 8px;"
        f'border-radius:12px;font-size:11px;margin:1px 2px;font-weight:500;'
        f"font-family:'Work Sans',sans-serif;\">"
        f"{text}</span>"
    )


def make_domain_pills(domains_str, compact=False):
    if not domains_str:
        return '<span style="color:#d1d5db;font-size:11px;">\u2014</span>'
    pills = []
    for d in str(domains_str).split("|"):
        d = d.strip()
        if d:
            color = DOMAIN_COLORS.get(d, "#6B7280")
            if compact:
                short = d.split(" and ")[0][:12]
                pills.append(
                    f'<span title="{d}" style="display:inline-block;background-color:{color}15;'
                    f"color:{color};border:1px solid {color}35;padding:1px 6px;"
                    f'border-radius:10px;font-size:10px;margin:1px;font-weight:500;'
                    f"font-family:'Work Sans',sans-serif;\">{short}</span>"
                )
            else:
                pills.append(make_pill(d, color))
    return " ".join(pills)


def make_major_pills(majors_str):
    if not majors_str:
        return '<span style="color:#d1d5db;font-size:11px;">\u2014</span>'
    pills = []
    for m in str(majors_str).split("|"):
        m = m.strip()
        if m:
            pills.append(make_pill(m, PRIMARY_ORANGE))
    return " ".join(pills)


def make_confidence_badge(conf):
    try:
        conf = float(conf)
    except (ValueError, TypeError):
        return ""
    if conf >= 0.9:
        color, label = "#10B981", "High"
    elif conf >= 0.7:
        color, label = "#F59E0B", "Med"
    elif conf > 0:
        color, label = "#EF4444", "Low"
    else:
        color, label = "#d1d5db", "\u2014"
    return (
        f'<span style="display:inline-block;background-color:{color};'
        f"color:white;padding:1px 6px;border-radius:8px;font-size:10px;"
        f"font-weight:600;font-family:'Work Sans',sans-serif;\">{label}</span>"
    )


def render_course_row(row, show_institution=False):
    """Render one course row. Columns: Course | Majors | Domains (compact) | Match."""
    title_link = (
        f'<a href="{row["url"]}" target="_blank" '
        f'style="color:{DARK_TEXT};text-decoration:none;font-weight:500;'
        f"font-size:14px;font-family:'Work Sans',sans-serif;\">"
        f'{row["title"]}'
        f'<span style="color:{PRIMARY_ORANGE};font-size:10px;margin-left:4px;">&#8599;</span></a>'
    )
    level = row.get("qualification_level", "")
    level_html = (
        f'<div style="color:#9ca3af;font-size:11px;margin-top:2px;">{level}</div>'
        if level else ""
    )
    majors_html = make_major_pills(row["matched_majors"])
    domains_html = make_domain_pills(row["matched_domains"], compact=True)
    conf_html = make_confidence_badge(row["confidence"])

    inst_td = ""
    if show_institution:
        inst_badge = (
            f'<span style="display:inline-block;background-color:{GOLD_ACCENT};'
            f"color:{DARK_TEXT};padding:2px 8px;border-radius:8px;"
            f"font-size:11px;font-weight:600;font-family:'Work Sans',sans-serif;\">"
            f'{row["institution_abbrev"]}</span>'
        )
        inst_td = (
            f'<td style="padding:10px 6px;border-bottom:1px solid #f3f4f6;'
            f'vertical-align:top;text-align:center;">{inst_badge}</td>'
        )

    return (
        f"<tr>"
        f'<td style="padding:10px 8px;border-bottom:1px solid #f3f4f6;vertical-align:top;'
        f'min-width:240px;">{title_link}{level_html}</td>'
        f'<td style="padding:10px 8px;border-bottom:1px solid #f3f4f6;vertical-align:top;">'
        f"{majors_html}</td>"
        f'<td style="padding:10px 6px;border-bottom:1px solid #f3f4f6;vertical-align:top;'
        f'max-width:180px;">{domains_html}</td>'
        f"{inst_td}"
        f'<td style="padding:10px 6px;border-bottom:1px solid #f3f4f6;vertical-align:top;'
        f'text-align:center;">{conf_html}</td>'
        f"</tr>"
    )


def render_table_header(show_institution=False):
    inst_th = ""
    if show_institution:
        inst_th = (
            f'<th style="text-align:center;padding:8px 6px;border-bottom:2px solid {PRIMARY_ORANGE};'
            f'color:{DARK_TEXT};font-size:12px;font-weight:600;">Inst.</th>'
        )
    return (
        f'<table style="width:100%;border-collapse:collapse;font-family:\'Work Sans\',sans-serif;">'
        f"<thead><tr>"
        f'<th style="text-align:left;padding:8px;border-bottom:2px solid {PRIMARY_ORANGE};'
        f'color:{DARK_TEXT};font-size:12px;font-weight:600;">Course</th>'
        f'<th style="text-align:left;padding:8px;border-bottom:2px solid {PRIMARY_ORANGE};'
        f'color:{DARK_TEXT};font-size:12px;font-weight:600;">Majors</th>'
        f'<th style="text-align:left;padding:8px 6px;border-bottom:2px solid {PRIMARY_ORANGE};'
        f'color:{DARK_TEXT};font-size:12px;font-weight:600;">Domains</th>'
        f"{inst_th}"
        f'<th style="text-align:center;padding:8px 6px;border-bottom:2px solid {PRIMARY_ORANGE};'
        f'color:{DARK_TEXT};font-size:12px;font-weight:600;">Match</th>'
        f"</tr></thead><tbody>"
    )


# ────────────────────────────────────────────────────────────────
# Landing page
# ────────────────────────────────────────────────────────────────


def render_landing(df, mapping):
    """Show a welcome page when no domains are selected. Cards are clickable."""
    domain_counts = count_courses_per_domain(df)
    total = len(df)

    st.markdown(
        f'<p style="font-family:\'Work Sans\',sans-serif;font-size:16px;'
        f'color:#6B7280;max-width:600px;line-height:1.6;">'
        f"Browse <strong style=\"color:{PRIMARY_ORANGE};\">{total} courses</strong> "
        f"across Singapore's universities and arts institutions. "
        f"Click a domain to explore, or use the sidebar filters.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Domain cards grid — each is a button that sets a pending domain
    all_domains = sorted(mapping["all_domains"])
    cols = st.columns(3)
    for i, domain in enumerate(all_domains):
        count = domain_counts.get(domain, 0)
        color = DOMAIN_COLORS.get(domain, "#6B7280")
        with cols[i % 3]:
            if st.button(
                f"**{domain}**\n\n{count} courses",
                key=f"landing_{domain}",
                use_container_width=True,
            ):
                # Store pending domain — will be applied on next rerun before widgets render
                st.session_state["_pending_domain"] = domain
                st.rerun()

    # Inject styling for landing buttons to look like cards
    card_css = f"""
    <style>
        /* Style landing page buttons as cards */
        [data-testid="stButton"][class*="st-key-landing_"] > button {{
            background-color: white !important;
            border: 1px solid #f3f4f6 !important;
            border-left: 4px solid {PRIMARY_ORANGE} !important;
            border-radius: 10px !important;
            padding: 16px 18px !important;
            text-align: left !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
            color: {DARK_TEXT} !important;
            font-family: 'Work Sans', sans-serif !important;
            min-height: 70px !important;
            transition: box-shadow 0.2s, border-color 0.2s !important;
        }}
        [data-testid="stButton"][class*="st-key-landing_"] > button:hover {{
            box-shadow: 0 3px 8px rgba(255,152,32,0.15) !important;
            border-left-color: {PRIMARY_ORANGE} !important;
            border-color: {PRIMARY_ORANGE}40 !important;
        }}
        [data-testid="stButton"][class*="st-key-landing_"] > button p {{
            margin: 0 !important;
        }}
    </style>
    """
    st.markdown(card_css, unsafe_allow_html=True)

    # Quick stats
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    uni_count = len(df[df["institution_type"] == "university"]["institution_abbrev"].unique())
    arts_count = len(df[df["institution_type"] == "arts"]["institution_abbrev"].unique())
    domain_count = len(all_domains)
    col1.metric("Universities", uni_count)
    col2.metric("Arts Institutions", arts_count)
    col3.metric("Domains", domain_count)


# ────────────────────────────────────────────────────────────────
# Sidebar filters
# ────────────────────────────────────────────────────────────────


def render_sidebar_filters(df, mapping):
    """Sidebar: Domains (all, alphabetical) > Majors > Institution Type > Advanced."""

    domain_counts = count_courses_per_domain(df)
    major_counts = count_courses_per_major(df)

    # ── 1. Domains (all visible, alphabetical) ──
    st.sidebar.markdown(
        f'<p style="font-family:\'Bricolage Grotesque\',serif;font-size:18px;'
        f'color:{DARK_TEXT};font-weight:600;margin-bottom:4px;">Domains</p>',
        unsafe_allow_html=True,
    )

    all_domains = sorted(mapping["all_domains"])
    selected_domains = set()

    # Select all / clear all
    sa_col1, sa_col2 = st.sidebar.columns(2)
    with sa_col1:
        if st.button("Select all", key="select_all_domains", type="secondary"):
            for d in all_domains:
                st.session_state[f"domain_{d}"] = True
            st.rerun()
    with sa_col2:
        if st.button("Clear all", key="clear_all_domains", type="secondary"):
            for d in all_domains:
                st.session_state[f"domain_{d}"] = False
            st.rerun()

    for domain in all_domains:
        count = domain_counts.get(domain, 0)
        if st.sidebar.checkbox(
            f"{domain} ({count})",
            key=f"domain_{domain}",
            value=False,
        ):
            selected_domains.add(domain)

    st.sidebar.markdown("---")

    # ── 2. Majors (smart-filtered dropdown with counts) ──
    available_majors = set()
    if selected_domains:
        for d in selected_domains:
            available_majors.update(mapping["domain_to_majors"].get(d, []))
    else:
        available_majors = set(mapping["all_majors"])

    major_options = sorted(available_majors)
    major_format = {m: f"{m} ({major_counts.get(m, 0)})" for m in major_options}

    selected_majors = st.sidebar.multiselect(
        "Majors",
        major_options,
        format_func=lambda m: major_format.get(m, m),
        help="Filtered by selected domains" if selected_domains else "Select domains to narrow down",
    )

    st.sidebar.markdown("---")

    # ── 3. Institution Type (checkboxes) ──
    st.sidebar.markdown(
        f'<p style="font-family:\'Bricolage Grotesque\',serif;font-size:14px;'
        f'color:{DARK_TEXT};font-weight:600;margin-bottom:4px;">Institution Type</p>',
        unsafe_allow_html=True,
    )

    selected_types = []
    for inst_type, label in INST_TYPE_LABELS.items():
        default = inst_type in ("university", "arts")
        if st.sidebar.checkbox(label, value=default, key=f"insttype_{inst_type}"):
            selected_types.append(inst_type)

    st.sidebar.markdown("---")

    # ── 4. Advanced Search (collapsed) ──
    with st.sidebar.expander("Advanced Search"):
        search = st.text_input("Search course title", key="search_input")

        if selected_types:
            available_insts = sorted(
                df[df["institution_type"].isin(selected_types)][
                    "institution_abbrev"
                ].unique()
            )
        else:
            available_insts = sorted(df["institution_abbrev"].unique())
        selected_insts = st.multiselect(
            "Institution", available_insts, key="inst_select"
        )

        show_flagged_only = st.checkbox("Show only flagged for review", key="flagged_only")
        show_unmatched_only = st.checkbox("Show only unmatched courses", key="unmatched_only")

    return {
        "domains": selected_domains,
        "majors": selected_majors,
        "types": selected_types,
        "institutions": selected_insts,
        "search": search if "search_input" in st.session_state else "",
        "flagged_only": show_flagged_only if "flagged_only" in st.session_state else False,
        "unmatched_only": show_unmatched_only if "unmatched_only" in st.session_state else False,
    }


def apply_filters(df, filters):
    filtered = df.copy()

    if filters["types"]:
        filtered = filtered[filtered["institution_type"].isin(filters["types"])]

    if filters["institutions"]:
        filtered = filtered[filtered["institution_abbrev"].isin(filters["institutions"])]

    if filters["domains"]:
        mask = filtered["matched_domains"].apply(
            lambda x: any(d in str(x).split("|") for d in filters["domains"])
            if x else False
        )
        filtered = filtered[mask]

    if filters["majors"]:
        mask = filtered["matched_majors"].apply(
            lambda x: any(m in str(x).split("|") for m in filters["majors"])
            if x else False
        )
        filtered = filtered[mask]

    if filters["search"]:
        filtered = filtered[
            filtered["title"].str.contains(filters["search"], case=False, na=False)
        ]

    if filters["flagged_only"]:
        filtered = filtered[filtered["needs_review"] == True]

    if filters["unmatched_only"]:
        filtered = filtered[
            (filtered["matched_domains"] == "") & (filtered["matched_majors"] == "")
        ]

    return filtered


# ────────────────────────────────────────────────────────────────
# Course view (grouped by institution, no pagination)
# ────────────────────────────────────────────────────────────────


def render_courses_view(filtered):
    """Render courses grouped by institution. No pagination — all results shown."""

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Courses", len(filtered))
    col2.metric(
        "Universities",
        len(filtered[filtered["institution_type"] == "university"]),
    )
    col3.metric(
        "Polytechnics",
        len(filtered[filtered["institution_type"] == "polytechnic"]),
    )
    col4.metric(
        "ITE / Arts",
        len(filtered[filtered["institution_type"].isin(["ite", "arts"])]),
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if len(filtered) == 0:
        st.info("No courses match the current filters. Try adjusting your selections.")
        return

    # Sort by custom institution order
    filtered = filtered.copy()
    filtered["_sort_order"] = filtered["institution_abbrev"].map(INST_SORT_ORDER).fillna(99)
    filtered = filtered.sort_values(["_sort_order", "title"])

    # Group by institution
    groups = filtered.groupby("institution_abbrev", sort=False)
    sorted_groups = sorted(groups, key=lambda x: INST_SORT_ORDER.get(x[0], 99))

    for inst_name, group_df in sorted_groups:
        group_df_sorted = group_df.sort_values("title")
        total = len(group_df_sorted)
        is_expanded = inst_name in st.session_state.expanded_groups
        show_count = total if is_expanded else min(COURSES_PER_GROUP, total)

        # Group header
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-top:20px;'
            f'padding-bottom:6px;border-bottom:2px solid {GOLD_ACCENT};">'
            f'<span style="font-family:\'Bricolage Grotesque\',serif;font-size:18px;'
            f'color:{DARK_TEXT};font-weight:600;">{inst_name}</span>'
            f'<span style="background-color:{CREAM_BG};color:{PRIMARY_ORANGE};'
            f"padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;"
            f"font-family:'Work Sans',sans-serif;\">{total} courses</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Render table
        visible_rows = group_df_sorted.head(show_count)
        rows_html = [render_course_row(row, show_institution=False) for _, row in visible_rows.iterrows()]
        table_html = render_table_header(show_institution=False) + "\n".join(rows_html) + "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # Show more/less
        if total > COURSES_PER_GROUP:
            if is_expanded:
                if st.button("Show less", key=f"less_{inst_name}"):
                    st.session_state.expanded_groups.discard(inst_name)
                    st.rerun()
            else:
                if st.button(
                    f"Show all {total} courses from {inst_name} \u2192",
                    key=f"more_{inst_name}",
                ):
                    st.session_state.expanded_groups.add(inst_name)
                    st.rerun()


# ────────────────────────────────────────────────────────────────
# Data quality tab
# ────────────────────────────────────────────────────────────────


def render_data_quality(df, mapping):
    st.subheader("Data Quality Overview")

    col1, col2, col3 = st.columns(3)
    total = len(df)
    has_major = (df["matched_majors"] != "").sum()
    has_domain = (df["matched_domains"] != "").sum()
    flagged_count = (df["needs_review"] == True).sum()

    col1.metric("Major Match Rate", f"{100 * has_major / total:.1f}%")
    col2.metric("Domain Match Rate", f"{100 * has_domain / total:.1f}%")
    col3.metric("Flagged for Review", flagged_count)

    st.subheader("Match Method Distribution")
    method_counts = df["match_method"].value_counts()
    st.bar_chart(method_counts, color=PRIMARY_ORANGE)

    st.subheader("Courses per Domain")
    domain_counts = count_courses_per_domain(df)
    if domain_counts:
        dc_df = pd.DataFrame(
            sorted(domain_counts.items(), key=lambda x: -x[1]),
            columns=["Domain", "Count"],
        ).set_index("Domain")
        st.bar_chart(dc_df, color=PRIMARY_ORANGE)

    st.subheader("Courses per Institution")
    inst_counts = df["institution_abbrev"].value_counts()
    st.bar_chart(inst_counts, color=LIGHT_ORANGE)

    # Coverage gaps
    st.subheader("Major Coverage Gaps")
    major_counts = count_courses_per_major(df)
    all_majors = mapping.get("all_majors", [])
    gaps = []
    for m in all_majors:
        count = major_counts.get(m, 0)
        if count <= 2:
            domains = mapping.get("major_to_domains", {}).get(m, [])
            gaps.append({"Major": m, "Courses": count, "Domains": ", ".join(domains)})
    if gaps:
        gaps_df = pd.DataFrame(gaps).sort_values("Courses")
        st.write(f"{len(gaps)} majors have 2 or fewer matched courses:")
        st.dataframe(gaps_df.reset_index(drop=True), use_container_width=True)
    else:
        st.success("All majors have good coverage!")

    # Unmatched courses
    st.subheader("Unmatched Courses (no domain or major)")
    unmatched = df[(df["matched_domains"] == "") & (df["matched_majors"] == "")]
    if len(unmatched) > 0:
        st.write(f"{len(unmatched)} courses have no match at all.")
        st.dataframe(
            unmatched[
                ["title", "institution_abbrev", "institution_type", "suggested_majors"]
            ].reset_index(drop=True),
            use_container_width=True,
        )
    else:
        st.success("All courses have at least one domain or major match!")


# ────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────


def main():
    st.set_page_config(
        page_title="SG Courses Explorer",
        page_icon=":mortar_board:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Init session state
    if "expanded_groups" not in st.session_state:
        st.session_state.expanded_groups = set()

    # Apply any pending domain selection from landing page card click.
    # This must happen BEFORE the sidebar checkboxes are rendered,
    # so the checkbox default value picks it up.
    if "_pending_domain" in st.session_state:
        domain = st.session_state.pop("_pending_domain")
        st.session_state[f"domain_{domain}"] = True

    # Header
    st.markdown(
        f'<h1 style="font-family:\'Bricolage Grotesque\',serif;margin-bottom:0;">'
        f'<span style="color:{PRIMARY_ORANGE};">Courses</span> Explorer</h1>',
        unsafe_allow_html=True,
    )
    st.caption("Singapore tertiary courses mapped to domains and majors")

    # Load data
    df, mapping = load_data()

    # Sidebar filters
    filters = render_sidebar_filters(df, mapping)

    # Check if any domain is selected
    has_active_filters = (
        filters["domains"]
        or filters["majors"]
        or filters["search"]
        or filters["institutions"]
        or filters.get("flagged_only")
        or filters.get("unmatched_only")
    )

    if has_active_filters:
        filtered = apply_filters(df, filters)
        tab1, tab2 = st.tabs(["Courses", "Data Quality"])
        with tab1:
            render_courses_view(filtered)
        with tab2:
            render_data_quality(df, mapping)
    else:
        # Landing page — no filters active
        tab1, tab2 = st.tabs(["Home", "Data Quality"])
        with tab1:
            # Apply type filter only so landing stats respect university/arts default
            type_filtered = df.copy()
            if filters["types"]:
                type_filtered = type_filtered[type_filtered["institution_type"].isin(filters["types"])]
            render_landing(type_filtered, mapping)
        with tab2:
            render_data_quality(df, mapping)


if __name__ == "__main__":
    main()
