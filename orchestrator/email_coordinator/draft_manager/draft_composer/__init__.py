"""
Draft Composer Service Package
Creates and saves email drafts in Gmail as replies to original emails.
"""

from .service import DraftComposerService

__version__ = "1.0.0"
__all__ = ["DraftComposerService"]
