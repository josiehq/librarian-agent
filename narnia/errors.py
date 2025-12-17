class NarniaError(Exception):
    """Base error for Narnia operations."""


class ConfigError(NarniaError):
    """Configuration issues (missing/invalid settings)."""


class AuthError(NarniaError):
    """Authentication/permission failures."""
