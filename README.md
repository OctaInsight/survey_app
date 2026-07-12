# Partner Needs Assessment — Survey & Dashboard

A small Streamlit app with two modes (chosen in the sidebar):

- **Fill out survey** — a 26-question form (institutional profile, the six
  core needs N1–N6, four secondary needs, two open questions). Each
  submission is saved as one row in Supabase.
- **View dashboard** — reads all responses from Supabase and shows
  aggregated results: which need scores lowest (= most urgent) across
  the consortium, secondary-need ratings, categorical breakdowns, the
  open-text answers, and a CSV download of the raw data.

After submitting, a respondent can either jump straight to the dashboard
or fill in another response (e.g. a second institution, or a colleague
answering separately).

---

## 1. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com) (free tier is fine).
2. Open **SQL Editor > New query**, paste the contents of `schema.sql`, and run it.
   This creates the `survey_responses` table and the Row Level Security
   policies that let the app insert and read rows using the public **anon** key.
3. Go to **Project Settings > API** and copy:
   - **Project URL**
   - **anon public** key

You will paste these into Streamlit's secrets in step 3 below — never into the code itself.

## 2. Push this project to GitHub

```bash
git init
git add .
git commit -m "Partner needs assessment survey + dashboard"
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
   url = "https://YOUR-PROJECT-REF.supabase.co"
   key = "YOUR-ANON-PUBLIC-KEY"
   ```

   (This is the same format as `.streamlit/secrets.toml.example` in this repo —
   Streamlit Cloud stores it securely and injects it as `st.secrets` at runtime,
   you don't need a secrets file in the repo itself.)
4. Click **Deploy**. The app will install `requirements.txt` automatically.

Any time you push a new commit to `main`, Streamlit Cloud redeploys automatically.

## 4. Running locally (optional, for testing before you push)

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml with your real Supabase URL + anon key
streamlit run app.py
```

---

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit app: survey form + dashboard |
| `db.py` | Supabase client + insert/fetch helpers |
| `config.py` | Shared question labels, options, and need→column mapping |
| `schema.sql` | Run once in Supabase SQL Editor to create the table + policies |
| `requirements.txt` | Python dependencies |
| `.streamlit/secrets.toml.example` | Template — copy locally, never commit the real one |

## Notes on data access

The SQL policies allow the public **anon** key to both insert and read rows,
since this is meant as an internal consortium tool where every partner can
see the aggregated dashboard. If you'd rather keep individual responses
private and only show aggregates, the cleanest change is to add a Postgres
view that pre-aggregates the data and grant `select` on the view instead of
the raw table — ask if you'd like that version.
