from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from uuid import uuid4
import random
from sample_data import SAMPLE_COMPANIES, MOCK_SOURCES
from llm_adapter import generate_llm_response

app = FastAPI(title="Company Agent Assistant")

# Allow frontend to call the backend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request models ---
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ResearchRequest(BaseModel):
    session_id: Optional[str] = None
    company: str

class UpdateRequest(BaseModel):
    session_id: Optional[str] = None
    company: str
    section: str
    new_value: Any

class GenerateRequest(BaseModel):
    session_id: Optional[str] = None
    company: str
    mode: Optional[str] = "concise"  # or 'detailed'

# --- In-memory conversation store (session_id -> data)
CONVERSATIONS: Dict[str, Dict[str, Any]] = {}

# --- Helper utilities ---
def new_session(persona: Optional[str] = None) -> str:
    sid = str(uuid4())
    CONVERSATIONS[sid] = {
        "history": [],
        "active_company": None,
        "research_progress": {},
        "persona": persona or "neutral",
        "account_plans": {},
    }
    return sid

def ensure_session(sid: str):
    """Create session entry if missing (idempotent)."""
    if sid not in CONVERSATIONS:
        CONVERSATIONS[sid] = {
            "history": [],
            "active_company": None,
            "research_progress": {},
            "persona": "neutral",
            "account_plans": {},
        }

def append_history(session_id: str, speaker: str, text: str):
    if session_id not in CONVERSATIONS:
        ensure_session(session_id)
    CONVERSATIONS[session_id]["history"].append({"speaker": speaker, "text": text})

# Very small persona detector (rule-based)
PERSONA_KEYWORDS = {
    "confused": ["i don't know", "not sure", "confused", "dont know", "idk"],
    "efficient": ["quick", "short", "summary", "bullet"],
    "chatty": ["story", "fun", "talk", "by the way"],
}

def detect_persona(text: str) -> str:
    t = text.lower()
    scores = {k: 0 for k in PERSONA_KEYWORDS}
    for persona, kws in PERSONA_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                scores[persona] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "neutral"

# Simulated multi-source research that notices conflicts
def multi_source_research(company: str) -> Dict[str, Any]:
    # Aggregate values and detect conflicts
    field_votes: Dict[str, Dict[Any, float]] = {}
    sources_used: List[str] = []

    for src in MOCK_SOURCES:
        sources_used.append(src["name"])
        data = src.get("data", {})
        if company in data:
            for key, val in data[company].items():
                field_votes.setdefault(key, {})
                field_votes[key][val] = field_votes[key].get(val, 0.0) + src.get("weight", 0.0)

    resolved: Dict[str, Any] = {}
    conflicts: Dict[str, List[Any]] = {}

    for field, votes in field_votes.items():
        # sort values by weight
        sorted_votes = sorted(votes.items(), key=lambda x: -x[1])
        top_val, top_score = sorted_votes[0]
        resolved[field] = top_val
        if len(sorted_votes) > 1 and (sorted_votes[0][1] - sorted_votes[1][1]) < 0.25:
            # small margin -> conflict
            conflicts[field] = [v for v, _ in sorted_votes]

    # fallback to sample company if missing
    fallback = SAMPLE_COMPANIES.get(company, {})
    for k, v in fallback.items():
        resolved.setdefault(k, v)

    return {
        "company": company,
        "resolved": resolved,
        "conflicts": conflicts,
        "sources": sources_used,
    }

# Account plan generator (creates sections)
def generate_account_plan(company: str, mode: str = "concise") -> Dict[str, Any]:
    research = multi_source_research(company)
    r = research["resolved"]

    def short(text: str) -> str:
        return text if mode == "detailed" else (text.split(".")[0] + '.')

    plan = {
        "overview": short(f"{company} is in {r.get('industry', 'Unknown')} industry, headquartered at {r.get('headquarters','Unknown')}."),
        "key_metrics": {
            "founded": r.get("founded"),
            "employees": r.get("employees", "Unknown")
        },
        "opportunities": [
            "AI/ML product partnerships",
            "Cloud migration services" if r.get("industry","") == "Technology" else "Market expansion"
        ],
        "risks": [
            "Competition from large incumbents",
            "Regulatory changes"
        ],
        "next_steps": [
            "Validate data from trusted sources",
            "Reach out to product leads for discovery call"
        ],
        "notes": research
    }

    # Use llm_adapter to generate a human-friendly summary and suggested outreach script
    try:
        prompt = (
            f"You are a helpful assistant. Summarize the following research about {company} in 3 bullets and give a one-sentence outreach template:\n\n"
            f"Research: {research}"
        )
        llm_text = generate_llm_response(prompt)
        plan["human_summary"] = llm_text
    except Exception as e:
        plan["human_summary"] = f"(LLM adapter failed: {e})"

    return plan

# --- Endpoints ---
@app.get("/")
def root():
    return {"message": "Company Agent Assistant backend is running. Use /docs for API."}

@app.post("/session/new")
async def create_session(preferred_persona: Optional[str] = None):
    sid = new_session(preferred_persona)
    return {"session_id": sid}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in CONVERSATIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return CONVERSATIONS[session_id]

@app.post("/chat")
async def chat(request: ChatRequest):
    # Create session if missing (accepts client-provided id or auto-creates)
    sid = request.session_id or new_session()
    ensure_session(sid)

    msg = request.message
    persona = detect_persona(msg)
    CONVERSATIONS[sid]["persona"] = persona
    append_history(sid, "user", msg)

    # Very simple intent routing
    lower = msg.lower()
    response = None

    if "research" in lower or any(c.lower() in lower for c in SAMPLE_COMPANIES):
        # if company mentioned, trigger research flow
        mentioned = None
        for c in SAMPLE_COMPANIES:
            if c.lower() in lower:
                mentioned = c
                break
        if mentioned:
            CONVERSATIONS[sid]["active_company"] = mentioned
            append_history(sid, "bot", f"Starting research for {mentioned}...")
            research_result = multi_source_research(mentioned)
            # if conflicts are present, ask user whether to dig deeper
            if research_result["conflicts"]:
                response = (
                    f"I found conflicting information about {', '.join(research_result['conflicts'].keys())}. "
                    f"Sources: {', '.join(research_result['sources'])}. Do you want me to dig deeper or proceed with the highest-confidence values?"
                )
                append_history(sid, "bot", response)
                return {"session_id": sid, "reply": response, "research": research_result}
            else:
                # Create a friendly summary using the llm adapter to make the demo feel natural
                try:
                    prompt = f"Summarize the following research succinctly for a product manager: {research_result}"
                    llm_reply = generate_llm_response(prompt)
                except Exception as e:
                    llm_reply = f"(LLM unavailable: {e})"

                response = f"I researched {mentioned} and prepared a brief summary. {llm_reply} Would you like an account plan?"
                append_history(sid, "bot", response)
                CONVERSATIONS[sid]["research_progress"][mentioned] = research_result
                return {"session_id": sid, "reply": response, "research": research_result}

    # default small-talk / echo with persona
    if persona == "confused":
        response = "No worries — let's take it step by step. Who or which company should we research first?"
    elif persona == "efficient":
        response = "Short answer: I can research companies and generate a concise account plan. Tell me the company name."
    elif persona == "chatty":
        response = "Love the energy! Tell me more, then I can dig into the company you want."
    else:
        # use llm_adapter to produce a friendly onboarding message
        try:
            prompt = f"User said: '{msg}'. Provide a friendly onboarding reply telling them how to ask for company research in one short paragraph."
            onboarding = generate_llm_response(prompt)
            response = onboarding
        except Exception:
            response = f"I received: '{msg}'. I can research companies, generate account plans, and keep track of our conversation. Try asking me to research a company (e.g. 'Research Google')."

    append_history(sid, "bot", response)
    return {"session_id": sid, "reply": response}

@app.post("/research")
async def research_endpoint(request: ResearchRequest):
    sid = request.session_id or new_session()
    ensure_session(sid)
    company = request.company

    append_history(sid, "user", f"Research request: {company}")

    # perform research
    result = multi_source_research(company)

    # save research to the session
    CONVERSATIONS[sid]["research_progress"][company] = result
    append_history(sid, "bot", f"Completed research for {company} (summary attached)")

    # Generate human-friendly summary using LLM adapter
    try:
        prompt = f"""
You are a research assistant. Given the following research JSON, produce:
1) A 2-sentence summary
2) One recommended next step
3) Note if any conflicts exist.

Research: {result}
"""
        analysis = generate_llm_response(prompt)

    except Exception as e:
        analysis = f"(LLM unavailable: {e})"

    # craft reply depending on conflict status
    if result["conflicts"]:
        reply = (
            f"I found conflicts for {company} in fields: {', '.join(result['conflicts'].keys())}. "
            f"{analysis} Would you like me to dig deeper (simulate deeper search) or proceed using the majority values?"
        )
    else:
        reply = (
            f"Research complete for {company}. {analysis} "
            f"Ready to generate an account plan."
        )

    return {
        "session_id": sid,
        "reply": reply,
        "research": result
    }

@app.post("/generate_account_plan")
async def generate_plan(request: GenerateRequest):
    sid = request.session_id or new_session()
    ensure_session(sid)
    company = request.company
    mode = request.mode or "concise"
    plan = generate_account_plan(company, mode)
    CONVERSATIONS[sid]["account_plans"][company] = plan
    append_history(sid, "bot", f"Generated {mode} account plan for {company}.")
    return {"session_id": sid, "account_plan": plan}

@app.post("/update")
async def update_endpoint(request: UpdateRequest):
    sid = request.session_id or new_session()
    ensure_session(sid)
    company = request.company
    section = request.section
    new_value = request.new_value

    # update both the SAMPLE_COMPANIES (mock) and the session account plan if exists
    if company in SAMPLE_COMPANIES:
        SAMPLE_COMPANIES[company][section] = new_value
    # update stored account plan if available
    plan = CONVERSATIONS[sid]["account_plans"].get(company)
    if plan:
        plan[section] = new_value

    append_history(sid, "user", f"Update request: {company} -> {section} = {new_value}")
    append_history(sid, "bot", f"Updated {section} for {company}.")

    return {"session_id": sid, "message": f"Updated '{section}' for {company}", "updated_value": new_value}

@app.get("/companies")
async def list_companies():
    return {"companies": list(SAMPLE_COMPANIES.keys())}

# A small debug endpoint to dump a session (useful for demo)
@app.get("/debug/{session_id}")
async def debug_session(session_id: str):
    if session_id not in CONVERSATIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return CONVERSATIONS[session_id]

# Run with: uvicorn main:app --reload --port 8000
