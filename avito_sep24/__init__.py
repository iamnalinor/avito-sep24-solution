from .misc import app
from .routes import root_router

__all__ = ["app"]

app.include_router(root_router)
