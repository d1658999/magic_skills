# Security Threat Modeling & Vulnerability Reference

This reference provides a taxonomy of high-impact security vulnerabilities, anti-patterns, and secure remediation blueprints for code reviews. Reviewers should use this guide to identify subtle security flaws during Phase 4 of the review lifecycle.

---

## 1. Injection Vulnerabilities (CWE-89, CWE-78, CWE-94)

### 1.1 SQL / NoSQL Injection
- **Defect Mechanism**: Unsanitized user inputs concatenated or formatted directly into raw queries.
- **Red Flag Snippets**:
  ```python
  # BAD: Raw string interpolation in SQL
  cursor.execute(f"SELECT * FROM users WHERE email = '{user_input}'")
  cursor.execute("SELECT * FROM products WHERE id = " + product_id)
  ```
  ```typescript
  // BAD: Unsanitized MongoDB query object injection
  db.collection('users').find({ username: req.body.username, password: req.body.password });
  // If req.body.password is { "$ne": null }, authentication is bypassed!
  ```
- **Remediation**: Always use parameterized queries, prepared statements, or ORM parameter bindings.
  ```python
  # GOOD: Parameterized query
  cursor.execute("SELECT * FROM users WHERE email = %s", (user_input,))
  ```
  ```typescript
  // GOOD: Enforce type checking / sanitize query payload
  if (typeof req.body.password !== 'string') throw new BadRequestError('Invalid password');
  ```

### 1.2 Command Injection
- **Defect Mechanism**: Passing untrusted strings into system shells (`subprocess.Popen(..., shell=True)`, `os.system`, `child_process.exec`).
- **Red Flag Snippets**:
  ```python
  # BAD: Shell execution with unescaped argument
  subprocess.run(f"ping -c 1 {host}", shell=True)
  ```
- **Remediation**: Avoid `shell=True`. Pass arguments as explicit arrays; use allow-lists for inputs.
  ```python
  # GOOD: Executed directly without shell interpolation
  subprocess.run(["ping", "-c", "1", host], shell=False, check=True)
  ```

---

## 2. Broken Authorization & Access Control (CWE-639, CWE-285)

### 2.1 Insecure Direct Object References (IDOR / BOLA)
- **Defect Mechanism**: Accepting an entity identifier (e.g. `order_id`, `user_id`) from client requests and fetching/updating the entity without verifying the caller owns or has permissions to access it.
- **Red Flag Snippets**:
  ```typescript
  // BAD: Fetching order without ownership check
  app.get('/api/orders/:id', async (req, res) => {
    const order = await Order.findById(req.params.id);
    return res.json(order);
  });
  ```
- **Remediation**: Scope all database lookups to the authenticated user's tenant or organization ID:
  ```typescript
  // GOOD: Scoped to authenticated user session
  app.get('/api/orders/:id', async (req, res) => {
    const order = await Order.findOne({ _id: req.params.id, userId: req.user.id });
    if (!order) return res.status(404).json({ error: 'Order not found' });
    return res.json(order);
  });
  ```

### 2.2 Missing Function Level Access Control
- **Defect Mechanism**: Internal, administrative, or privileged endpoints missing role/permission middleware.
- **Review Check**: Does every state-mutating route explicitly enforce authentication and authorization guards?

---

## 3. Server-Side Request Forgery (SSRF) (CWE-918)

- **Defect Mechanism**: Backend fetches a URL provided by user input (e.g. webhooks, avatar import, PDF renderers) without restricting target IP addresses.
- **Failure Scenario**: Attacker supplies `http://169.254.169.254/latest/meta-data/` to harvest cloud instance credentials or probes internal microservices (`http://10.0.0.5:8080/admin`).
- **Red Flag Snippet**:
  ```python
  # BAD: Fetching arbitrary user-supplied URL
  response = requests.get(request.json['webhook_url'])
  ```
- **Remediation**:
  1. Validate URL scheme (allow only `https:`).
  2. Resolve DNS hostname to IP **before** fetching.
  3. Validate that the resolved IP does not belong to private/reserved CIDRs (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`).
  4. Disable automatic redirect following, or re-validate redirect destination IPs.

---

## 4. Cryptographic Flaws & Timing Attacks (CWE-208, CWE-330)

### 4.1 Non-Constant-Time Secret Comparison
- **Defect Mechanism**: Using standard string comparison operators (`==` or `===`) to compare HMAC signatures, API tokens, or password hashes.
- **Failure Scenario**: Early return on mismatch allows timing side-channel attacks to deduce the token byte by byte.
- **Remediation**:
  ```python
  # BAD:
  if user_hmac == expected_hmac: ...
  # GOOD: Constant-time comparison
  import hmac
  if hmac.compare_digest(user_hmac, expected_hmac): ...
  ```
  ```typescript
  // GOOD in Node.js:
  import crypto from 'crypto';
  crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
  ```

### 4.2 Weak Pseudo-Random Number Generators (PRNG)
- **Defect Mechanism**: Using `Math.random()` or Python's `random` module for security tokens, reset links, session IDs, or salts.
- **Remediation**: Always use cryptographically secure PRNG: `crypto.randomBytes()` (Node.js), `secrets.token_hex()` (Python), or `crypto/rand` (Go).

---

## 5. Insecure Deserialization & Prototype Pollution (CWE-502, CWE-1321)

### 5.1 Deserialization of Untrusted Data
- **Red Flags**:
  - Python: `pickle.loads()`, `yaml.load()` without `yaml.SafeLoader`.
  - Java: `ObjectInputStream.readObject()` without lookahead validation.
  - C#: `BinaryFormatter.Deserialize()`.
- **Remediation**: Prefer safe data interchange formats (JSON, Protocol Buffers, MessagePack) and schema validators (Pydantic, Zod).

### 5.2 JavaScript / TypeScript Prototype Pollution
- **Defect Mechanism**: Recursive object merges, `lodash.merge`, or deep cloning user payloads with keys like `__proto__`, `constructor`, `prototype`.
- **Remediation**: Use object map without prototype (`Object.create(null)`), freeze prototypes, or sanitize dangerous keys.

---

## 6. Sensitive Data Exposure & Logging (CWE-532, CWE-312)

- **Red Flags**:
  - Printing full request headers (containing `Authorization: Bearer ...` or `Cookie`).
  - Logging entire exception objects containing DB connection strings, passwords, or PII.
  - Returning internal stack traces or database error messages in production API responses.
- **Review Standard**:
  - Redact or mask passwords, credit cards (PAN), social security numbers, and API tokens.
  - API responses in production must return generic error messages with an opaque correlation/trace ID:
    ```json
    { "error": "Internal server error", "trace_id": "c4b92a10-..." }
    ```

---

## 7. Path Traversal & Arbitrary File Overwrite (CWE-22)

- **Defect Mechanism**: Constructing file system paths by directly concatenating user-supplied filenames.
- **Failure Scenario**: Filename `../../../../etc/passwd` escapes the designated upload directory.
- **Remediation**:
  ```python
  # BAD:
  file_path = os.path.join(UPLOAD_DIR, user_filename)
  
  # GOOD:
  safe_filename = os.path.basename(user_filename)
  target_path = Path(UPLOAD_DIR).resolve() / safe_filename
  if not target_path.resolve().is_relative_to(Path(UPLOAD_DIR).resolve()):
      raise SecurityException("Path traversal attempt detected")
  ```

---

## Security Audit Review Checklist

- [ ] All inputs validated against strict schema / whitelist?
- [ ] Database queries parameterized or safely handled by ORM?
- [ ] No `shell=True` or direct command execution with untrusted strings?
- [ ] Object-level authorization checked on all resource fetches/updates?
- [ ] Webhook and external URL fetching protected against SSRF & local subnet access?
- [ ] Cryptographic operations use constant-time comparison and CSPRNG?
- [ ] Zero secrets, tokens, or PII printed to application logs?
- [ ] File operations safe from directory traversal (`..`) attacks?
- [ ] Safe deserializers used exclusively (no `pickle`, no unsafe YAML loaders)?
