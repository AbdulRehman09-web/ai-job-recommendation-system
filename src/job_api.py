# src/job_api.py
import os
from dotenv import load_dotenv
from apify_client import ApifyClient
from apify_client.errors import ApifyApiError

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
if not APIFY_API_KEY:
    # do not raise on import; raise inside functions for clearer errors
    APIFY_API_KEY = None

# Actor IDs used previously; change if you want other actors
LINKEDIN_ACTOR_ID = "BHzefUZlZRKWxkTck"
NAUKRI_ACTOR_ID = "wsrn5gy5C4EDeYCcD"

def _ensure_client():
    if not APIFY_API_KEY:
        raise RuntimeError("APIFY_API_KEY not set in environment (.env).")
    return ApifyClient(APIFY_API_KEY)

def _normalize_search_query(search_query):
    if search_query is None:
        return ""
    if isinstance(search_query, str):
        return search_query.strip()
    if isinstance(search_query, (list, tuple, set)):
        return ", ".join(str(x).strip() for x in search_query if str(x).strip())
    return str(search_query).strip()

def fetch_linkedin_job(search_query, location="Remote", rows=60):
    """
    Call Apify LinkedIn actor. Returns list of job dicts.
    Raises RuntimeError with descriptive message on failure.
    """
    client = _ensure_client()
    title = _normalize_search_query(search_query)
    if not title:
        raise RuntimeError("search_query (title) is empty for LinkedIn actor.")

    run_input = {
        "title": title,
        "location": location or "Remote",
        "rows": int(rows),
        "proxy": {"useApifyProxy": True, "ApifyProxyGroups": ["SHADER"]},
    }

    try:
        run = client.actor(LINKEDIN_ACTOR_ID).call(run_input=run_input)
    except ApifyApiError as e:
        raise RuntimeError(f"Apify LinkedIn actor call failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to call LinkedIn actor: {e}")

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        return []

    try:
        items = list(client.dataset(dataset_id).iterate_items())
    except Exception as e:
        raise RuntimeError(f"Failed to read Apify dataset: {e}")
    return items

def fetch_naukri_job(search_query, rows=60):
    """
    Call Apify Naukri actor. Returns list of job dicts.
    """
    client = _ensure_client()
    keyword = _normalize_search_query(search_query)
    if not keyword:
        raise RuntimeError("search_query (keyword) is empty for Naukri actor.")

    run_input = {
        "keyword": keyword,
        "maxJobs": int(rows),
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
        "jobType": "all",
    }

    try:
        run = client.actor(NAUKRI_ACTOR_ID).call(run_input=run_input)
    except ApifyApiError as e:
        raise RuntimeError(f"Apify Naukri actor call failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to call Naukri actor: {e}")

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        return []

    try:
        items = list(client.dataset(dataset_id).iterate_items())
    except Exception as e:
        raise RuntimeError(f"Failed to read Apify dataset: {e}")
    return items
