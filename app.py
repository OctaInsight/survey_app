"""
Partner Institution Needs Assessment — Streamlit app
Octa Research · HARMONIA project

Two modes, chosen in the sidebar:
  1. Fill out survey  -> writes one row to Supabase (harmonia_needs_survey)
  2. View dashboard    -> reads all rows from Supabase and shows aggregated results

Run locally:
    streamlit run app.py

Requires .streamlit/secrets.toml with your Supabase project URL + anon key
(see README.md).
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    PROJECT_HEADER,
    RATING_OPTIONS,
    RATING_LABELS,
    ORG_TYPES,
    STAFF_BUCKETS,
    COUNT_BUCKETS_0TO10PLUS,
    COUNT_BUCKETS_0TO6PLUS,
    COUNT_BUCKETS_EU_PROJECTS,
    STANDARDS_OPTIONS,
    SCALEUP_BARRIERS,
    CORE_NEEDS,
    SECONDARY_NEEDS,
)
from db import insert_response, fetch_responses

st.set_page_config(page_title="HARMONIA — Partner Needs Assessment", page_icon="📋", layout="wide")


def render_header():
    st.markdown(
        f"<div style='font-size:0.95rem; color:#5b6b7a; font-weight:600; "
        f"letter-spacing:0.02em; margin-bottom:-0.5rem;'>{PROJECT_HEADER}</div>",
        unsafe_allow_html=True,
    )


def rating_radio(label: str, key: str) -> int:
    return st.radio(
        label,
        options=RATING_OPTIONS,
        format_func=lambda v: RATING_LABELS[v],
        key=key,
        horizontal=True,
    )


# ----------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "survey"
if "form_round" not in st.session_state:
    st.session_state.form_round = 0
if "just_submitted" not in st.session_state:
    st.session_state.just_submitted = False


def go_to(mode: str, new_form: bool = False):
    st.session_state.mode = mode
    st.session_state.just_submitted = False
    if new_form:
        st.session_state.form_round += 1  # bump so form widgets reset to defaults
    st.rerun()


# ----------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------
st.sidebar.markdown(f"**{PROJECT_HEADER}**")
st.sidebar.title("📋 Needs Assessment")
choice = st.sidebar.radio(
    "Go to",
    ["Fill out survey", "View dashboard"],
    index=0 if st.session_state.mode == "survey" else 1,
)
st.session_state.mode = "survey" if choice == "Fill out survey" else "dashboard"


# ----------------------------------------------------------------------
# SURVEY MODE
# ----------------------------------------------------------------------
def render_survey():
    render_header()
    st.title("Partner Institution Needs Assessment Survey")
    st.caption(
        "This survey applies to all types of partner organisations — universities, "
        "hospitals and health facilities, ministries and regulators, development "
        "organisations, innovation actors, and NGOs. Where a question doesn't apply "
        "to your role, please choose the closest 'not applicable / don't know' option. "
        "Takes about 15–20 minutes."
    )

    if st.session_state.just_submitted:
        st.success("✅ Thank you — your response has been saved.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 View dashboard", use_container_width=True):
                go_to("dashboard")
        with c2:
            if st.button("📝 Submit another response", use_container_width=True):
                go_to("survey", new_form=True)
        return

    k = st.session_state.form_round  # key suffix so a fresh form has fresh defaults

    with st.form(key=f"survey_form_{k}"):
        st.markdown(
            "For rating questions, pick one option from **1 (Not at all / None)** "
            "to **5 (Fully / Extensive)**. There are no 'right' answers — accurate "
            "answers are more useful than favourable ones."
        )

        # --- A. Institutional profile ---
        st.header("A · Institutional profile")
        institution_name = st.text_input("Institution / organisation name", key=f"a1_{k}")
        country = st.text_input("Country", key=f"a2_{k}")
        org_type = st.selectbox("Type of organisation", ORG_TYPES, key=f"a3_{k}")
        org_type_other = ""
        if org_type == "Other":
            org_type_other = st.text_input("Please specify", key=f"a3o_{k}")
        respondent_name = st.text_input("Respondent name & role", key=f"a4_{k}")
        staff_count = st.selectbox(
            "Number of staff working on digital health, data, AI, or related "
            "policy/coordination activities (approx.)",
            STAFF_BUCKETS,
            key=f"a5_{k}",
        )

        # --- B1. Fragmentation (N1) ---
        st.header("B1 · Fragmentation of digital systems  _(core need N1)_")
        q1_systems_count = st.selectbox(
            "How many separate digital systems or platforms does your organisation "
            "currently use or oversee for its core activities (e.g. data collection, "
            "programme/case management, reporting, monitoring, service delivery)?",
            COUNT_BUCKETS_0TO6PLUS,
            key=f"q1_{k}",
        )
        q2_integration_rating = rating_radio(
            "To what extent do these systems/platforms share data with each other "
            "automatically (without manual re-entry)?",
            key=f"q2_{k}",
        )
        q3_coordination = st.selectbox(
            "Is there a single unit or person responsible for coordinating digital/"
            "data systems or initiatives across your organisation?",
            ["Yes, dedicated unit", "Yes, informal coordination", "No", "Don't know"],
            key=f"q3_{k}",
        )

        # --- B2. Interoperability & governance (N2) ---
        st.header("B2 · Interoperability & data governance  _(core need N2)_")
        q4_governance_policy = st.selectbox(
            "Does your organisation have a formal, written data governance policy "
            "(covering ownership, access rights, sharing conditions)?",
            ["Yes, documented & applied", "Yes, but inconsistently applied", "Being developed", "No"],
            key=f"q4_{k}",
        )
        q5_standards = st.multiselect(
            "Which data/interoperability standards does your organisation currently "
            "use, require, or promote (select 'not applicable' if this is outside "
            "your organisation's role)?",
            STANDARDS_OPTIONS,
            key=f"q5_{k}",
        )
        q6_data_sharing_rating = rating_radio(
            "Rate your organisation's ability to securely share data or information "
            "with external partners while retaining appropriate control over it.",
            key=f"q6_{k}",
        )

        # --- B3. Responsible AI (N3) ---
        st.header("B3 · Responsible AI & contextual validation  _(core need N3)_")
        q7_ai_use = st.selectbox(
            "Does your organisation currently use, regulate, fund, or plan to engage "
            "with any AI-enabled tools or systems (e.g. decision-support, predictive "
            "analytics, automated monitoring)?",
            ["Yes, routine use", "Yes, pilot/testing", "Yes, in a regulatory/funding capacity",
             "No, but planned", "No", "Not applicable"],
            key=f"q7_{k}",
        )
        q8_bias_audit = st.selectbox(
            "To your knowledge, has any AI tool relevant to your organisation's work "
            "undergone a formal bias/fairness or performance audit before use?",
            ["Yes", "No", "Not applicable", "Don't know"],
            key=f"q8_{k}",
        )
        q9_ai_confidence_rating = rating_radio(
            "Rate your confidence in your organisation's ability to judge whether a "
            "digital/AI tool is trustworthy and fit for your local context (population, "
            "language, infrastructure, or regulatory setting).",
            key=f"q9_{k}",
        )

        # --- B4. Human capital (N4) ---
        st.header("B4 · Human capital & implementation capacity  _(core need N4)_")
        q10_trained_staff = st.selectbox(
            "How many staff at your organisation have formal training or professional "
            "experience in digital health, health informatics, bioinformatics, AI, or "
            "digital policy?",
            COUNT_BUCKETS_0TO10PLUS,
            key=f"q10_{k}",
        )
        q11_staffing_rating = rating_radio(
            "Rate the adequacy of current staffing/expertise to carry out your "
            "organisation's role in digital health, data, or AI-related initiatives.",
            key=f"q11_{k}",
        )
        q12_turnover_impact = st.selectbox(
            "In the past 3 years, has staff turnover disrupted the continuity of any "
            "digital health/data-related initiative your organisation is involved in?",
            ["Significantly", "Somewhat", "Not at all", "Not applicable"],
            key=f"q12_{k}",
        )

        # --- B5. Scale-up gap (N5) ---
        st.header("B5 · Scale-up gap  _(core need N5)_")
        q13_pilot_not_scaled = st.selectbox(
            "Has your organisation ever been involved in a digital health/data pilot "
            "or initiative that was NOT later adopted at wider scale (institutional, "
            "regional, or national)?",
            ["Yes, several times", "Yes, once or twice", "No", "Not applicable"],
            key=f"q13_{k}",
        )
        q14_scaleup_barriers = st.multiselect(
            "If yes — what was the main barrier to scale-up?",
            SCALEUP_BARRIERS,
            key=f"q14_{k}",
        )
        q14_other_barrier = ""
        if "Other" in q14_scaleup_barriers:
            q14_other_barrier = st.text_input("Please specify the other barrier", key=f"q14o_{k}")
        q15_scaleup_readiness = rating_radio(
            "Rate your organisation's current readiness to support moving a validated "
            "pilot into routine, wider-scale use.",
            key=f"q15_{k}",
        )

        # --- B6. Policy & sustainability (N6) ---
        st.header("B6 · Policy uptake & sustainability  _(core need N6)_")
        q16_policy_link = st.selectbox(
            "Does your organisation have an active link — formal or informal — with "
            "other relevant policy, regulatory, or coordination bodies (e.g. Ministries "
            "of Health, digital health agencies, regulators, standard-setting bodies)?",
            ["Yes, formal", "Yes, informal", "No", "Don't know"],
            key=f"q16_{k}",
        )
        q17_policy_feed_rating = rating_radio(
            "Rate the extent to which your organisation's digital health/data-related "
            "work currently feeds into national or regional strategy or policy "
            "decisions.",
            key=f"q17_{k}",
        )
        q18_financing_mechanism = st.selectbox(
            "Does your organisation have a defined financing/budget mechanism to "
            "sustain digital tools or initiatives once donor or project funding ends?",
            ["Yes", "Partially", "No", "Not applicable"],
            key=f"q18_{k}",
        )

        # --- C. Secondary needs ---
        st.header("C · Additional needs  _(secondary — lower priority)_")
        q19_infrastructure_rating = rating_radio(
            "Rate the reliability of internet connectivity and electricity supply at "
            "your main site(s).",
            key=f"q19_{k}",
        )
        q20_gender_policy = st.selectbox(
            "Does your organisation have a Gender Equality Plan (or equivalent "
            "inclusion/equity policy)?",
            ["Yes", "In development", "No", "Don't know"],
            key=f"q20_{k}",
        )
        q21_leadership_rating = rating_radio(
            "Rate senior leadership's active support (visible commitment, resources, "
            "time) for digital health/data-related initiatives.",
            key=f"q21_{k}",
        )
        q22_eu_projects_count = st.selectbox(
            "How many international (EU/Horizon Europe or equivalent) research/"
            "innovation projects has your organisation participated in over the past "
            "5 years?",
            COUNT_BUCKETS_EU_PROJECTS,
            key=f"q22_{k}",
        )
        q23_dissemination_rating = rating_radio(
            "Rate your organisation's capacity to disseminate results (website, social "
            "media, publications, policy briefs).",
            key=f"q23_{k}",
        )
        q24_grant_mgmt_rating = rating_radio(
            "Rate your organisation's experience managing multi-partner EU/"
            "international grant budgets and reporting.",
            key=f"q24_{k}",
        )

        # --- D. Open questions ---
        st.header("D · Open questions")
        q25_biggest_need = st.text_area(
            "In your own words, what is the single biggest need your organisation has "
            "to improve its digital health / data / AI capacity or effectiveness?",
            key=f"q25_{k}",
        )
        q26_valuable_support = st.text_area(
            "What kind of support from this consortium (training, mentoring, funding, "
            "equipment, policy dialogue, connections) would be most valuable to you?",
            key=f"q26_{k}",
        )

        submitted = st.form_submit_button("Submit survey", use_container_width=True)

    if submitted:
        if not institution_name.strip():
            st.error("Please enter your institution/organisation name before submitting.")
            return

        payload = {
            "institution_name": institution_name.strip(),
            "country": country.strip(),
            "org_type": org_type,
            "org_type_other": org_type_other.strip(),
            "respondent_name": respondent_name.strip(),
            "staff_count": staff_count,
            "q1_systems_count": q1_systems_count,
            "q2_integration_rating": q2_integration_rating,
            "q3_coordination": q3_coordination,
            "q4_governance_policy": q4_governance_policy,
            "q5_standards": q5_standards,
            "q6_data_sharing_rating": q6_data_sharing_rating,
            "q7_ai_use": q7_ai_use,
            "q8_bias_audit": q8_bias_audit,
            "q9_ai_confidence_rating": q9_ai_confidence_rating,
            "q10_trained_staff": q10_trained_staff,
            "q11_staffing_rating": q11_staffing_rating,
            "q12_turnover_impact": q12_turnover_impact,
            "q13_pilot_not_scaled": q13_pilot_not_scaled,
            "q14_scaleup_barriers": q14_scaleup_barriers,
            "q14_other_barrier": q14_other_barrier.strip(),
            "q15_scaleup_readiness": q15_scaleup_readiness,
            "q16_policy_link": q16_policy_link,
            "q17_policy_feed_rating": q17_policy_feed_rating,
            "q18_financing_mechanism": q18_financing_mechanism,
            "q19_infrastructure_rating": q19_infrastructure_rating,
            "q20_gender_policy": q20_gender_policy,
            "q21_leadership_rating": q21_leadership_rating,
            "q22_eu_projects_count": q22_eu_projects_count,
            "q23_dissemination_rating": q23_dissemination_rating,
            "q24_grant_mgmt_rating": q24_grant_mgmt_rating,
            "q25_biggest_need": q25_biggest_need.strip(),
            "q26_valuable_support": q26_valuable_support.strip(),
        }

        try:
            insert_response(payload)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not save your response: {exc}")
            return

        st.session_state.just_submitted = True
        st.rerun()


# ----------------------------------------------------------------------
# DASHBOARD MODE
# ----------------------------------------------------------------------
def render_dashboard():
    render_header()
    st.title("📊 Needs Assessment Dashboard")

    try:
        records = fetch_responses()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not load data from Supabase: {exc}")
        return

    if not records:
        st.info("No responses yet. Once partners submit the survey, results will appear here.")
        return

    df = pd.DataFrame(records)

    # --- Filters ---
    with st.sidebar:
        st.markdown("### Filters")
        countries = sorted(df["country"].dropna().unique().tolist())
        org_types = sorted(df["org_type"].dropna().unique().tolist())
        f_countries = st.multiselect("Country", countries, default=countries)
        f_org_types = st.multiselect("Organisation type", org_types, default=org_types)

    fdf = df[df["country"].isin(f_countries) & df["org_type"].isin(f_org_types)]

    if fdf.empty:
        st.warning("No responses match the selected filters.")
        return

    # --- Top KPIs ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Responses", len(fdf))
    c2.metric("Institutions", fdf["institution_name"].nunique())
    c3.metric("Countries", fdf["country"].nunique())

    st.divider()

    # --- Core needs priority chart ---
    st.subheader("Core needs — average rating (lower = greater need)")
    need_rows = []
    for code, meta in CORE_NEEDS.items():
        col = meta["column"]
        if col in fdf.columns:
            avg = pd.to_numeric(fdf[col], errors="coerce").mean()
            need_rows.append({"Need": meta["title"], "Average rating": avg})
    need_df = pd.DataFrame(need_rows).sort_values("Average rating")
    fig = px.bar(
        need_df,
        x="Average rating",
        y="Need",
        orientation="h",
        range_x=[0, 5],
        text=need_df["Average rating"].round(2),
        color="Average rating",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(coloraxis_showscale=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

    # --- Secondary needs ---
    st.subheader("Secondary needs — average rating")
    sec_rows = []
    for label, col in SECONDARY_NEEDS.items():
        if col in fdf.columns:
            avg = pd.to_numeric(fdf[col], errors="coerce").mean()
            sec_rows.append({"Need": label, "Average rating": avg})
    sec_df = pd.DataFrame(sec_rows).sort_values("Average rating")
    fig2 = px.bar(
        sec_df, x="Average rating", y="Need", orientation="h", range_x=[0, 5],
        text=sec_df["Average rating"].round(2),
    )
    fig2.update_layout(height=280)
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # --- Categorical breakdowns ---
    st.subheader("Key categorical answers")
    cat_cols = {
        "q7_ai_use": "AI tool use / regulation / funding",
        "q13_pilot_not_scaled": "Pilots not scaled up",
        "q16_policy_link": "Link with policy/regulatory bodies",
        "q4_governance_policy": "Formal data governance policy",
        "q18_financing_mechanism": "Post-funding financing mechanism",
        "q20_gender_policy": "Gender Equality Plan / equivalent",
    }
    cols = st.columns(2)
    for i, (col, label) in enumerate(cat_cols.items()):
        if col not in fdf.columns:
            continue
        counts = fdf[col].fillna("No answer").value_counts().reset_index()
        counts.columns = [label, "Count"]
        fig3 = px.pie(counts, names=label, values="Count", title=label, hole=0.4)
        fig3.update_layout(height=320, margin=dict(t=40, b=0, l=0, r=0))
        cols[i % 2].plotly_chart(fig3, use_container_width=True)

    st.divider()

    # --- Open answers ---
    st.subheader("Open answers")
    open_df = fdf[["institution_name", "q25_biggest_need", "q26_valuable_support"]].rename(
        columns={
            "institution_name": "Institution",
            "q25_biggest_need": "Biggest need",
            "q26_valuable_support": "Most valuable support",
        }
    )
    st.dataframe(open_df, use_container_width=True, hide_index=True)

    st.divider()

    # --- Raw data + download ---
    st.subheader("Raw data")
    st.dataframe(fdf, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered data as CSV",
        fdf.to_csv(index=False).encode("utf-8"),
        file_name="harmonia_survey_responses.csv",
        mime="text/csv",
    )


# ----------------------------------------------------------------------
if st.session_state.mode == "survey":
    render_survey()
else:
    render_dashboard()
