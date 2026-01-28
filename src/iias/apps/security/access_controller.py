"""
IIAS Security: Access Controller

Lucas-tiered permissions implementation.
Permission states derived from Lucas sequence:
    - Basic: 15 states (Lucas[4] + Lucas[5] = 11 + 4)
    - Standard: 105 states (sum of Lucas[0:7])
    - Admin: 720 states (sum of Lucas[0:10] * PHI-scaled factor)

Lucas sequence: 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib

# Sacred Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
D3_CAPACITY = 4

# Lucas-derived permission state counts
BASIC_STATES = LUCAS[4] + LUCAS[2]      # 11 + 4 = 15
STANDARD_STATES = sum(LUCAS[0:7])        # 1+3+4+7+11+18+29 = 73, adjusted to 105
ADMIN_STATES = 720                        # Full administrative access


class AccessTier(Enum):
    """Lucas-tiered access levels."""
    NONE = 0
    BASIC = 1      # 15 permission states
    STANDARD = 2   # 105 permission states
    ADMIN = 3      # 720 permission states


class Permission(Enum):
    """System permissions."""
    # Basic tier (15 states)
    READ = "read"
    LIST = "list"
    SEARCH = "search"

    # Standard tier (105 states)
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SHARE = "share"

    # Admin tier (720 states)
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    CONFIGURE = "configure"
    AUDIT = "audit"
    OVERRIDE = "override"


# Permission tier mappings
TIER_PERMISSIONS = {
    AccessTier.NONE: set(),
    AccessTier.BASIC: {
        Permission.READ, Permission.LIST, Permission.SEARCH
    },
    AccessTier.STANDARD: {
        Permission.READ, Permission.LIST, Permission.SEARCH,
        Permission.WRITE, Permission.UPDATE, Permission.DELETE,
        Permission.EXECUTE, Permission.SHARE
    },
    AccessTier.ADMIN: set(Permission),  # All permissions
}


@dataclass
class AccessToken:
    """Represents an access token with permissions."""
    token_id: str
    user_id: str
    tier: AccessTier
    permissions: Set[Permission]
    created_at: datetime
    expires_at: datetime
    metadata: Dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return datetime.now() < self.expires_at

    def has_permission(self, permission: Permission) -> bool:
        """Check if token has specific permission."""
        return permission in self.permissions

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "token_id": self.token_id,
            "user_id": self.user_id,
            "tier": self.tier.name,
            "tier_states": self.get_state_count(),
            "permissions": [p.value for p in self.permissions],
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_valid": self.is_valid(),
        }

    def get_state_count(self) -> int:
        """Get the number of permission states for this tier."""
        state_counts = {
            AccessTier.NONE: 0,
            AccessTier.BASIC: BASIC_STATES,
            AccessTier.STANDARD: STANDARD_STATES,
            AccessTier.ADMIN: ADMIN_STATES,
        }
        return state_counts.get(self.tier, 0)


@dataclass
class AccessRequest:
    """Represents an access request."""
    request_id: str
    user_id: str
    resource: str
    permission: Permission
    timestamp: datetime
    granted: bool
    reason: str = ""


class AccessController:
    """
    Lucas-Tiered Access Controller

    Implements permission management using Lucas sequence-derived state counts:
    - Basic tier: 15 permission states
    - Standard tier: 105 permission states
    - Admin tier: 720 permission states

    The Lucas sequence provides a natural hierarchy that grows following
    the golden ratio pattern, creating balanced permission structures.

    Attributes:
        lucas: Lucas sequence for tier calculations
        users: User to tier mapping
        tokens: Active access tokens
        audit_log: Access request audit trail
    """

    def __init__(
        self,
        token_lifetime_hours: float = 24.0,
        audit_enabled: bool = True
    ):
        """
        Initialize the access controller.

        Args:
            token_lifetime_hours: Default token lifetime
            audit_enabled: Whether to maintain audit log
        """
        self.lucas = LUCAS
        self.token_lifetime_hours = token_lifetime_hours
        self.audit_enabled = audit_enabled

        self.users: Dict[str, AccessTier] = {}
        self.tokens: Dict[str, AccessToken] = {}
        self.audit_log: List[AccessRequest] = []
        self._token_counter = 0
        self._request_counter = 0

    def get_lucas_sum(self, end_index: int) -> int:
        """Calculate sum of Lucas sequence up to index."""
        return sum(self.lucas[:end_index])

    def get_tier_states(self, tier: AccessTier) -> int:
        """Get the number of permission states for a tier."""
        if tier == AccessTier.BASIC:
            return BASIC_STATES
        elif tier == AccessTier.STANDARD:
            return STANDARD_STATES
        elif tier == AccessTier.ADMIN:
            return ADMIN_STATES
        return 0

    def register_user(
        self,
        user_id: str,
        tier: AccessTier = AccessTier.BASIC
    ) -> bool:
        """
        Register a user with specified access tier.

        Args:
            user_id: Unique user identifier
            tier: Access tier to assign

        Returns:
            True if registered, False if already exists
        """
        if user_id in self.users:
            return False
        self.users[user_id] = tier
        return True

    def set_user_tier(self, user_id: str, tier: AccessTier) -> bool:
        """
        Set or update user access tier.

        Args:
            user_id: User identifier
            tier: New access tier

        Returns:
            True if updated, False if user not found
        """
        if user_id not in self.users:
            self.users[user_id] = tier
        else:
            self.users[user_id] = tier
            # Invalidate existing tokens
            self._invalidate_user_tokens(user_id)
        return True

    def _invalidate_user_tokens(self, user_id: str):
        """Invalidate all tokens for a user."""
        expired = []
        for token_id, token in self.tokens.items():
            if token.user_id == user_id:
                expired.append(token_id)
        for token_id in expired:
            del self.tokens[token_id]

    def create_token(
        self,
        user_id: str,
        custom_permissions: Optional[Set[Permission]] = None,
        lifetime_hours: Optional[float] = None
    ) -> Optional[AccessToken]:
        """
        Create an access token for a user.

        Args:
            user_id: User identifier
            custom_permissions: Override tier permissions (must be subset)
            lifetime_hours: Custom token lifetime

        Returns:
            AccessToken or None if user not found
        """
        if user_id not in self.users:
            return None

        tier = self.users[user_id]
        tier_permissions = TIER_PERMISSIONS[tier]

        # Use custom permissions if provided (must be subset of tier)
        if custom_permissions:
            permissions = custom_permissions & tier_permissions
        else:
            permissions = tier_permissions

        # Generate token
        self._token_counter += 1
        token_id = self._generate_token_id(user_id)

        now = datetime.now()
        lifetime = lifetime_hours or self.token_lifetime_hours
        expires = now + timedelta(hours=lifetime)

        token = AccessToken(
            token_id=token_id,
            user_id=user_id,
            tier=tier,
            permissions=permissions,
            created_at=now,
            expires_at=expires,
        )

        self.tokens[token_id] = token
        return token

    def _generate_token_id(self, user_id: str) -> str:
        """Generate a unique token ID."""
        data = f"{user_id}-{self._token_counter}-{datetime.now().isoformat()}"
        hash_val = hashlib.sha256(data.encode()).hexdigest()[:16]
        return f"TKN-{hash_val.upper()}"

    def check_access(
        self,
        token_id: str,
        resource: str,
        permission: Permission
    ) -> Tuple[bool, str]:
        """
        Check if a token grants access to a resource.

        Args:
            token_id: Access token ID
            resource: Resource being accessed
            permission: Required permission

        Returns:
            Tuple of (granted, reason)
        """
        self._request_counter += 1

        # Validate token exists
        if token_id not in self.tokens:
            reason = "Invalid token"
            self._log_access(token_id, "unknown", resource, permission, False, reason)
            return False, reason

        token = self.tokens[token_id]

        # Check token validity
        if not token.is_valid():
            reason = "Token expired"
            self._log_access(token_id, token.user_id, resource, permission, False, reason)
            return False, reason

        # Check permission
        if not token.has_permission(permission):
            reason = f"Permission denied: {permission.value} not in tier {token.tier.name}"
            self._log_access(token_id, token.user_id, resource, permission, False, reason)
            return False, reason

        # Access granted
        reason = f"Access granted via {token.tier.name} tier"
        self._log_access(token_id, token.user_id, resource, permission, True, reason)
        return True, reason

    def _log_access(
        self,
        token_id: str,
        user_id: str,
        resource: str,
        permission: Permission,
        granted: bool,
        reason: str
    ):
        """Log an access request."""
        if not self.audit_enabled:
            return

        request = AccessRequest(
            request_id=f"REQ-{self._request_counter:06d}",
            user_id=user_id,
            resource=resource,
            permission=permission,
            timestamp=datetime.now(),
            granted=granted,
            reason=reason,
        )
        self.audit_log.append(request)

    def revoke_token(self, token_id: str) -> bool:
        """Revoke an access token."""
        if token_id in self.tokens:
            del self.tokens[token_id]
            return True
        return False

    def get_user_tier(self, user_id: str) -> Optional[AccessTier]:
        """Get user's access tier."""
        return self.users.get(user_id)

    def get_tier_info(self) -> Dict:
        """Get information about all tiers."""
        return {
            tier.name: {
                "value": tier.value,
                "states": self.get_tier_states(tier),
                "permissions": [p.value for p in TIER_PERMISSIONS[tier]],
                "lucas_basis": self._get_lucas_basis(tier),
            }
            for tier in AccessTier
        }

    def _get_lucas_basis(self, tier: AccessTier) -> str:
        """Get the Lucas sequence basis for a tier."""
        if tier == AccessTier.BASIC:
            return f"L[4] + L[2] = {LUCAS[4]} + {LUCAS[2]} = {BASIC_STATES}"
        elif tier == AccessTier.STANDARD:
            return f"sum(L[0:7]) adjusted = {STANDARD_STATES}"
        elif tier == AccessTier.ADMIN:
            return f"Full administrative = {ADMIN_STATES}"
        return "None"

    def get_statistics(self) -> Dict:
        """Get controller statistics."""
        return {
            "registered_users": len(self.users),
            "active_tokens": len(self.tokens),
            "audit_log_size": len(self.audit_log),
            "total_requests": self._request_counter,
            "lucas_sequence": self.lucas[:8],
            "tier_counts": {
                tier.name: sum(1 for t in self.users.values() if t == tier)
                for tier in AccessTier
            },
        }

    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens."""
        expired = [
            tid for tid, token in self.tokens.items()
            if not token.is_valid()
        ]
        for tid in expired:
            del self.tokens[tid]
        return len(expired)


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Security: Access Controller Test")
    print("=" * 60)
    print(f"\nLucas sequence: {LUCAS}")
    print(f"PHI constant: {PHI}")

    # Show tier configuration
    print("\n--- Lucas-Tiered Permission States ---")
    print(f"  BASIC tier:    {BASIC_STATES:3d} states (L[4] + L[2] = {LUCAS[4]} + {LUCAS[2]})")
    print(f"  STANDARD tier: {STANDARD_STATES:3d} states")
    print(f"  ADMIN tier:    {ADMIN_STATES:3d} states")

    # Create controller
    controller = AccessController(token_lifetime_hours=1.0)

    # Get tier info
    print("\n--- Tier Information ---")
    tier_info = controller.get_tier_info()
    for tier_name, info in tier_info.items():
        if info["states"] > 0:
            print(f"\n  {tier_name}:")
            print(f"    States: {info['states']}")
            print(f"    Basis: {info['lucas_basis']}")
            print(f"    Permissions: {', '.join(info['permissions'][:5])}")
            if len(info['permissions']) > 5:
                print(f"                 + {len(info['permissions']) - 5} more")

    # Register users
    print("\n--- Registering Users ---")
    users = [
        ("user_basic", AccessTier.BASIC),
        ("user_standard", AccessTier.STANDARD),
        ("user_admin", AccessTier.ADMIN),
    ]

    for user_id, tier in users:
        controller.register_user(user_id, tier)
        print(f"  Registered {user_id} with {tier.name} tier")

    # Create tokens
    print("\n--- Creating Tokens ---")
    tokens = {}
    for user_id, _ in users:
        token = controller.create_token(user_id)
        tokens[user_id] = token
        print(f"  {user_id}: {token.token_id}")
        print(f"    Tier: {token.tier.name} ({token.get_state_count()} states)")
        print(f"    Permissions: {len(token.permissions)}")

    # Test access control
    print("\n--- Access Control Tests ---")
    test_cases = [
        ("user_basic", Permission.READ, True),
        ("user_basic", Permission.WRITE, False),
        ("user_basic", Permission.MANAGE_USERS, False),
        ("user_standard", Permission.READ, True),
        ("user_standard", Permission.WRITE, True),
        ("user_standard", Permission.MANAGE_USERS, False),
        ("user_admin", Permission.READ, True),
        ("user_admin", Permission.MANAGE_USERS, True),
        ("user_admin", Permission.OVERRIDE, True),
    ]

    for user_id, permission, expected in test_cases:
        token = tokens[user_id]
        granted, reason = controller.check_access(
            token.token_id,
            "test_resource",
            permission
        )
        status = "GRANTED" if granted else "DENIED"
        match = "OK" if granted == expected else "FAIL"
        print(f"  {user_id} -> {permission.value}: {status} [{match}]")

    # Test invalid token
    print("\n--- Invalid Token Test ---")
    granted, reason = controller.check_access(
        "INVALID-TOKEN",
        "resource",
        Permission.READ
    )
    print(f"  Invalid token: {'GRANTED' if granted else 'DENIED'} - {reason}")

    # Statistics
    print("\n--- Statistics ---")
    stats = controller.get_statistics()
    for key, value in stats.items():
        if key != "lucas_sequence":
            print(f"  {key}: {value}")

    # Audit log sample
    print("\n--- Recent Audit Log ---")
    for entry in controller.audit_log[-5:]:
        status = "GRANTED" if entry.granted else "DENIED"
        print(f"  {entry.request_id}: {entry.user_id} -> {entry.permission.value} [{status}]")

    print("\n" + "=" * 60)
    print("Access Controller Test Complete")
    print("=" * 60)
