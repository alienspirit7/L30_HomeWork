"""
Input Validators

Provides validation functions for email addresses and URLs.
"""

import re
from typing import Optional


# Email regex pattern (simplified but practical)
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# GitHub URL pattern
GITHUB_URL_PATTERN = re.compile(
    r'^https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(?:\.git)?/?$'
)


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))


def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository URL format.
    
    Accepts URLs like:
    - https://github.com/username/repo
    - https://github.com/username/repo.git
    
    Args:
        url: GitHub URL to validate
        
    Returns:
        True if URL format is valid, False otherwise
        
    Example:
        >>> validate_github_url("https://github.com/user/repo.git")
        True
        >>> validate_github_url("https://gitlab.com/user/repo")
        False
    """
    if not url or not isinstance(url, str):
        return False
    return bool(GITHUB_URL_PATTERN.match(url.strip()))


def extract_repo_name(url: str) -> Optional[str]:
    """
    Extract repository name from GitHub URL.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Repository name or None if invalid URL
        
    Example:
        >>> extract_repo_name("https://github.com/user/my-repo.git")
        'my-repo'
    """
    if not validate_github_url(url):
        return None
    
    # Remove trailing .git and /
    clean_url = url.rstrip('/').removesuffix('.git')
    # Extract last path component
    return clean_url.split('/')[-1]
