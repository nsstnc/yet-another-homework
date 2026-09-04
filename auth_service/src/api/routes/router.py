from importlib import import_module
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

routes_dir = Path(__file__).parent

for directory in routes_dir.iterdir():
    if not directory.is_dir():
        continue

    if directory.name.startswith("_"):
        continue

    router_file = directory / "router.py"

    if not router_file.exists():
        continue

    module = import_module(
        f"{__package__}.{directory.name}.router"
    )

    child_router = getattr(module, "router", None)

    if child_router is None:
        raise RuntimeError(
            f"{module.__name__} must define 'router'"
        )

    if not isinstance(child_router, APIRouter):
        raise RuntimeError(
            f"{module.__name__}.router must be an APIRouter"
        )

    router.include_router(child_router)
