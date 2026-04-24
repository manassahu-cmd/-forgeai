"""
logic.py — Hardened Agent + Judge (No LiteLLM, Direct Gemini SDK)
=================================================================
All API key handling is silent. Falls back gracefully on any error.
"""

import os
import json
import textwrap
import logging
from dataclasses import dataclass, field
from typing import Generator

import google.generativeai as genai
from tavily import TavilyClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — plain model names for google-generativeai SDK (no gemini/ prefix)
# ---------------------------------------------------------------------------
PRIMARY_MODEL   = "gemini-2.5-flash"
FALLBACK_MODEL  = "gemini-2.5-flash-lite"
FALLBACK_MODEL2 = "gemini-2.5-pro"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------
@dataclass
class AgentStep:
    step_type: str   # "thought" | "action" | "observation" | "final"
    content: str
    tool_name: str = ""
    tool_input: str = ""


@dataclass
class AgentResult:
    names: list[dict] = field(default_factory=list)
    research_context: str = ""
    error: str = ""


# ---------------------------------------------------------------------------
# Key Helper — always re-reads from env so a refreshed key is picked up
# ---------------------------------------------------------------------------
def _fresh_keys() -> tuple[str, str]:
    """Re-load .env on every call so swapped keys are picked up immediately."""
    load_dotenv(override=True)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    return gemini_key, tavily_key


# ---------------------------------------------------------------------------
# Auth error detection — tight, does NOT fire on quota/rate-limit errors
# ---------------------------------------------------------------------------
def _is_auth_error(err_str: str) -> bool:
    err = err_str.lower()
    if "api_key_invalid" in err:
        return True
    if "api key not valid" in err:
        return True
    if "invalid api key" in err:
        return True
    if "401" in err:
        return True
    # 403 only when it's a permissions error, not a free-tier quota block
    if "403" in err and "quota" not in err and "rate" not in err and "limit" not in err:
        return True
    return False


# ---------------------------------------------------------------------------
# Core call helper — tries all models, skips on quota/model errors
# ---------------------------------------------------------------------------
def _generate(api_key: str, prompt: str, **gen_kwargs) -> tuple[str, str]:
    """
    Call Gemini with fallback. Returns (response_text, model_name_used).
    Raises RuntimeError on auth failure or if all models are exhausted.
    """
    genai.configure(api_key=api_key)
    last_err = None
    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL, FALLBACK_MODEL2]:
        try:
            m = genai.GenerativeModel(model_name)
            resp = m.generate_content(prompt, **gen_kwargs)
            return resp.text, model_name
        except Exception as e:
            err_str = str(e)
            if _is_auth_error(err_str):
                raise RuntimeError(
                    "🔑 API Key Issue: Your Gemini key appears to be invalid or expired. "
                    "Please update GEMINI_API_KEY in your .env file and click Generate again."
                ) from e
            logger.warning("Model %s unavailable: %s", model_name, e)
            last_err = e
    raise RuntimeError(
        f"All Gemini models are currently unavailable (quota/rate-limit). "
        f"Wait a few minutes and try again. Last error: {last_err}"
    )


# ---------------------------------------------------------------------------
# StartupNameAgent
# ---------------------------------------------------------------------------
class StartupNameAgent:
    def __init__(self, api_key: str, tavily_api_key: str):
        self.api_key = api_key
        self.model_name = PRIMARY_MODEL   # updated on first successful call
        self.tavily = TavilyClient(api_key=tavily_api_key)

    def _call_llm(self, prompt: str, temperature: float = 0.8) -> str:
        text, model_used = _generate(
            self.api_key,
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature),
        )
        self.model_name = model_used
        return text

    def _tavily_search(self, query: str, max_results: int = 5) -> str:
        try:
            response = self.tavily.search(
                query=query, max_results=max_results, include_answer=True
            )
            lines = []
            if response.get("answer"):
                lines.append(f"Summary: {response['answer']}\n")
            for i, r in enumerate(response.get("results", []), 1):
                lines.append(
                    f"[{i}] {r.get('title')}\n"
                    f"    {r.get('content', '')[:300]}\n"
                    f"    Source: {r.get('url')}"
                )
            return "\n".join(lines) if lines else "No results found."
        except Exception as exc:
            return f"Search failed: {exc}"

    def _plan_searches(self, industry: str, keywords: str, vibe: str) -> list[str]:
        prompt = (
            f"Plan 2 web search queries to find competitors and naming trends for a "
            f"{industry} startup with vibe '{vibe}' and mission: {keywords}. "
            f"Output ONLY a JSON array of strings."
        )
        try:
            raw = self._call_llm(prompt, temperature=0.4)
            queries = json.loads(raw.replace("```json", "").replace("```", "").strip())
            return queries[:2]
        except Exception:
            return [f"{industry} startup naming trends 2025", f"top {industry} startups"]

    def _generate_names(
        self, industry: str, keywords: str, vibe: str, research_context: str
    ) -> list[dict]:
        prompt = textwrap.dedent(f"""
            You are a world-class brand strategist.
            Generate exactly 5 unique startup names for a {industry} company.
            Brand vibe: {vibe}. Core mission: {keywords}.
            Market context (use to avoid existing names): {research_context[:1200]}

            Rules:
            - Names must be original, pronounceable, and memorable
            - Avoid clichés like "Nova", "Flux", "Spark", "Nexus"
            - Each name should have a clear etymological hook

            Respond ONLY with a valid JSON array:
            [
              {{"name": "...", "rationale": "One-sentence brand story.", "domain": "e.g. getname.io"}}
            ]
        """).strip()
        try:
            raw = self._call_llm(prompt, temperature=0.85)
            return json.loads(raw.replace("```json", "").replace("```", "").strip())
        except Exception as e:
            return [{"name": "ParseError", "rationale": str(e), "domain": ""}]

    def run(
        self, industry: str, keywords: str, vibe: str
    ) -> Generator[AgentStep, None, AgentResult]:
        yield AgentStep(
            step_type="thought",
            content=f"Scoping the **{industry}** landscape to find naming opportunities.",
        )

        queries = self._plan_searches(industry, keywords, vibe)
        research_parts = []

        for query in queries:
            yield AgentStep(
                step_type="action",
                content=f"Searching live web: *{query}*",
                tool_name="tavily_search",
                tool_input=query,
            )
            result = self._tavily_search(query)
            research_parts.append(result)
            yield AgentStep(step_type="observation", content=result[:600] + "…")

        yield AgentStep(
            step_type="thought",
            content="Synthesising market signals into distinct brand identities…",
        )

        research_context = "\n\n".join(research_parts)
        names_data = self._generate_names(industry, keywords, vibe, research_context)

        yield AgentStep(step_type="final", content=json.dumps(names_data))
        return AgentResult(names=names_data, research_context=research_context)


# ---------------------------------------------------------------------------
# ForgeScorer  (LLM-as-Judge)
# ---------------------------------------------------------------------------
class ForgeScorer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = PRIMARY_MODEL   # updated on first successful call

    def score_names(
        self, industry: str, names: list[dict], context: str
    ) -> list[dict] | dict:
        prompt = textwrap.dedent(f"""
            You are an impartial brand analyst. Score these 5 startup names for a {industry} company.
            Market context: {context[:600]}
            Names: {json.dumps(names)}

            Scoring criteria (1–10 each, averaged):
            1. Memorability — easy to recall, spell, say aloud
            2. Domain availability — how likely a clean .com/.io exists
            3. Industry fit — signals the right sector and vibe
            4. Uniqueness — differentiated from known competitors

            Respond ONLY with a valid JSON array:
            [{{"name": "...", "score": <avg float 1-10>, "verdict": "One punchy sentence."}}]
        """).strip()

        # Attempt 1: JSON MIME mode
        try:
            text, model_used = _generate(
                self.api_key,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.15,
                ),
            )
            self.model_name = model_used
            return json.loads(text)
        except RuntimeError:
            raise   # propagate auth errors
        except Exception as e1:
            logger.warning("Judge JSON-mode failed: %s", e1)

        # Attempt 2: Plain text + manual strip
        try:
            text, model_used = _generate(
                self.api_key,
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.15),
            )
            self.model_name = model_used
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except RuntimeError:
            raise
        except Exception as e2:
            logger.error("Judge fallback also failed: %s", e2)
            return {"error": f"Judge evaluation failed: {e2}"}


# ---------------------------------------------------------------------------
# Public façade — called by app.py
# ---------------------------------------------------------------------------
def run_pipeline(
    industry: str, keywords: str, vibe: str
) -> tuple[Generator, "ForgeScorer", str, str]:
    """
    Returns (generator, scorer, agent_model_name, judge_model_name).
    Raises RuntimeError with a user-friendly message on key/config problems.
    """
    gemini_key, tavily_key = _fresh_keys()

    if not gemini_key:
        raise RuntimeError("Missing GEMINI_API_KEY — add it to your .env file.")
    if not tavily_key:
        raise RuntimeError("Missing TAVILY_API_KEY — add it to your .env file.")

    agent = StartupNameAgent(api_key=gemini_key, tavily_api_key=tavily_key)
    scorer = ForgeScorer(api_key=gemini_key)
    gen = agent.run(industry, keywords, vibe)
    return gen, scorer, agent.model_name, scorer.model_name
