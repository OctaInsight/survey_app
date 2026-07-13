"""
TEMPORARY DIAGNOSTIC — paste this at the very top of app.py (right after
`import streamlit as st`), redeploy, then look at the running app in the
browser. It cannot crash, even if supabase/plotly are missing, because it
only uses the standard library + streamlit.

Remove this block once the real issue is found.
"""
import subprocess
import sys
import os

import streamlit as st

st.set_page_config(page_title="DEBUG", page_icon="🔧")
st.title("🔧 Environment diagnostic")

st.subheader("1. Python being used")
st.code(sys.executable)

st.subheader("2. Installed packages (pip list)")
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
st.code(result.stdout or result.stderr)

st.subheader("3. Files Streamlit Cloud sees in the app's working directory")
cwd = os.getcwd()
st.write("Working directory:", cwd)
for root, dirs, files in os.walk(cwd):
    # skip noisy folders
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "venv", ".venv")]
    for f in files:
        st.write(os.path.relpath(os.path.join(root, f), cwd))

st.subheader("4. Contents of requirements.txt, if found")
req_path = os.path.join(cwd, "requirements.txt")
if os.path.exists(req_path):
    with open(req_path) as fh:
        st.code(fh.read())
else:
    st.error(f"requirements.txt NOT FOUND at: {req_path}")

st.stop()  # prevents the rest of app.py from running while debugging
