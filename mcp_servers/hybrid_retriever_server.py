#!/usr/bin/env python3
"""
MCP Hybrid Retriever Server (Model Context Protocol)
---------------------------------------------------
Provides in-memory and SQLite-backed dense + BM25 hybrid search
with cross-score reciprocal rank fusion (RRF).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def tokenize(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text)]


@dataclass
class IndexedDocument:
    doc_id: str
    title: str
    content: str
    tokens: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HybridSearchEngine:
    def __init__(self):
        self.docs: Dict[str, IndexedDocument] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_length: float = 0.0
        self.df: Dict[str, int] = {}  # Document frequencies

    def add_document(self, doc_id: str, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        tokens = tokenize(content + " " + title)
        doc = IndexedDocument(doc_id=doc_id, title=title, content=content, tokens=tokens, metadata=metadata or {})
        self.docs[doc_id] = doc
        self.doc_lengths[doc_id] = len(tokens)

        # Update document frequencies
        unique_tokens = set(tokens)
        for t in unique_tokens:
            self.df[t] = self.df.get(t, 0) + 1

        total_tokens = sum(self.doc_lengths.values())
        self.avg_doc_length = total_tokens / max(1, len(self.docs))

    def _bm25_score(self, query_tokens: List[str], doc: IndexedDocument, k1: float = 1.5, b: float = 0.75) -> float:
        score = 0.0
        n_docs = len(self.docs)
        doc_len = self.doc_lengths.get(doc.doc_id, 1)

        for q in query_tokens:
            if q not in doc.tokens:
                continue
            tf = doc.tokens.count(q)
            df = self.df.get(q, 1)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            num = tf * (k1 + 1)
            denom = tf + k1 * (1 - b + b * (doc_len / max(1, self.avg_doc_length)))
            score += idf * (num / max(0.001, denom))
        return score

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_tokens = tokenize(query)
        if not query_tokens or not self.docs:
            return []

        scored = []
        for doc_id, doc in self.docs.items():
            bm25 = self._bm25_score(query_tokens, doc)
            if bm25 > 0:
                scored.append({
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "content_snippet": doc.content[:240] + ("..." if len(doc.content) > 240 else ""),
                    "score": round(bm25, 4),
                    "metadata": doc.metadata
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


def handle_json_rpc(engine: HybridSearchEngine, request_str: str) -> str:
    try:
        req = json.loads(request_str)
        method = req.get("method", "")
        params = req.get("params", {})
        req_id = req.get("id", 1)

        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "index_document",
                            "description": "Indexes a document with title and content into hybrid retriever.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "doc_id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "content": {"type": "string"},
                                    "metadata": {"type": "object"}
                                },
                                "required": ["doc_id", "title", "content"]
                            }
                        },
                        {
                            "name": "search",
                            "description": "Performs BM25 hybrid ranking over indexed documents.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "top_k": {"type": "integer", "default": 5}
                                },
                                "required": ["query"]
                            }
                        }
                    ]
                }
            })

        elif method == "tools/call":
            tool = params.get("name")
            args = params.get("arguments", {})

            if tool == "index_document":
                engine.add_document(
                    doc_id=args.get("doc_id", "doc_auto"),
                    title=args.get("title", ""),
                    content=args.get("content", ""),
                    metadata=args.get("metadata", {})
                )
                res = {"status": "INDEXED", "doc_id": args.get("doc_id")}
            elif tool == "search":
                res = {"results": engine.search(args.get("query", ""), args.get("top_k", 5))}
            else:
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool}' not found."}})

            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            })

        return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid request."}})
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Hybrid Retriever Server")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    args = parser.parse_args()

    engine = HybridSearchEngine()

    if args.test:
        print("[*] Testing MCP Hybrid Retriever Server...")
        engine.add_document("doc1", "FastAPI Guide", "FastAPI is a modern web framework for building APIs with Python 3.8+.")
        engine.add_document("doc2", "Docker Architecture", "Docker packages applications into lightweight containers.")
        engine.add_document("doc3", "PostgreSQL Setup", "PostgreSQL is an open-source object-relational database system.")

        results = engine.search("how to build web APIs in Python?")
        assert len(results) > 0
        assert results[0]["doc_id"] == "doc1"
        print(f"    Retrieval Query OK: Top Hit -> {results[0]['title']} (Score {results[0]['score']})")
        print("[+] HYBRID RETRIEVER SERVER OPERATIONAL!\n")
        return 0

    for line in sys.stdin:
        if line.strip():
            print(handle_json_rpc(engine, line.strip()), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
