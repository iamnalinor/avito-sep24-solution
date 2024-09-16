import os

__all__ = ["POSTGRES_CONN"]

POSTGRES_CONN = os.environ["POSTGRES_CONN"].replace("postgres://", "postgresql://")
