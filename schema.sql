-- ============================================================
-- Partner Needs Assessment Survey — Supabase schema
-- Run this once in: Supabase Dashboard > SQL Editor > New query
-- ============================================================

create table if not exists public.survey_responses (
    id                      uuid primary key default gen_random_uuid(),
    created_at              timestamptz not null default now(),

    -- A. Institutional profile
    institution_name        text,
    country                 text,
    org_type                text,
    org_type_other          text,
    respondent_name         text,
    staff_count             text,

    -- B1. Fragmentation (N1)
    q1_systems_count         text,
    q2_integration_rating    int2,
    q3_coordination          text,

    -- B2. Interoperability & data governance (N2)
    q4_governance_policy     text,
    q5_standards             jsonb,
    q6_data_sharing_rating   int2,

    -- B3. Responsible AI & validation (N3)
    q7_ai_use                text,
    q8_bias_audit            text,
    q9_ai_confidence_rating  int2,

    -- B4. Human capital (N4)
    q10_trained_staff        text,
    q11_staffing_rating      int2,
    q12_turnover_impact      text,

    -- B5. Scale-up gap (N5)
    q13_pilot_not_scaled     text,
    q14_scaleup_barriers     jsonb,
    q14_other_barrier        text,
    q15_scaleup_readiness    int2,

    -- B6. Policy uptake & sustainability (N6)
    q16_policy_link          text,
    q17_policy_feed_rating   int2,
    q18_financing_mechanism  text,

    -- C. Secondary needs
    q19_infrastructure_rating int2,
    q20_gender_policy         text,
    q21_leadership_rating     int2,
    q22_eu_projects_count     text,
    q23_dissemination_rating  int2,
    q24_grant_mgmt_rating     int2,

    -- D. Open questions
    q25_biggest_need         text,
    q26_valuable_support     text
);

-- ------------------------------------------------------------
-- Row Level Security
-- ------------------------------------------------------------
-- This is an internal consortium tool: every partner should be able
-- to submit a response (INSERT) and the dashboard needs to read all
-- responses (SELECT) using the same public "anon" key.
-- The policies below allow both using the anon key. If you want
-- submissions to be public but the dashboard to require a separate
-- login/service key instead, remove the "select" policy and read
-- data from the app using the service_role key kept server-side only.

alter table public.survey_responses enable row level security;

create policy "Allow anonymous insert"
    on public.survey_responses
    for insert
    to anon
    with check (true);

create policy "Allow anonymous read"
    on public.survey_responses
    for select
    to anon
    using (true);

-- Optional: index to speed up dashboard filters by country / org type
create index if not exists idx_survey_country on public.survey_responses (country);
create index if not exists idx_survey_org_type on public.survey_responses (org_type);
