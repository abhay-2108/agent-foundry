# Canonical Security & Hardening Standards

This reference establishes security controls across application architectures, including the 3-Tier Security Boundary Isolation pattern, OWASP Top 10 vulnerability prevention, and secret management hygiene.

---

## 1. The 3-Tier Security Boundary Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: UNTRUSTED INGESTION BOUNDARY                                   │
│ - External user input, webhooks, query parameters, file uploads       │
│ - Zero trust: Validate strictly against typed schemas (Zod/Pydantic)   │
│ - Sanitize encoding, strip null bytes, enforce byte length limits      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Strongly Typed & Sanitized DTO)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 2: ISOLATED DOMAIN LOGIC BOUNDARY                                 │
│ - Business rules, computational pipelines, authorization policies     │
│ - Identity context propagated through typed claims (RBAC/ABAC)         │
│ - Strict memory isolation; no raw OS subprocess spawning              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Parameterized Query / Safe API Call)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 3: PRIVILEGED EXECUTION & STORAGE BOUNDARY                       │
│ - Databases, filesystems, cloud APIs, shell / code interpreters        │
│ - Least privilege credentials; row-level security (RLS)               │
│ - Sandboxed execution; strict command whitelist; path traversal guards │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. OWASP Top 10 Prevention Checklist

### 1. Injection (SQL, NoSQL, Command, LDAP)
- [ ] **Parameterized SQL Only**: All SQL queries use bind variables or ORM parameterization. Zero raw string formatting (`f"SELECT * WHERE id = {user_id}"` is forbidden).
- [ ] **No Shell Executions with User Input**: Subprocesses must pass argument lists (`subprocess.run(["ls", path])`), never raw shell strings (`shell=True`).
- [ ] **Command Whitelisting**: Any command-line tool invocation must validate arguments against a strict regex whitelist.

### 2. Broken Authentication & Session Management
- [ ] **Cryptographic Hash Functions**: Passwords hashed with Argon2id or bcrypt (cost $\ge 12$). MD5 and SHA-1 strictly banned.
- [ ] **Session Expiration**: Ephemeral tokens enforce explicit TTLs (access token $\le 15$ min, refresh token $\le 7$ days).
- [ ] **HttpOnly & Secure Cookies**: Session cookies set `HttpOnly`, `Secure`, and `SameSite=Lax` or `Strict`.

### 3. Sensitive Data Exposure & Secret Management
- [ ] **Zero Hardcoded Secrets**: No API keys, JWT secrets, private certificates, or database passwords in source code or git history.
- [ ] **Environment Separation**: Secrets injected at runtime via environment variables or secret managers (Vault, AWS Secrets Manager).
- [ ] **Redaction in Logs**: Credit card numbers, passwords, auth tokens, and PII are redacted before emitting log events.

### 4. Broken Access Control & IDOR
- [ ] **Tenant Isolation**: Every database read/write checks `WHERE tenant_id = :current_tenant_id` or uses database RLS.
- [ ] **Object-Level Authorization**: Never trust client-supplied IDs (e.g., `/api/user/123/documents/456`) without validating that the authenticated session owns that document.

### 5. Cross-Site Scripting (XSS) & CSRF
- [ ] **Context-Aware Escaping**: HTML rendering engines enforce automatic output escaping.
- [ ] **Content Security Policy (CSP)**: HTTP response headers include restrictive CSP (`default-src 'self'`).
- [ ] **Anti-CSRF Tokens**: State-changing endpoints (POST/PUT/DELETE) validate anti-CSRF tokens or verify Origin/SameSite headers.

### 6. SSRF (Server-Side Request Forgery)
- [ ] **URL Scheme Whitelist**: Outbound HTTP requests only allow `http://` and `https://` (no `file://`, `gopher://`, `ldap://`).
- [ ] **Private IP Blocking**: DNS resolution verifies destination IP does not resolve to loopback (`127.0.0.1`), link-local (`169.254.169.254`), or private RFC 1918 subnets (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`).

### 7. Path Traversal & File Uploads
- [ ] **Canonical Path Resolution**: File paths validated using `.resolve()` and confirmed to start with the authorized base directory (`path.startswith(base_dir)`).
- [ ] **Extension & MIME Validation**: Uploaded files validated against both MIME type and binary magic numbers.

---

## 3. Secret Detection Verification

Run prior to committing any code:

```bash
# Verify no staged secrets or credential leaks
git diff --staged | grep -iE "(api_key|secret|password|bearer|aws_secret|private_key)\s*[:=]"
```
