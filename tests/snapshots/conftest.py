from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _pin_banner_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "albert_code.cli.textual_ui.widgets.banner.banner.__version__", "0.0.0"
    )
