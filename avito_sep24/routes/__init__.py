from importlib import import_module
from pathlib import Path

from fastapi import APIRouter

__all__ = ["root_router"]

root_router = APIRouter()
current_dir = Path(__file__).parent.absolute()

for module_path in sorted(current_dir.rglob("*.py")):
    rel_path = module_path.relative_to(current_dir)
    if module_path.stem != "__init__":
        parts = ["", *rel_path.parts[:-1], rel_path.stem]
        module = import_module(".".join(parts), __package__)
        root_router.include_router(module.router)
