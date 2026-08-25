"""Allow ``python -m qspecbench`` (used by release_verify and Makefile preflight)."""

from qspecbench.cli import main

if __name__ == "__main__":
    main()
