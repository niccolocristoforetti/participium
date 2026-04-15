def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored hash.

    Inputs:
        password: plaintext password candidate.
        password_hash: stored password hash.

    Returns:
        `True` when the password matches the hash, else `False`.

    Raises:
        No documented domain exception.
    """
    raise NotImplementedError
