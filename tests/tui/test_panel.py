import pytest
from tui.widgets.panel import ControlPanel, _TAB_NAMES


def test_default_active_tab():
    panel = ControlPanel()
    assert panel.active_tab == "Inventory"


def test_set_active_tab():
    panel = ControlPanel()
    panel.set_active_tab("Skills")
    assert panel.active_tab == "Skills"


def test_set_invalid_tab_raises():
    panel = ControlPanel()
    with pytest.raises(ValueError):
        panel.set_active_tab("NotATab")
