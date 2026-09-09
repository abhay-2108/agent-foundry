# Model Context Protocol (MCP) Tool Servers

A collection of ready-to-run, zero-dependency Python **Model Context Protocol (MCP)** tool servers conforming to the standard JSON-RPC 2.0 specification.

---

## 1. Available Tool Servers

| Server Script | Exposed Tools | Capabilities & Safeguards |
| :--- | :--- | :--- |
| **[`code_sandbox_server.py`](./code_sandbox_server.py)** | `execute_python`, `run_shell_command` | Subprocess execution with AST syntax validation, configurable timeouts (default 10s), and stdout/stderr capture. |
| **[`filesystem_server.py`](./filesystem_server.py)** | `read_file`, `write_file`, `diff_preview`, `rollback_file`, `list_directory` | Path-traversal defense, atomic writes with auto `.bak` snapshots, and unified diff previews. |
| **[`hybrid_retriever_server.py`](./hybrid_retriever_server.py)** | `index_document`, `search` | Local dense + BM25 hybrid ranking over text documents with TF-IDF scoring. |

---

## 2. Configuration for MCP Clients

Add the following to your MCP client configuration (e.g. `mcp_config.json`, Claude Desktop, Antigravity, or Cursor):

```json
{
  "mcpServers": {
    "code-sandbox": {
      "command": "python",
      "args": ["p:/AIML Projects/Skills and Agents/mcp_servers/code_sandbox_server.py"]
    },
    "filesystem-sandbox": {
      "command": "python",
      "args": ["p:/AIML Projects/Skills and Agents/mcp_servers/filesystem_server.py"]
    },
    "hybrid-retriever": {
      "command": "python",
      "args": ["p:/AIML Projects/Skills and Agents/mcp_servers/hybrid_retriever_server.py"]
    }
  }
}
```

---

## 3. Testing & Verification

Each server includes a standalone self-test mode:

```bash
# Verify Code Sandbox
python mcp_servers/code_sandbox_server.py --test

# Verify Filesystem Sandbox
python mcp_servers/filesystem_server.py --test

# Verify Hybrid Retriever
python mcp_servers/hybrid_retriever_server.py --test
```
