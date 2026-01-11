"""
Entry point for running the GitHub Cloner service as a module.
Usage: python -m github_cloner --url "https://github.com/user/repo"
"""

from .service import main

if __name__ == '__main__':
    exit(main())
