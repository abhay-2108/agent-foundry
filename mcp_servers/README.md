# Model Context Protocol (MCP) Tool Servers

A collection of ready-to-run, zero-dependency Python **Model Context Protocol (MCP)** tool servers conforming to the standard JSON-RPC 2.0 specification.

---

## 1. Available Tool Servers

| Server Script | Exposed Tools | Capabilities & Safeguards |
| :--- | :--- | :--- |
| **[`agent_foundry_server.py`](./agent_foundry_server.py)** | `execute_python`, `run_shell`, `read_file_safe`, `write_file_safe`, `list_directory_safe`, `hybrid_search`, `index_documents`, `memory_*`, `workflow_*` | **Unified server** — exposes the full Agent Foundry stack over one MCP endpoint: sandboxed code execution, filesystem operations, hybrid BM25 retrieval, 3-tier memory engine, and workflow DAG runner. Requires the `mcp` package (`pip install mcp`). |
| **[`code_sandbox_server.py`](./code_sandbox_server.py)** | `execute_python`, `run_shell_command` | Lightweight code execution sandbox with AST syntax validation, configurable timeouts (default 10 s), and stdout/stderr capture. Zero extra dependencies. |
| **[`filesystem_server.py`](./filesystem_server.py)** | `read_file`, `write_file`, `diff_preview`, `rollback_file`, `list_directory` | Path-traversal defense, atomic writes with auto `.bak` snapshots, and unified diff previews. Zero extra dependencies. |
| **[`hybrid_retriever_server.py`](./hybrid_retriever_server.py)** | `index_document`, `search` | Local dense + BM25 hybrid ranking over text documents with TF-IDF scoring. Zero extra dependencies. |

---

## 2. Configuration for MCP Clients

Add the following to your MCP client configuration (e.g. `mcp_config.json`, Claude Desktop, Antigravity, or Cursor).

> **Recommended**: Use `agent_foundry_server.py` as the single unified endpoint instead of running the three smaller servers separately.

```json
{
  "mcpServers": {
    "agent-foundry": {
      "command": "python",
      "args": ["/absolute/path/to/Skills and Agents/mcp_servers/agent_foundry_server.py"]
    }
  }
}
```

Or register the individual lightweight zero-dependency servers:

```json
{
  "mcpServers": {
    "code-sandbox": {
      "command": "python",
      "args": ["/absolute/path/to/Skills and Agents/mcp_servers/code_sandbox_server.py"]
    },
    "filesystem-sandbox": {
      "command": "python",
      "args": ["/absolute/path/to/Skills and Agents/mcp_servers/filesystem_server.py"]
    },
    "hybrid-retriever": {
      "command": "python",
      "args": ["/absolute/path/to/Skills and Agents/mcp_servers/hybrid_retriever_server.py"]
    }
  }
}
```

---

## 3. Testing & Verification

Each standalone server includes a self-test mode:

```bash
# Verify Code Sandbox (zero dependencies)
python mcp_servers/code_sandbox_server.py --test

# Verify Filesystem Sandbox (zero dependencies)
python mcp_servers/filesystem_server.py --test

# Verify Hybrid Retriever (zero dependencies)
python mcp_servers/hybrid_retriever_server.py --test

# Inspect Unified Agent Foundry Server tool list (requires mcp package)
python mcp_servers/agent_foundry_server.py --help
```
