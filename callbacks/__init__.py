"""Callback registry — call ``register_all_callbacks(app)`` once at startup."""
from .sidebar_cb import register_sidebar_callbacks
from .risultati import register_risultati
from .inverse import register_inverse
from .rent import register_rent
from .amort import register_amort
from .sensitivity import register_sensitivity


def register_all_callbacks(app) -> None:
    """Register every Dash callback with the given app instance."""
    register_sidebar_callbacks(app)
    register_risultati(app)
    register_inverse(app)
    register_rent(app)
    register_amort(app)
    register_sensitivity(app)
