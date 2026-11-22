"""Repository layer: the sole evidence source used by the researcher role."""

from __future__ import annotations

import sample_data
from models import ResearcherOutput

try:
    import search_client
except Exception:  # pragma: no cover - optional adapter
    search_client = None


def get_evidence(query: str, allow_web: bool = False) -> ResearcherOutput:
    if allow_web and search_client and search_client.is_configured():
        try:
            return search_client.search(query)
        except Exception:
            pass
    return sample_data.lookup(query)
