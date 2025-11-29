# app.py
import io
import streamlit as st
from typing import Any, Dict, List, Tuple

from src.helper import extract_text_from_pdf, ask_openrouter
from src.job_api import fetch_linkedin_job, fetch_naukri_job

# Page config and CSS
st.set_page_config(page_title="AI Job Recommendation System", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    /* Simple dark theme and card styles */
    :root{--muted:#9fb3c8;--accent1:#06b6d4;--accent2:#0ea5a4;}
    .card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:12px;padding:16px;margin-bottom:12px;}
    .logo{width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,var(--accent1),var(--accent2));display:flex;align-items:center;justify-content:center;color:#042027;font-weight:800}
    .job-card{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:12px;border-radius:10px;background:rgba(255,255,255,0.01);margin-bottom:10px;border:1px solid rgba(255,255,255,0.02);}
    .apply-btn{background:linear-gradient(135deg,var(--accent1),var(--accent2));padding:8px 12px;border-radius:8px;color:#042027;font-weight:700;text-decoration:none;}
    .muted{color:var(--muted)}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div style="display:flex;gap:12px;align-items:center">
      <div class="logo">AI</div>
      <div>
        <h2 style="margin:0">AI Job Recommender</h2>
        <div class="muted">Smart resume analysis + global job recommendations</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.header("Search settings")
    location_input = st.text_input("Location(s) (comma-separated). Use 'Remote' for global:", value="Remote")
    rows = st.slider("Max results per provider", 10, 200, 60, 10)
    show_raw = st.checkbox("Show raw job JSON (debug)", value=False)
    st.markdown("---")
    st.markdown("Make sure OPENROUTER_API_KEY and APIFY_API_KEY are set in your environment (.env).")

# Helpers
def normalize_model_keywords(raw_text: str) -> Tuple[List[str], str]:
    if not raw_text:
        return [], ""
    txt = raw_text.strip().replace("\r", "")
    if "," in txt:
        parts = [p.strip() for p in txt.split(",") if p.strip()]
    elif "\n" in txt:
        parts = [p.strip() for p in txt.split("\n") if p.strip()]
    else:
        parts = [p.strip() for p in txt.split() if p.strip()]
    search_title = ", ".join(parts)
    return parts, search_title

def get_field(job: Dict[str, Any], candidates: List[str], join_with: str = ", ") -> str:
    # Support nested path like 'company.name' (very small utility)
    def resolve_path(obj, path):
        cur = obj
        for part in path.split("."):
            if isinstance(cur, dict):
                cur = cur.get(part)
            else:
                return None
            if cur is None:
                return None
        return cur

    for key in candidates:
        val = resolve_path(job, key) if "." in key else job.get(key)
        if val is None:
            continue
        if isinstance(val, list):
            out = []
            for item in val:
                if isinstance(item, dict):
                    for sub in ("location", "city", "name", "address", "formattedLocation"):
                        if sub in item and item[sub]:
                            out.append(str(item[sub])); break
                    else:
                        out.append(str(item))
                else:
                    out.append(str(item))
            if out:
                return join_with.join(out)
        if isinstance(val, dict):
            for sub in ("location", "city", "name", "address", "formattedLocation"):
                if sub in val and val[sub]:
                    return str(val[sub])
            try:
                return ", ".join(str(v) for v in val.values() if v)
            except Exception:
                pass
        if isinstance(val, (str, int, float)):
            s = str(val).strip()
            if s:
                return s
    return None

# Upload & analysis
st.markdown("<div class='card'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
st.markdown("</div>", unsafe_allow_html=True)

if not uploaded_file:
    st.info("Upload a PDF resume to get started.")
    st.stop()

# Read bytes to use as cache key
resume_bytes = uploaded_file.read()
if not resume_bytes:
    st.error("Uploaded file empty.")
    st.stop()

# Cached resume analysis (use LLM via helper)
@st.cache_data(show_spinner=False)
def analyze_resume_cached(resume_b: bytes) -> Dict[str, str]:
    # recreate a file-like object for extract_text_from_pdf
    f = io.BytesIO(resume_b)
    f.seek(0)
    out = {"resume_text": "", "summary": "", "gaps": "", "roadmap": ""}
    try:
        text = extract_text_from_pdf(f)
    except Exception as e:
        out["summary"] = f"[Extraction error] {e}"
        return out
    out["resume_text"] = text or ""
    if not text:
        out["summary"] = "[No text extracted from PDF]"
        return out
    # call LLM prompts (wrapped to avoid entire failure)
    try:
        out["summary"] = ask_openrouter(f"Summarize this resume highlighting the skills, education, and experience: {text}", max_tokens=500).strip()
    except Exception as e:
        out["summary"] = f"[API error] {e}"
    try:
        out["gaps"] = ask_openrouter(f"Analyze this resume and highlight missing skills, certifications and experience needed for job opportunities: {text}", max_tokens=500).strip()
    except Exception as e:
        out["gaps"] = f"[API error] {e}"
    try:
        out["roadmap"] = ask_openrouter(f"Based on this resume, suggest a future roadmap to improve career prospects (skills, certifications, industry exposure): {text}", max_tokens=500).strip()
    except Exception as e:
        out["roadmap"] = f"[API error] {e}"
    return out

with st.spinner("Analyzing resume..."):
    analysis = analyze_resume_cached(resume_bytes)

resume_text = analysis.get("resume_text", "")
summary = analysis.get("summary", "")
gaps = analysis.get("gaps", "")
roadmap = analysis.get("roadmap", "")

# Show results
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='card'><strong>📃 Resume Summary</strong><div class='muted'>"+ (summary or "No summary") + "</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='card'><strong>🔍 Skill Gaps</strong><div class='muted'>"+ (gaps or "No skill gap analysis") + "</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='card'><strong>🚀 Roadmap</strong><div class='muted'>"+ (roadmap or "No roadmap") + "</div></div>", unsafe_allow_html=True)

# Keyword extraction and override
st.markdown("---")
st.markdown("### 🔑 Job title & keyword extraction")
if st.button("Auto-extract keywords from summary"):
    try:
        prompt = ("Based on this resume summary, suggest a suitable job title and keywords for job search. "
                  "Return a comma-separated list only (no explanation).\n\nSummary: " + (summary or resume_text))
        keywords_raw = ask_openrouter(prompt, max_tokens=60).strip()
    except Exception as e:
        st.error(f"Keyword extraction failed: {e}")
        keywords_raw = ""
    parts, search_title = normalize_model_keywords(keywords_raw)
    st.session_state["parts"] = parts
    st.session_state["search_title"] = search_title

parts = st.session_state.get("parts", [])
search_title = st.session_state.get("search_title", "")
manual = st.text_input("Or enter job title/keywords (comma-separated):", value=search_title)
if manual:
    parts, search_title = normalize_model_keywords(manual)
    st.session_state["parts"] = parts
    st.session_state["search_title"] = search_title

st.markdown(f"**Using keywords:** {', '.join(parts) if parts else 'None'}")

# Job fetch (with debug)
st.markdown("---")
if st.button("Get Job Recommendations"):
    if not search_title:
        st.warning("Please provide job title/keywords via auto-extract or manual input.")
        st.stop()

    # Defensive coercion
    if isinstance(search_title, (list, tuple, set)):
        search_title = ", ".join(map(str, search_title))
    elif not isinstance(search_title, str):
        search_title = str(search_title or "")

    st.write("**DEBUG**: search_title =", search_title, " | location =", location_input)

    # fetch LinkedIn
    with st.spinner("Fetching LinkedIn jobs..."):
        try:
            linkedin_jobs = fetch_linkedin_job(search_title, location=location_input or "Remote", rows=rows)
        except Exception as e:
            st.error(f"LinkedIn fetch error: {e}")
            linkedin_jobs = []

    # fetch Naukri
    with st.spinner("Fetching Naukri jobs..."):
        try:
            naukri_jobs = fetch_naukri_job(search_title, rows=rows)
        except Exception as e:
            st.error(f"Naukri fetch error: {e}")
            naukri_jobs = []

    # Display LinkedIn jobs
    st.header("💼 LinkedIn — Recommendations")
    if not linkedin_jobs:
        st.warning("No LinkedIn jobs found.")
    else:
        for job in linkedin_jobs:
            title = get_field(job, ["title", "jobTitle", "job_title", "position", "vacancy"]) or "N/A"
            company = get_field(job, ["company", "companyName", "employer", "hiringOrganization.name"]) or "N/A"
            location = get_field(job, ["location", "jobLocation", "formattedLocation", "locations", "place", "meta.location"]) or "N/A"
            url = job.get("url") or job.get("jobUrl") or job.get("applyUrl") or "#"
            desc = job.get("description") or job.get("summary") or ""
            st.markdown("<div class='job-card'>", unsafe_allow_html=True)
            st.markdown(f"<div style='flex:1'><div style='font-weight:700'>{title}</div><div class='muted'>{company}</div><div class='muted'>{desc[:220]}{'...' if len(desc)>220 else ''}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:right;min-width:160px;'><div class='muted'>📍 Location</div><div style='font-weight:700'>{location}</div><div style='margin-top:8px;'><a class='apply-btn' href='{url}' target='_blank'>Apply</a></div></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if show_raw:
                st.json(job)

    # Display Naukri jobs
    st.header("💼 Naukri.com — Recommendations")
    if not naukri_jobs:
        st.warning("No Naukri jobs found.")
    else:
        for job in naukri_jobs:
            title = get_field(job, ["title", "jobTitle", "job_title", "position"]) or "N/A"
            company = get_field(job, ["companyName", "company", "employer"]) or "N/A"
            location = get_field(job, ["location", "locations", "place"]) or "N/A"
            url = job.get("jobUrl") or job.get("url") or "#"
            st.markdown("<div class='job-card'>", unsafe_allow_html=True)
            st.markdown(f"<div style='flex:1'><div style='font-weight:700'>{title}</div><div class='muted'>{company}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:right;min-width:160px;'><div class='muted'>📍 Location</div><div style='font-weight:700'>{location}</div><div style='margin-top:8px;'><a class='apply-btn' href='{url}' target='_blank'>Apply</a></div></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if show_raw:
                st.json(job)

    st.success("✅ Job recommendations fetched.")
