"""
MCP security: authentication, authorization, input validation, and audit logging.

Run: python 08-mcp-security.py

Requirements: none (stdlib only)
"""

import json
import re
import os
import hashlib
from datetime import datetime

print("=== MCP Security ===\n")

class AuditLogger:
    def __init__(self):
        self.log = []

    def log_event(self, event_type, user, tool, params, status, reason=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": user,
            "tool": tool,
            "params_safe": self.sanitize(params),
            "status": status,
            "reason": reason,
        }
        self.log.append(entry)
        return entry

    def sanitize(self, params):
        safe = {}
        sensitive_keys = {"password", "secret", "token", "api_key", "key", "credential"}
        for k, v in params.items():
            if k.lower() in sensitive_keys:
                safe[k] = "***REDACTED***"
            else:
                safe[k] = v
        return safe

    def report(self):
        return self.log

class ScopeChecker:
    def __init__(self):
        self.tool_scopes = {
            "read_file": {"scope": "files:read", "auto_approve": True},
            "write_file": {"scope": "files:write", "auto_approve": False},
            "delete_file": {"scope": "files:delete", "auto_approve": False},
            "search": {"scope": "search:read", "auto_approve": True},
            "send_email": {"scope": "email:send", "auto_approve": False},
            "query_db": {"scope": "db:read", "auto_approve": True},
            "execute_db": {"scope": "db:write", "auto_approve": False},
        }

    def check_access(self, user, tool_name):
        tool_info = self.tool_scopes.get(tool_name)
        if not tool_info:
            return True, "Unknown tool — default allow"

        required_scope = tool_info["scope"]

        user_scopes = USER_SCOPES.get(user, [])

        if required_scope in user_scopes:
            return True, f"User '{user}' has scope '{required_scope}'"

        return False, f"User '{user}' missing scope '{required_scope}'"

    def needs_confirmation(self, tool_name):
        info = self.tool_scopes.get(tool_name)
        if not info:
            return False
        return not info["auto_approve"]

USER_SCOPES = {
    "admin": ["files:read", "files:write", "files:delete", "search:read", "email:send", "db:read", "db:write"],
    "developer": ["files:read", "files:write", "search:read", "db:read"],
    "viewer": ["files:read", "search:read", "db:read"],
}

class InputValidator:
    @staticmethod
    def validate_path(path):
        allowed = ["/home/user/projects", "/tmp/work"]
        abs_path = os.path.abspath(os.path.expanduser(path))
        for allowed_dir in allowed:
            if abs_path.startswith(allowed_dir):
                return True, abs_path
        return False, f"Path not in allowed directories"

    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, email
        return False, "Invalid email format"

    @staticmethod
    def validate_sql_input(text):
        dangerous = ["DROP", "DELETE", "TRUNCATE", "ALTER", "EXEC", "EXECUTE",
                     "INSERT", "UPDATE", "CREATE", "--", "/*", "*/", ";"]
        upper = text.upper()
        for pattern in dangerous:
            if pattern in upper:
                return False, f"SQL injection pattern detected: {pattern}"
        return True, text

audit = AuditLogger()
checker = ScopeChecker()
validator = InputValidator()

print("1. Scope-Based Authorization\n")

users = ["admin", "developer", "viewer"]
actions = [
    ("read_file", {"path": "/home/user/projects/config.json"}),
    ("delete_file", {"path": "/home/user/projects/config.json"}),
    ("send_email", {"to": "alice@corp.com", "subject": "Test", "body": "Hello"}),
    ("query_db", {"query": "SELECT * FROM users"}),
]

for user in users:
    print(f"  User: {user} (scopes: {USER_SCOPES[user]})")
    for tool, params in actions:
        allowed, reason = checker.check_access(user, tool)
        needs_confirm = checker.needs_confirmation(tool)
        status = "ALLOW" if allowed else "DENY"
        confirm = " (+confirm)" if needs_confirm and allowed else ""
        audit.log_event("authorization", user, tool, params,
                       "allowed" if allowed else "denied", reason)
        print(f"    {tool:<20} → {status:<6}{confirm:<15} ({reason})")
    print()

print("2. Input Validation\n")

test_inputs = [
    ("path", "/home/user/projects/config.json"),
    ("path", "/etc/passwd"),
    ("email", "alice@corp.com"),
    ("email", "not-an-email"),
    ("sql", "SELECT * FROM users WHERE id = 1"),
    ("sql", "1; DROP TABLE users; --"),
]

for validation_type, value in test_inputs:
    if validation_type == "path":
        valid, result = validator.validate_path(value)
    elif validation_type == "email":
        valid, result = validator.validate_email(value)
    else:
        valid, result = validator.validate_sql_input(value)

    icon = "✓" if valid else "✗"
    print(f"  {icon} {validation_type:<8} '{value[:40]}' → {result[:50]}")

print(f"\n3. Audit Log Summary\n")
print(f"  {'User':<12} {'Tool':<20} {'Status':<10} {'Reason':<30}")
print(f"  {'-'*70}")
for entry in audit.log[-8:]:
    print(f"  {entry['user']:<12} {entry['tool']:<20} "
          f"{entry['status']:<10} {(entry['reason'] or '')[:30]}")

print(f"\n{'='*60}")
print("Security Architecture")
print(f"{'='*60}")
print("  Authentication: Transport-level (OS) or API keys (SSE)")
print("  Authorization:  Scope-based (tool-level)")
print("  Consent:        Sensitive tools require user confirmation")
print("  Validation:     Path traversal, SQL injection, email format")
print("  Audit:          Full log of all tool invocations")
