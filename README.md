# Octa Research · HARMONIA project — Partner Needs Assessment

A small Streamlit app with two modes (chosen in the sidebar):

- **Fill out survey** — a 26-question form (institutional profile, the six
  core needs N1–N6, four secondary needs, two open questions), written to
  apply to any type of partner — universities, hospitals, ministries/
  regulators, development organisations, innovation actors, and NGOs alike.
  Each submission is saved as one row in Supabase.
- **View dashboard** — reads all responses from Supabase and shows
  aggregated results: which need scores lowest (= most urgent) across
  the consortium, secondary-need ratings, categorical breakdowns, the
  open-text answers, and a CSV download of the raw data.

After submitting, a respondent can either jump straight to the dashboard
or fill in another response (e.g. a second institution, or a colleague
answering separately).

---

## 1. Add the table to your existing Supabase database

This app uses its own table, `harmonia_needs_survey`, so it can live
alongside any other tables already in your database
(`https://vbjwhjicwnqfhplvjxbx.supabase.co`) without touching them.

1. Open your project's **SQL Editor > New query**.
2. Paste the contents of `schema.sql` and run it. This creates the
   `harmonia_needs_survey` table and the Row Level Security policies that
   let the app insert and read rows using the public **anon** key.
3. Go to **Project Settings > API** and copy the **anon public** key
   (the Project URL is already `https://vbjwhjicwnqfhplvjxbx.supabase.co`).

You will paste the anon key into Streamlit's secrets in step 3 below —
never into the code itself.

## 2. Push this project to GitHub

```bash
git init
git add .
git commit -m "HARMONIA partner needs assessment survey + dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

`.gitignore` already excludes `.streamlit/secrets.toml`, so your Supabase
key will never be pushed to GitHub even if you create that file locally
for testing.

## 3. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**, pick your repo/branch, and set **Main file path** to `app.py`.
3. Before (or right after) deploying, open **Settings > Secrets** for the app
   and paste:

   ```toml
   [supabase]
   url = "https://vbjwhjicwnqfhplvjxbx.supabase.co"
   key = "YOUR-ANON-PUBLIC-KEY"
   ```

   Streamlit Cloud stores this securely and injects it as `st.secrets` at
   runtime — you don't need a secrets file in the repo itself.
4. Click **Deploy**. The app will install `requirements.txt` automatically.

Any time you push a new commit to `main`, Streamlit Cloud redeploys automatically.

## 4. Running locally (optional, for testing before you push)

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml with your real anon key
streamlit run app.py
```

---

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit app: survey form + dashboard (header shows "Octa Research · HARMONIA project") |
| `db.py` | Supabase client + insert/fetch helpers (table: `harmonia_needs_survey`) |
| `config.py` | Shared question labels, options, and need→column mapping |
| `schema.sql` | Run once in Supabase SQL Editor to create the table + policies |
| `requirements.txt` | Python dependencies |
| `.streamlit/secrets.toml.example` | Template — copy locally, never commit the real one |

## Notes

- **Table naming:** the table is `harmonia_needs_survey` (not a generic
  `survey_responses`) specifically so it won't collide with other tables
  already in your shared database.
- **Question wording:** questions were generalised so partners who are not
  clinical/health professionals — policymakers, universities, development
  organisations — can answer meaningfully. Most questions include a
  "not applicable / don't know" option for exactly this reason.
- **Data access:** the SQL policies allow the public **anon** key to both
  insert and read rows, since this is meant as an internal consortium tool
  where every partner can see the aggregated dashboard. If you'd rather
  keep individual responses private and only show aggregates, the cleanest
  change is to add a Postgres view that pre-aggregates the data and grant
  `select` on the view instead of the raw table — ask if you'd like that
  version.
