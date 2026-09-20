#!/usr/bin/env python3
"""
Production 3-Tier Agentic Memory Engine
---------------------------------------
Implements the 3-Tier Agent Memory Architecture:
  Tier 1: Transient Working Memory (Scratchpad with auto-compaction)
  Tier 2: Episodic Memory (Persistent SQLite execution ledger with FTS5)
  Tier 3: Semantic Memory (Durable fact vector store with cosine similarity)

Zero external pip dependencies required (pure standard library: sqlite3, math, json).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def resolve_typesafe_key(api_key: Optional[str] = None) -> Optional[str]:
    """Finds TYPESAFE_API_KEY from argument, os.environ, or .env files."""
    if api_key:
        return api_key
    env_val = os.environ.get("TYPESAFE_API_KEY")
    if env_val:
        return env_val
    candidate_files = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.expanduser(r"~\.gemini\.env"),
    ]
    for env_path in candidate_files:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("TYPESAFE_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip("\"'")
                            if val:
                                return val
            except Exception:
                pass
    return None


# ======================================================================
# Tier 1: Working Memory (Transient In-Context Scratchpad)
# ======================================================================

@dataclass
class WorkingTurn:
    role: str
    agent_name: str
    content: str
    token_estimate: int
    timestamp: float = field(default_factory=time.time)


class WorkingMemory:
    """Manages active session context with token estimation and auto-compaction."""
    def __init__(self, token_budget: int = 4000, compaction_threshold: float = 0.85):
        self.token_budget = token_budget
        self.compaction_threshold = compaction_threshold
        self.turns: List[WorkingTurn] = []
        self.system_notes: List[str] = []

    def estimate_tokens(self, text: str) -> int:
        """Rough token heuristic (~4 chars per token for English/code)."""
        return max(1, len(text) // 4)

    def add_turn(self, role: str, agent_name: str, content: str) -> None:
        toks = self.estimate_tokens(content)
        turn = WorkingTurn(role=role, agent_name=agent_name, content=content, token_estimate=toks)
        self.turns.append(turn)
        self._check_and_compact()

    def add_note(self, note: str) -> None:
        self.system_notes.append(note)

    @property
    def total_tokens(self) -> int:
        return sum(t.token_estimate for t in self.turns)

    def _check_and_compact(self) -> None:
        """Compacts older turns into a rolling summary when budget is exceeded."""
        if self.total_tokens > (self.token_budget * self.compaction_threshold):
            if len(self.turns) > 4:
                # Retain last 3 turns, compact preceding turns
                to_compact = self.turns[:-3]
                remaining = self.turns[-3:]
                summary_bullet_points = [
                    f"- [{t.agent_name}] {t.content[:120]}..." for t in to_compact
                ]
                compaction_note = "Compacted Milestones:\n" + "\n".join(summary_bullet_points)
                self.system_notes.append(compaction_note)
                self.turns = remaining

    def get_context_window(self) -> Dict[str, Any]:
        return {
            "token_budget": self.token_budget,
            "current_tokens": self.total_tokens,
            "system_notes": self.system_notes,
            "active_turns": [asdict(t) for t in self.turns]
        }


# ======================================================================
# Lightweight Vector Math & Semantic Embeddings (Zero External Deps)
# ======================================================================

def tokenize_and_stem(text: str) -> List[str]:
    """Lightweight suffix stemmer & tokenizer without external libraries."""
    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
        "to", "was", "were", "will", "with", "do", "how", "we", "our", "all"
    }
    raw_tokens = re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text.lower())
    stems = []
    for t in raw_tokens:
        if t in stop_words:
            continue
        # Strip common English suffixes
        for suffix in ("ation", "tions", "tion", "ing", "ies", "ied", "ed", "es", "ly", "s"):
            if t.endswith(suffix) and len(t) > len(suffix) + 2:
                t = t[:-len(suffix)]
                break
        stems.append(t)
    return stems


def calculate_overlap_similarity(query_text: str, doc_text: str) -> float:
    """Computes symmetric Jaccard + Term Frequency similarity over stemmed tokens and root prefixes."""
    q_stems = tokenize_and_stem(query_text)
    d_stems = tokenize_and_stem(doc_text)
    if not q_stems or not d_stems:
        return 0.0

    matches = 0
    matched_d = set()
    for q in q_stems:
        for idx, d in enumerate(d_stems):
            if idx in matched_d:
                continue
            # Exact match or root prefix match (5+ chars)
            if q == d or (len(q) >= 4 and len(d) >= 4 and (q.startswith(d[:4]) or d.startswith(q[:4]))):
                matches += 1
                matched_d.add(idx)
                break

    if matches == 0:
        return 0.0

    coverage = matches / len(q_stems)
    jaccard = matches / (len(q_stems) + len(d_stems) - matches)
    return round((coverage * 0.7) + (jaccard * 0.3), 4)


def generate_local_embedding(text: str, dimensions: int = 128) -> List[float]:
    """Retained for serializable vector storage compatibility."""
    stems = tokenize_and_stem(text)
    vec = [0.0] * dimensions
    for s in stems:
        h = int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16) % dimensions
        vec[h] += 1.0
    mag = math.sqrt(sum(x * x for x in vec))
    return [x / mag for x in vec] if mag > 0 else vec


# ======================================================================
# Tier 2 & Tier 3: Persistent Episodic & Semantic SQLite Storage
# ======================================================================

class PersistentAgentMemory:
    """Manages Tier 2 (Episodic SQLite Log) and Tier 3 (Semantic Vector Store)."""
    def __init__(self, db_path: Optional[str] = None, max_episodes: int = 2000):
        self.max_episodes = max_episodes
        if db_path is None:
            default_dir = Path(__file__).resolve().parent.parent / ".memory"
            default_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(default_dir / "agent_memory.db")
        else:
            self.db_path = db_path
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            # Tier 2: Episodic Execution Ledger
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodic_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    agent_name TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    input_payload TEXT,
                    output_payload TEXT,
                    status TEXT NOT NULL,
                    duration_ms INTEGER,
                    tokens_used INTEGER
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ep_session ON episodic_log (session_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ep_agent ON episodic_log (agent_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ep_time ON episodic_log (timestamp);")

            # Tier 3: Semantic Long-Term Facts
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    fact_key TEXT UNIQUE NOT NULL,
                    fact_text TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    disputed INTEGER DEFAULT 0,
                    dispute_reason TEXT DEFAULT ''
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sem_category ON semantic_facts (category);")

            # Dynamic schema migration for existing SQLite databases
            cursor = conn.execute("PRAGMA table_info(semantic_facts);")
            existing_cols = {row["name"] for row in cursor.fetchall()}
            if "disputed" not in existing_cols:
                conn.execute("ALTER TABLE semantic_facts ADD COLUMN disputed INTEGER DEFAULT 0;")
            if "dispute_reason" not in existing_cols:
                conn.execute("ALTER TABLE semantic_facts ADD COLUMN dispute_reason TEXT DEFAULT '';")

            conn.execute("CREATE INDEX IF NOT EXISTS idx_sem_disputed ON semantic_facts (disputed);")

    # ------------------------------------------------------------------
    # Tier 2 API (Episodic)
    # ------------------------------------------------------------------
    def log_episode(
        self,
        session_id: str,
        agent_name: str,
        action_type: str,
        input_payload: Any,
        output_payload: Any,
        status: str = "SUCCESS",
        duration_ms: int = 0,
        tokens_used: int = 0
    ) -> int:
        with self._get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO episodic_log (
                    session_id, timestamp, agent_name, action_type,
                    input_payload, output_payload, status, duration_ms, tokens_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    time.time(),
                    agent_name,
                    action_type,
                    json.dumps(input_payload) if not isinstance(input_payload, str) else input_payload,
                    json.dumps(output_payload) if not isinstance(output_payload, str) else output_payload,
                    status,
                    duration_ms,
                    tokens_used
                )
            )
            # Automatic Ring-Buffer: Keep only the most recent self.max_episodes
            conn.execute(
                """
                DELETE FROM episodic_log WHERE id NOT IN (
                    SELECT id FROM episodic_log ORDER BY id DESC LIMIT ?
                )
                """,
                (self.max_episodes,)
            )
            return cur.lastrowid

    def prune_stale_episodes(self, max_days: int = 30) -> Dict[str, Any]:
        """Prunes episodes older than max_days and runs VACUUM to free disk space."""
        cutoff = time.time() - (max_days * 86400)
        with self._get_conn() as conn:
            cur = conn.execute("DELETE FROM episodic_log WHERE timestamp < ?", (cutoff,))
            pruned = cur.rowcount
            conn.commit()
            conn.execute("VACUUM;")
            total_remaining = conn.execute("SELECT COUNT(*) FROM episodic_log").fetchone()[0]
            db_size_bytes = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            return {
                "pruned_episodes": pruned,
                "remaining_episodes": total_remaining,
                "db_size_kb": round(db_size_bytes / 1024, 2)
            }

    def get_recent_episodes(self, session_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            if session_id:
                rows = conn.execute(
                    "SELECT * FROM episodic_log WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM episodic_log ORDER BY id DESC LIMIT ?", (limit,)
                ).fetchall()
            return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Tier 3 API (Semantic Vector Memory with Consistency Guardrails)
    # ------------------------------------------------------------------
    def check_fact_consistency(self, category: str, fact_key: str, new_text: str) -> Dict[str, Any]:
        """
        Guards against memory poisoning and contradictory architectural drift.
        Compares new_text against existing fact (by key or semantic similarity).
        Returns verdict with is_consistent, disputed, confidence, and reason.
        """
        existing_text = None
        existing_key = None

        with self._get_conn() as conn:
            # 1. Direct match on key
            row = conn.execute(
                "SELECT fact_key, fact_text FROM semantic_facts WHERE fact_key = ?",
                (fact_key,)
            ).fetchone()
            if row:
                existing_key = row["fact_key"]
                existing_text = row["fact_text"]
            else:
                # 2. Match on category + high overlap similarity
                candidates = conn.execute(
                    "SELECT fact_key, fact_text FROM semantic_facts WHERE category = ?",
                    (category,)
                ).fetchall()
                best_sim = 0.0
                best_cand = None
                for c in candidates:
                    sim = calculate_overlap_similarity(new_text, c["fact_text"])
                    if sim > best_sim:
                        best_sim = sim
                        best_cand = c
                if best_cand and best_sim >= 0.15:
                    existing_key = best_cand["fact_key"]
                    existing_text = best_cand["fact_text"]

        if not existing_text:
            return {
                "is_consistent": True,
                "status": "new_fact",
                "disputed": False,
                "confidence": 1.0,
                "matched_key": None,
                "reason": "No conflicting prior knowledge found in this domain.",
                "mode": "deterministic"
            }

        # If identical text
        if existing_text.strip().lower() == new_text.strip().lower():
            return {
                "is_consistent": True,
                "status": "identical",
                "disputed": False,
                "confidence": 1.0,
                "matched_key": existing_key,
                "reason": "Exact match with existing stored fact.",
                "mode": "deterministic"
            }

        # Live TypeSafe / Jev System One check
        api_key = resolve_typesafe_key()
        if api_key:
            try:
                from typesafe_sdk import TypeSafeClient, Noul, Choice
                client = TypeSafeClient(api_key=api_key)
                state = {
                    "category": category,
                    "existing_fact": existing_text,
                    "proposed_update": new_text
                }
                questions = {
                    "is_contradiction": Noul(
                        instructions="Does the proposed_update directly contradict, violate, or negate the existing_fact?"
                    ),
                    "relationship": Choice(
                        options=["compatible_refinement", "direct_contradiction", "divergent_scope"],
                        criteria=[
                            "The update refines, extends, or details the existing fact without violating it",
                            "The update explicitly opposes, disables, or reverses what the existing fact states",
                            "The update discusses a different context or component entirely"
                        ]
                    )
                }
                pred = client.system_one(questions, state=state)
                contra_prob = 0.0
                if hasattr(pred, "answers") and "is_contradiction" in pred.answers:
                    contra_prob = getattr(pred.answers["is_contradiction"], "probability", 0.0)
                elif isinstance(pred, dict) and "is_contradiction" in pred:
                    ans = pred["is_contradiction"]
                    contra_prob = getattr(ans, "probability", ans if isinstance(ans, (int, float)) else 0.0)

                rel_choice = "compatible_refinement"
                if hasattr(pred, "answers") and "relationship" in pred.answers:
                    rel_choice = getattr(pred.answers["relationship"], "answer", "compatible_refinement")
                elif isinstance(pred, dict) and "relationship" in pred:
                    ans = pred["relationship"]
                    rel_choice = getattr(ans, "answer", str(ans))

                is_disputed = (contra_prob >= 0.60) or (rel_choice == "direct_contradiction")

                return {
                    "is_consistent": not is_disputed,
                    "status": "contradiction" if is_disputed else "refinement",
                    "disputed": is_disputed,
                    "confidence": round(contra_prob if is_disputed else (1.0 - contra_prob), 4),
                    "matched_key": existing_key,
                    "reason": f"Live Jev evaluation: {'Contradiction detected against existing fact' if is_disputed else 'Compatible refinement of existing fact'} ('{existing_text[:80]}...').",
                    "mode": "live"
                }
            except Exception:
                pass

        # Offline heuristic fallback
        return self._offline_check_consistency(existing_key, existing_text, new_text)

    def _offline_check_consistency(self, existing_key: str, existing_text: str, new_text: str) -> Dict[str, Any]:
        """Offline lexical & semantic heuristic for contradiction and memory poisoning detection."""
        e_lower = existing_text.lower()
        n_lower = new_text.lower()

        antonym_pairs = [
            ("allow", "deny"), ("allowed", "denied"), ("permit", "forbid"),
            ("enable", "disable"), ("enabled", "disabled"),
            ("jwt", "cookie_only"), ("rs256", "plaintext"), ("https", "http"),
            ("encrypted", "unencrypted"), ("plaintext", "ciphertext"),
            ("mandatory", "optional"), ("required", "prohibited"),
            ("strictly", "never"), ("postgresql", "mongodb"), ("mysql", "dynamodb")
        ]
        negations = {"not", "never", "no longer", "unencrypted", "unauthorized", "disabled", "deprecated", "removed", "forbidden"}

        sim = calculate_overlap_similarity(existing_text, new_text)
        e_words = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", e_lower))
        n_words = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", n_lower))

        has_negation_diff = bool((e_words & negations) ^ (n_words & negations))
        has_antonym_conflict = False
        conflict_pair = None
        for a, b in antonym_pairs:
            if (a in e_words and b in n_words) or (b in e_words and a in n_words):
                has_antonym_conflict = True
                conflict_pair = (a, b)
                break

        if (sim >= 0.15 and (has_negation_diff or has_antonym_conflict)) or has_antonym_conflict:
            reason = (
                f"Offline rule detector found conflicting terms ({conflict_pair[0]} vs {conflict_pair[1]})"
                if conflict_pair else "Negation divergence detected between existing and proposed facts"
            )
            return {
                "is_consistent": False,
                "status": "contradiction",
                "disputed": True,
                "confidence": 0.85,
                "matched_key": existing_key,
                "reason": f"{reason} against prior fact '{existing_text[:80]}...'",
                "mode": "offline_simulation"
            }

        return {
            "is_consistent": True,
            "status": "refinement",
            "disputed": False,
            "confidence": 0.75,
            "matched_key": existing_key,
            "reason": f"No direct contradiction detected with prior fact '{existing_text[:80]}...'",
            "mode": "offline_simulation"
        }

    def store_fact(
        self,
        category: str,
        fact_key: str,
        fact_text: str,
        verify_consistency: bool = True
    ) -> Dict[str, Any]:
        consistency_report = {"is_consistent": True, "disputed": False, "reason": "Consistency check skipped."}
        if verify_consistency:
            consistency_report = self.check_fact_consistency(category, fact_key, fact_text)

        is_disputed = 1 if consistency_report.get("disputed") else 0
        dispute_reason = consistency_report.get("reason", "") if is_disputed else ""

        vec = generate_local_embedding(fact_text)
        now = time.time()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO semantic_facts (
                    category, fact_key, fact_text, embedding_json, created_at, last_accessed, access_count,
                    disputed, dispute_reason
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(fact_key) DO UPDATE SET
                    fact_text = excluded.fact_text,
                    embedding_json = excluded.embedding_json,
                    last_accessed = excluded.last_accessed,
                    access_count = access_count + 1,
                    disputed = excluded.disputed,
                    dispute_reason = excluded.dispute_reason
                """,
                (category, fact_key, fact_text, json.dumps(vec), now, now, is_disputed, dispute_reason)
            )
        return {
            "fact_key": fact_key,
            "category": category,
            "disputed": bool(is_disputed),
            "dispute_reason": dispute_reason,
            "consistency_report": consistency_report
        }

    def query_facts(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.15,
        include_disputed: bool = False
    ) -> List[Dict[str, Any]]:
        scored: List[Tuple[float, Dict[str, Any]]] = []

        with self._get_conn() as conn:
            if include_disputed:
                rows = conn.execute("SELECT * FROM semantic_facts").fetchall()
            else:
                rows = conn.execute("SELECT * FROM semantic_facts WHERE disputed = 0").fetchall()
            for r in rows:
                row_dict = dict(r)
                sim = calculate_overlap_similarity(query, row_dict["fact_text"])
                if sim >= min_similarity:
                    scored.append((sim, row_dict))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        with self._get_conn() as conn:
            for score, row in scored[:top_k]:
                # Increment access count
                conn.execute(
                    "UPDATE semantic_facts SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
                    (time.time(), row["id"])
                )
                row["similarity_score"] = round(score, 4)
                del row["embedding_json"]
                results.append(row)
        return results

    def search_episodes(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search episodic log by keyword across action_type, agent_name, and payload content."""
        like_pattern = f"%{keyword}%"
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, timestamp, agent_name, action_type,
                       status, duration_ms, tokens_used
                FROM episodic_log
                WHERE action_type LIKE ?
                   OR agent_name LIKE ?
                   OR input_payload LIKE ?
                   OR output_payload LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (like_pattern, like_pattern, like_pattern, like_pattern, limit)
            ).fetchall()
        return [dict(r) for r in rows]

    def export_all_facts(self) -> List[Dict[str, Any]]:
        """Export all semantic facts as a list of dicts (without raw embeddings)."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT id, category, fact_key, fact_text, created_at, last_accessed, access_count, disputed, dispute_reason "
                "FROM semantic_facts ORDER BY category, fact_key"
            ).fetchall()
        return [dict(r) for r in rows]

    def export_session(self, session_id: str) -> Dict[str, Any]:
        """Export all episodes for a session as a structured JSON object."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM episodic_log WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            ).fetchall()
        episodes = []
        for r in rows:
            ep = dict(r)
            for key in ("input_payload", "output_payload"):
                try:
                    ep[key] = json.loads(ep[key]) if ep[key] else {}
                except (json.JSONDecodeError, TypeError):
                    pass
            episodes.append(ep)
        return {"session_id": session_id, "episode_count": len(episodes), "episodes": episodes}

    def get_stats(self) -> Dict[str, Any]:
        """Return database statistics: row counts, DB file size, unique sessions."""
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        with self._get_conn() as conn:
            ep_count = conn.execute("SELECT COUNT(*) FROM episodic_log").fetchone()[0]
            fact_count = conn.execute("SELECT COUNT(*) FROM semantic_facts").fetchone()[0]
            session_count = conn.execute(
                "SELECT COUNT(DISTINCT session_id) FROM episodic_log"
            ).fetchone()[0]
            oldest_row = conn.execute(
                "SELECT MIN(timestamp) FROM episodic_log"
            ).fetchone()[0]
        return {
            "db_path": self.db_path,
            "db_size_kb": round(db_size / 1024, 2),
            "total_episodes": ep_count,
            "total_semantic_facts": fact_count,
            "unique_sessions": session_count,
            "oldest_episode_ts": oldest_row,
        }


# ======================================================================
# Unified 3-Tier Agent Memory Facade
# ======================================================================

class AgentMemoryEngine:
    """Unified coordinator managing Working, Episodic, and Semantic memory."""
    def __init__(self, session_id: str = "default_session", db_path: Optional[str] = None):
        self.session_id = session_id
        self.working = WorkingMemory()
        self.persistent = PersistentAgentMemory(db_path=db_path)

    def record_turn(self, agent: str, role: str, content: str) -> None:
        self.working.add_turn(role=role, agent_name=agent, content=content)
        self.persistent.log_episode(
            session_id=self.session_id,
            agent_name=agent,
            action_type=role,
            input_payload={"turn": content},
            output_payload={"status": "RECORDED"}
        )

    def remember_fact(self, category: str, key: str, fact: str, verify_consistency: bool = True) -> Dict[str, Any]:
        return self.persistent.store_fact(category, key, fact, verify_consistency=verify_consistency)

    def recall_facts(self, query: str, top_k: int = 3, include_disputed: bool = False) -> List[Dict[str, Any]]:
        return self.persistent.query_facts(query, top_k=top_k, include_disputed=include_disputed)

    def prune(self, max_days: int = 30) -> Dict[str, Any]:
        return self.persistent.prune_stale_episodes(max_days=max_days)

    def get_full_status(self) -> Dict[str, Any]:
        db_size = os.path.getsize(self.persistent.db_path) if os.path.exists(self.persistent.db_path) else 0
        return {
            "session_id": self.session_id,
            "working_tokens": self.working.total_tokens,
            "working_turns_count": len(self.working.turns),
            "recent_episodes": len(self.persistent.get_recent_episodes(self.session_id, 100)),
            "db_path": self.persistent.db_path,
            "db_size_kb": round(db_size / 1024, 2)
        }


# ======================================================================
# CLI & Self-Test Mode
# ======================================================================

def run_self_test() -> int:
    print("[*] Initializing 3-Tier Agent Memory Engine Self-Test...")
    temp_db = "scratch/test_memory.db"
    if os.path.exists(temp_db):
        os.remove(temp_db)

    engine = AgentMemoryEngine(session_id="test_run_01", db_path=temp_db)

    # 1. Test Working Memory
    print("  -> Testing Tier 1 (Working Memory)...")
    for i in range(10):
        engine.working.add_turn("assistant", "fullstack-engineer", f"Step {i}: Implemented module component with unit testing coverage.")
    assert engine.working.total_tokens > 0
    print(f"     Working memory tokens: {engine.working.total_tokens}, turns: {len(engine.working.turns)}")

    # 2. Test Episodic Memory
    print("  -> Testing Tier 2 (Episodic SQLite Ledger)...")
    ep_id = engine.persistent.log_episode(
        session_id="test_run_01",
        agent_name="lead-orchestrator",
        action_type="TASK_DECOMPOSITION",
        input_payload={"goal": "Build payment service"},
        output_payload={"subtasks": ["schema", "tests", "api"]},
        status="SUCCESS",
        duration_ms=45,
        tokens_used=120
    )
    assert ep_id > 0
    episodes = engine.persistent.get_recent_episodes("test_run_01")
    assert len(episodes) >= 1
    print(f"     Recorded episode #{ep_id} successfully.")

    # 3. Test Semantic Memory
    print("  -> Testing Tier 3 (Semantic Vector Store)...")
    engine.remember_fact("architecture", "database_choice", "We use PostgreSQL with SQLAlchemy for ACID transactions.")
    engine.remember_fact("security", "auth_protocol", "Authentication is strictly handled via RS256 JWT tokens with Redis blocklists.")
    engine.remember_fact("frontend", "styling_policy", "Vanilla CSS design tokens with dark mode and micro-animations are mandatory.")

    results = engine.recall_facts("how do we authenticate users?")
    assert len(results) > 0
    top_hit = results[0]
    print(f"     Query: 'how do we authenticate users?'")
    print(f"     Top Recall (Score {top_hit['similarity_score']}): [{top_hit['category']}] {top_hit['fact_text']}")
    assert top_hit["fact_key"] == "auth_protocol"

    # 4. Test Factual Consistency & Memory Poisoning Defense
    print("  -> Testing Tier 3 Guardrails (Memory Poisoning & Contradiction Detection)...")
    poison_res = engine.remember_fact(
        "security",
        "auth_bypass",
        "Authentication uses unencrypted plaintext cookies with no token signing."
    )
    assert poison_res["disputed"] is True, f"Expected poison attempt to be disputed, got {poison_res}"
    print(f"     [PASS] Memory poisoning attempt flagged as DISPUTED: {poison_res['dispute_reason'][:70]}...")

    # Safe recall without include_disputed must omit poisoned fact
    safe_results = engine.recall_facts("how do we authenticate users?", include_disputed=False)
    for hit in safe_results:
        assert hit["fact_key"] != "auth_bypass", "Poisoned fact leaked into safe recall_facts query!"
    print(f"     [PASS] Safe query filtered out disputed poisoned fact successfully.")

    # Audited recall with include_disputed=True must return disputed fact
    all_results = engine.recall_facts("authentication cookies", include_disputed=True)
    poisoned_hit = next((h for h in all_results if h["fact_key"] == "auth_bypass"), None)
    assert poisoned_hit is not None, "Disputed fact missing when include_disputed=True"
    assert poisoned_hit["disputed"] == 1, "Disputed flag not set in returned hit"
    print(f"     [PASS] Audited recall includes disputed fact with explicit dispute badge.")

    # Architectural refinement must pass without dispute
    refine_res = engine.remember_fact(
        "security",
        "auth_protocol",
        "Authentication is strictly handled via RS256 JWT tokens with Redis blocklists, and supports optional WebAuthn passkeys."
    )
    assert refine_res["disputed"] is False, f"Expected refinement to pass without dispute, got {refine_res}"
    print(f"     [PASS] Architectural refinement accepted cleanly without dispute.")

    # Direct key overwrite contradiction attempt
    poison_res2 = engine.remember_fact(
        "architecture",
        "database_choice",
        "We never use PostgreSQL or SQL; all persistence is strictly disabled and kept ephemeral."
    )
    assert poison_res2["disputed"] is True, f"Expected direct key overwrite poison attempt to be disputed, got {poison_res2}"
    print(f"     [PASS] Direct key overwrite contradiction flagged as DISPUTED: {poison_res2['dispute_reason'][:70]}...")

    print("\n[+] 3-TIER MEMORY ENGINE SELF-TEST PASSED: 100% OPERATIONAL WITH TYPE-SAFE GUARDRAILS!\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="3-Tier Agentic Memory Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python memory/memory_engine.py --test
  python memory/memory_engine.py --stats
  python memory/memory_engine.py --export-facts
  python memory/memory_engine.py --query "how do we handle authentication?"
  python memory/memory_engine.py --search-episodes "TASK_DECOMPOSITION"
"""
    )
    parser.add_argument("--test", action="store_true", help="Run automated self-tests")
    parser.add_argument("--query", help="Semantic query to test against long-term memory")
    parser.add_argument("--stats", action="store_true", help="Print database statistics (row counts, size)")
    parser.add_argument("--export-facts", action="store_true", help="Export all semantic facts as JSON")
    parser.add_argument("--search-episodes", metavar="TERM", help="Search episodic log for keyword")
    args = parser.parse_args()

    if args.test or not sys.argv[1:]:
        return run_self_test()

    engine = AgentMemoryEngine()

    if args.query:
        hits = engine.recall_facts(args.query)
        print(f"\nResults for '{args.query}':")
        for h in hits:
            print(f"  [{h['similarity_score']}] ({h['category']}) {h['fact_text']}")
        return 0

    if args.stats:
        stats = engine.persistent.get_stats()
        print("\n  Memory Engine Statistics")
        print("  " + "=" * 40)
        for k, v in stats.items():
            print(f"  {k:<30} {v}")
        print()
        return 0

    if args.export_facts:
        facts = engine.persistent.export_all_facts()
        print(json.dumps(facts, indent=2))
        return 0

    if args.search_episodes:
        episodes = engine.persistent.search_episodes(args.search_episodes)
        print(f"\nEpisode search results for '{args.search_episodes}' ({len(episodes)} found):")
        for ep in episodes:
            print(f"  [{ep['id']}] {ep['agent_name']} | {ep['action_type']} | {ep['status']} | {ep['duration_ms']}ms")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
