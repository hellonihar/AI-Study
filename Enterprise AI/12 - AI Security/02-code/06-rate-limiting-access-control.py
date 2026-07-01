"""
Rate limiting and access control: token bucket, user quotas, and IP-based throttling.

Run: python 06-rate-limiting-access-control.py

Requirements: numpy
"""

import time
import hashlib
import random

print("=== Rate Limiting & Access Control ===\n")

class TokenBucket:
    def __init__(self, capacity, refill_rate, refill_interval=1.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def consume(self, tokens=1):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, self.tokens
        return False, self.tokens

class RateLimiter:
    def __init__(self):
        self.buckets = {}

    def _get_bucket(self, key, capacity, refill_rate):
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(capacity, refill_rate)
        return self.buckets[key]

    def check_ip(self, ip, cost=1):
        bucket = self._get_bucket(f"ip:{ip}", 60, 1.0)
        return bucket.consume(cost)

    def check_user(self, user_id, cost=1):
        bucket = self._get_bucket(f"user:{user_id}", 100, 2.0)
        return bucket.consume(cost)

    def check_global(self, cost=1):
        bucket = self._get_bucket("global", 1000, 20.0)
        return bucket.consume(cost)

class AccessController:
    def __init__(self):
        self.api_keys = {}
        self.roles = {
            "admin": {"rate_multiplier": 5.0, "can_access_admin": True},
            "user": {"rate_multiplier": 1.0, "can_access_admin": False},
            "free": {"rate_multiplier": 0.3, "can_access_admin": False},
        }

    def register_key(self, owner, role="user"):
        key = f"ak-{hashlib.sha256(f'{owner}{time.time()}'.encode()).hexdigest()[:16]}"
        self.api_keys[key] = {"owner": owner, "role": role}
        return key

    def validate_key(self, api_key):
        if api_key in self.api_keys:
            return self.api_keys[api_key]
        return None

    def check_access(self, api_key, resource):
        info = self.validate_key(api_key)
        if not info:
            return False, "invalid_key"
        role_config = self.roles.get(info["role"], self.roles["free"])
        if resource == "admin" and not role_config["can_access_admin"]:
            return False, "insufficient_permissions"
        return True, role_config

def simulate_requests():
    limiter = RateLimiter()
    controller = AccessController()

    user_key = controller.register_key("alice", "user")
    admin_key = controller.register_key("bob", "admin")
    free_key = controller.register_key("charlie", "free")

    print(f"Registered API keys:")
    print(f"  alice (user):  {user_key}")
    print(f"  bob (admin):   {admin_key}")
    print(f"  charlie (free): {free_key}")

    print(f"\n{'Request':>8} {'IP':>16} {'User':>10} {'API Key':>20} {'Result':>12} {'Tokens Left':>12}")
    print("-" * 82)

    scenarios = [
        ("alice", "192.168.1.1", user_key, "chat"),
        ("bob", "10.0.0.1", admin_key, "admin"),
        ("charlie", "203.0.113.5", free_key, "chat"),
        ("alice", "192.168.1.1", user_key, "chat"),
        ("alice", "192.168.1.1", user_key, "chat"),
        ("alice", "192.168.1.1", user_key, "chat"),
        ("unknown", "10.0.0.99", "invalid-key-123", "chat"),
        ("charlie", "203.0.113.5", free_key, "admin"),
        ("bob", "10.0.0.1", admin_key, "admin"),
    ]

    for user, ip, key, resource in scenarios:
        access_ok, access_info = controller.check_access(key, resource)
        if not access_ok:
            reason = access_info if isinstance(access_info, str) else "denied"
            print(f"{'REQ':>8} {ip:>16} {user:>10} {key[:16]+'...':>20} {'ACCESS_DENIED':>12} {'-':>12}")
            continue

        role = access_info
        base_capacity = 60 * role["rate_multiplier"]
        ip_allowed, ip_tokens = limiter.check_ip(ip)
        user_allowed, user_tokens = limiter.check_user(user)
        global_allowed, global_tokens = limiter.check_global()

        if ip_allowed and user_allowed and global_allowed:
            print(f"{'REQ':>8} {ip:>16} {user:>10} {key[:16]+'...':>20} {'ALLOWED':>12} {f'{user_tokens:.0f}':>12}")
        else:
            print(f"{'REQ':>8} {ip:>16} {user:>10} {key[:16]+'...':>20} {'RATE_LIMITED':>12} {f'{user_tokens:.0f}':>12}")

simulate_requests()
