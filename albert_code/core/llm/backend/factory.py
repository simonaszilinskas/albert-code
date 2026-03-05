from __future__ import annotations

from albert_code.core.config import Backend
from albert_code.core.llm.backend.generic import GenericBackend
from albert_code.core.llm.backend.mistral import MistralBackend

BACKEND_FACTORY = {Backend.MISTRAL: MistralBackend, Backend.GENERIC: GenericBackend}
