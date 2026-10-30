# OWASP Web & API Security Reference Encyclopedia

This reference provides an exhaustive guide to identifying, exploiting (PoC), and securely remediating web application and API security vulnerabilities during security code reviews.

---

## 1. Injection Vulnerabilities (CWE-89, CWE-943, CWE-78, CWE-1336)

### 1.1 SQL Injection (CWE-89)
- **Vulnerability Mechanism**: Untrusted user inputs are directly concatenated or formatted into dynamic SQL query strings, allowing attackers to manipulate query logic, bypass authentication, extract data, or execute administrative commands.
- **Vulnerable Patterns**:
  ```python
  # BAD: Python raw string interpolation
  cursor.execute(f"SELECT id, balance FROM accounts WHERE user_id = '{user_id}' AND status = 'ACTIVE'")
  ```
  ```typescript
  // BAD: Node.js raw query with template literals
  const result = await db.query(`SELECT * FROM products WHERE category = '${req.query.cat}' ORDER BY ${req.query.sort}`);
  ```
- **Exploit Scenario (PoC)**:
  - Input: `user_id = "' UNION SELECT credit_card_num, cvv FROM payment_vault -- "`
  - The database executes the union query, exfiltrating credit card numbers to the attacker.
- **Hardened Drop-In Remediation**:
  ```python
  # GOOD: Parameterized query with explicit placeholder binding
  cursor.execute(
      "SELECT id, balance FROM accounts WHERE user_id = %s AND status = %s",
      (user_id, "ACTIVE")
  )
  ```
  ```typescript
  // GOOD: Safe parameterized binding and strict identifier allowlist
  const ALLOWED_SORT = new Set(['name', 'price', 'created_at']);
  const sortCol = ALLOWED_SORT.has(String(req.query.sort)) ? String(req.query.sort) : 'created_at';
  const result = await db.query(
      `SELECT * FROM products WHERE category = $1 ORDER BY ${sortCol} ASC`,
      [req.query.cat]
  );
  ```

---

### 1.2 NoSQL & Mongo Operator Injection (CWE-943)
- **Vulnerability Mechanism**: Passing untrusted JSON objects directly into MongoDB/Mongoose query functions, allowing attackers to inject query operators like `$ne`, `$gt`, `$where`, or `$regex`.
- **Vulnerable Pattern**:
  ```typescript
  // BAD: Directly accepting req.body into findOne
  app.post('/api/login', async (req, res) => {
    const user = await User.findOne({ username: req.body.username, password: req.body.password });
    if (user) { /* Authenticated! */ }
  });
  ```
- **Exploit Scenario (PoC)**:
  - Attacker sends HTTP payload: `{"username": "admin", "password": {"$ne": null}}`
  - MongoDB evaluates `password != null` (which is true), logging the attacker into the admin account without knowing the password.
- **Hardened Drop-In Remediation**:
  ```typescript
  // GOOD: Strict schema validation enforcing primitive strings
  import { z } from 'zod';

  const LoginSchema = z.object({
    username: z.string().min(1).max(100),
    password: z.string().min(1).max(100)
  });

  app.post('/api/login', async (req, res) => {
    const parsed = LoginSchema.safeParse(req.body);
    if (!parsed.success) return res.status(400).json({ error: "Invalid credentials format" });

    const user = await User.findOne({
      username: parsed.data.username,
      password: parsed.data.password // guaranteed to be a string
    });
  });
  ```

---

### 1.3 Server-Side Template Injection (SSTI) (CWE-1336)
- **Vulnerability Mechanism**: Dynamic template evaluation (Jinja2, Pug, Handlebars, Twig) where untrusted input is embedded directly in the template source string rather than passed as context data.
- **Vulnerable Pattern**:
  ```python
  # BAD: Jinja2 template rendered from interpolated string
  from jinja2 import Environment, FunctionLoader
  env = Environment()
  template = env.from_string(f"Hello, {user_input}!")
  rendered = template.render()
  ```
- **Exploit Scenario (PoC)**:
  - Input: `{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}`
  - Achieves instant Remote Code Execution (RCE) on the server.
- **Hardened Drop-In Remediation**:
  ```python
  # GOOD: Pass user input strictly through template context variables
  template = env.from_string("Hello, {{ user_name }}!")
  rendered = template.render(user_name=user_input)
  ```

---

## 2. Broken Object Level Authorization (BOLA / IDOR) (API1:2023, CWE-639)

- **Vulnerability Mechanism**: An API endpoint receives an object ID in the URL path, query params, or body, and queries the database using only that ID without asserting that the currently authenticated user owns or has tenant rights to that object.
- **Vulnerable Pattern**:
  ```typescript
  // BAD: Order fetched solely by ID from route parameter
  router.get('/api/orders/:id', authenticateToken, async (req, res) => {
    const order = await Order.findById(req.params.id);
    if (!order) return res.status(404).json({ error: "Order not found" });
    return res.json(order);
  });
  ```
- **Exploit Scenario (PoC)**:
  - User A is logged in as User ID `usr_123`.
  - User A requests `/api/orders/ord_999` (belonging to User B).
  - The API returns User B's full invoice, shipping address, and payment metadata.
- **Hardened Drop-In Remediation**:
  ```typescript
  // GOOD: Always enforce tenant and ownership boundary at the database layer
  router.get('/api/orders/:id', authenticateToken, async (req, res) => {
    const order = await Order.findOne({
      _id: req.params.id,
      tenantId: req.user.tenantId, // Multi-tenant guard
      userId: req.user.id          // Direct ownership guard (or role check)
    });
    if (!order) {
      // Return 404 to avoid leaking existence of another tenant's entity
      return res.status(404).json({ error: "Order not found" });
    }
    return res.json(order);
  });
  ```

---

## 3. Server-Side Request Forgery (SSRF) (CWE-918)

- **Vulnerability Mechanism**: Application fetches a remote resource (e.g. image preview, webhook notification, PDF generator) using a URL provided by an untrusted user without validating destination IP addresses.
- **Vulnerable Pattern**:
  ```python
  # BAD: Fetching user-supplied URL directly
  import requests

  @app.route("/api/preview-avatar")
  def preview_avatar():
      url = request.args.get("avatar_url")
      resp = requests.get(url, timeout=5)
      return (resp.content, resp.headers["Content-Type"])
  ```
- **Exploit Scenario (PoC)**:
  - Input: `avatar_url = "http://169.254.169.254/latest/meta-data/iam/security-credentials/"`
  - AWS EC2 Instance Metadata Service (IMDSv1) returns temporary AWS STS credentials, granting the attacker full AWS cloud access.
  - Or targeting internal services: `http://127.0.0.1:6379/` (Redis) or `http://localhost:9200/` (Elasticsearch).
- **Hardened Drop-In Remediation**:
  ```python
  # GOOD: Strict URL scheme, host allowlist, and IP address validation
  import ipaddress
  import socket
  from urllib.parse import urlparse

  FORBIDDEN_NETWORKS = [
      ipaddress.ip_network("127.0.0.0/8"),      # Loopback
      ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private
      ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private
      ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private
      ipaddress.ip_network("169.254.0.0/16"),   # Link-Local (Cloud Metadata)
      ipaddress.ip_network("::1/128"),          # IPv6 Loopback
      ipaddress.ip_network("fc00::/7"),         # IPv6 Private
  ]

  def is_safe_url(target_url: str) -> bool:
      parsed = urlparse(target_url)
      if parsed.scheme not in ("http", "https"):
          return False

      hostname = parsed.hostname
      if not hostname:
          return False

      # Resolve DNS to all associated IPs
      try:
          addr_info = socket.getaddrinfo(hostname, None)
      except socket.gaierror:
          return False

      for item in addr_info:
          ip_str = item[4][0]
          ip_obj = ipaddress.ip_address(ip_str)
          for forbidden in FORBIDDEN_NETWORKS:
              if ip_obj in forbidden:
                  return False # Blocked private / metadata IP
      return True
  ```

---

## 4. Broken Object Property Level Authorization (Mass Assignment) (API3:2023, CWE-915)

- **Vulnerability Mechanism**: Exposing internal object properties to client modification by passing unvetted request payloads directly into database update or creation methods.
- **Vulnerable Pattern**:
  ```typescript
  // BAD: Assigning entire request body to existing user record
  app.patch('/api/users/profile', authenticateToken, async (req, res) => {
    const user = await User.findById(req.user.id);
    Object.assign(user, req.body); // Attacker includes { "role": "admin", "isVerified": true }
    await user.save();
    return res.json(user);
  });
  ```
- **Exploit Scenario (PoC)**:
  - User updates profile with payload: `{"name": "Alice", "role": "superadmin", "billingTier": "enterprise_unlimited"}`
  - Attacker elevates privilege to `superadmin` without paying or administrative authorization.
- **Hardened Drop-In Remediation**:
  ```typescript
  // GOOD: Explicit Data Transfer Object (DTO) validation using allowlist
  import { z } from 'zod';

  const UpdateProfileSchema = z.object({
    name: z.string().min(1).max(100).optional(),
    avatarUrl: z.string().url().optional(),
    bio: z.string().max(500).optional()
  }).strict(); // Disallows unexpected fields

  app.patch('/api/users/profile', authenticateToken, async (req, res) => {
    const result = UpdateProfileSchema.safeParse(req.body);
    if (!result.success) return res.status(400).json({ error: result.error });

    const updatedUser = await User.findByIdAndUpdate(
      req.user.id,
      { $set: result.data },
      { new: true, runValidators: true }
    );
    return res.json(updatedUser);
  });
  ```

---

## 5. Path Traversal & Zip Slip (CWE-22)

- **Vulnerability Mechanism**: Using untrusted filenames from user uploads or query params directly in filesystem operations without canonical path validation.
- **Vulnerable Pattern**:
  ```typescript
  // BAD: Path joined without boundary check
  import path from 'path';
  import fs from 'fs';

  app.get('/api/files/download', (req, res) => {
    const filePath = path.join('/var/app/uploads', req.query.filename);
    res.sendFile(filePath);
  });
  ```
- **Exploit Scenario (PoC)**:
  - Input: `filename = "../../../etc/passwd"` or `"..\\..\\..\\Windows\\System32\\drivers\\etc\\hosts"`
  - Attacker reads arbitrary sensitive operating system files or source code.
- **Hardened Drop-In Remediation**:
  ```typescript
  // GOOD: Resolve canonical path and enforce base directory containment
  import path from 'path';
  import fs from 'fs';

  const BASE_DIR = path.resolve('/var/app/uploads');

  app.get('/api/files/download', (req, res) => {
    const requestedFile = String(req.query.filename || '');
    // Sanitize basename to strip path separators
    const safeName = path.basename(requestedFile);
    const resolvedPath = path.resolve(BASE_DIR, safeName);

    // Verify resolved path resides within BASE_DIR
    if (!resolvedPath.startsWith(BASE_DIR + path.sep)) {
      return res.status(403).json({ error: "Access denied" });
    }

    if (!fs.existsSync(resolvedPath)) {
      return res.status(404).json({ error: "File not found" });
    }

    res.sendFile(resolvedPath);
  });
  ```

---

## 6. Cross-Site Scripting (XSS) (CWE-79)

- **Vulnerability Mechanism**: Untrusted user input rendered in HTML or executed in JavaScript context without appropriate contextual encoding.
- **Context-Specific Encoding Rules**:
  - HTML Body: `&` $\rightarrow$ `&amp;`, `<` $\rightarrow$ `&lt;`, `>` $\rightarrow$ `&gt;`
  - HTML Attribute: `"` $\rightarrow$ `&quot;`, `'` $\rightarrow$ `&#x27;`
  - JavaScript String: Unicode hexadecimal escapes `\u003C`, `\u003E`, `\u0022`
  - React/Vue: Avoid `dangerouslySetInnerHTML` or `v-html` unless sanitized by DOMPurify with strict config.
- **Hardened Drop-In Example**:
  ```typescript
  import DOMPurify from 'dompurify';
  import { JSDOM } from 'jsdom';

  const window = new JSDOM('').window;
  const purify = DOMPurify(window);

  export function sanitizeHtml(untrustedInput: string): string {
    return purify.sanitize(untrustedInput, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'li'],
      ALLOWED_ATTR: ['href', 'target'],
      FORCE_BODY: true
    });
  }
  ```
