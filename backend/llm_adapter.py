"""
llm_adapter.py - lightweight adapter for switching between a mock LLM and a real LLM API.

By default this file uses a mock response generator so you can demo offline.
To enable a real LLM, set the environment variable USE_REAL_LLM=true and provide OPENAI_API_KEY.
"""

import os
import random
import json

USE_REAL_LLM = os.getenv("USE_REAL_LLM", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def mock_llm(prompt: str) -> str:
    templates = [
        "Analyzing the request... Here are 3 concise bullets:",
        "Thinking step-by-step: summary and suggestion below:",
        "Simulated research synthesis:",
        "Mock assistant: here's a short summary and an outreach line:"
    ]
    body = random.choice(templates) + "\n\n"
    # very small 'fake' analysis derived from the prompt (keeps it deterministic-ish)
    snippet = prompt
    if len(snippet) > 400:
        snippet = snippet[:400] + "..."
    body += f"- {snippet[:120].replace('\\n',' ')}\n"
    body += "- Suggestion: Validate key facts and schedule discovery call.\n"
    body += "- Outreach: Hi {contact}, we have a short idea to discuss — can we book 20 minutes?\n"
    return body

# Optional OpenAI minimal example (works if USE_REAL_LLM=true and OPENAI_API_KEY set)
def real_llm_openai(prompt: str) -> str:
    try:
        import openai
    except Exception as e:
        return f"(OpenAI client missing: {e})"
    if not OPENAI_API_KEY:
        return "(OPENAI_API_KEY not set)"
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # change to your available model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"(OpenAI call failed: {e})"

def generate_llm_response(prompt: str) -> str:
    """
    Public interface used by main.py
    - If USE_REAL_LLM is set, will try to call the real provider
    - Otherwise returns a mocked response (safe for demos)
    """
    if USE_REAL_LLM:
        # try openai; fallback to mock if it errors
        res = real_llm_openai(prompt)
        if res is None:
            return mock_llm(prompt)
        return res
    return mock_llm(prompt)

# quick CLI test
if __name__ == "__main__":
    print(generate_llm_response("Explain Tesla's competitive position."))
