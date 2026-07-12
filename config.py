"""Shared metadata for the survey form and the dashboard."""

RATING_OPTIONS = [1, 2, 3, 4, 5]
RATING_LABELS = {
    1: "1 – Not at all / None",
    2: "2 – Very limited",
    3: "3 – Partial / Moderate",
    4: "4 – Good / Most cases",
    5: "5 – Fully / Extensive",
}

ORG_TYPES = [
    "University",
    "Hospital / health facility",
    "Research institute",
    "Government / public authority",
    "SME / company",
    "NGO",
    "Other",
]

STAFF_BUCKETS = ["0", "1–5", "6–15", "16–30", "30+"]
COUNT_BUCKETS_0TO10PLUS = ["0", "1–3", "4–10", "10+"]
COUNT_BUCKETS_0TO6PLUS = ["0–1", "2–3", "4–5", "6+", "Don't know"]
COUNT_BUCKETS_EU_PROJECTS = ["0", "1–2", "3–5", "6+"]

STANDARDS_OPTIONS = ["HL7 FHIR", "SNOMED CT", "ICD-10/11", "National-only formats", "None", "Don't know"]
SCALEUP_BARRIERS = [
    "Funding ended",
    "No institutional decision/ownership",
    "Technical/integration issues",
    "Lack of government engagement",
    "Staff capacity",
    "Other",
]

# One representative rating question per core need — used to build the
# "which need is most urgent" dashboard view. Lower average = greater need.
CORE_NEEDS = {
    "N1": {
        "title": "N1 · Fragmentation of digital systems",
        "column": "q2_integration_rating",
        "question": "Extent to which institutional systems share data automatically",
    },
    "N2": {
        "title": "N2 · Interoperability & data governance",
        "column": "q6_data_sharing_rating",
        "question": "Ability to securely share data with external partners",
    },
    "N3": {
        "title": "N3 · Responsible AI & contextual validation",
        "column": "q9_ai_confidence_rating",
        "question": "Confidence validating AI/digital tools locally",
    },
    "N4": {
        "title": "N4 · Human capital & implementation capacity",
        "column": "q11_staffing_rating",
        "question": "Adequacy of current staffing",
    },
    "N5": {
        "title": "N5 · Scale-up gap",
        "column": "q15_scaleup_readiness",
        "question": "Readiness to move pilots into routine wider-scale use",
    },
    "N6": {
        "title": "N6 · Policy uptake & sustainability",
        "column": "q17_policy_feed_rating",
        "question": "Extent digital health work feeds into national policy",
    },
}

SECONDARY_NEEDS = {
    "Infrastructure (connectivity/electricity)": "q19_infrastructure_rating",
    "Leadership support": "q21_leadership_rating",
    "Dissemination capacity": "q23_dissemination_rating",
    "Grant management experience": "q24_grant_mgmt_rating",
}
