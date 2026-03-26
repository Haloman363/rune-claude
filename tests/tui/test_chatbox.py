import pytest
from tui.widgets.chatbox import Chatbox, ChatMessage, MSG_PUBLIC, MSG_GAME


def test_initial_messages():
    cb = Chatbox()
    assert len(cb.messages) == 3
    assert "Welcome to Old School RuneScape" in cb.messages[0].text


def test_add_message():
    cb = Chatbox()
    cb.add_message("Hello world", MSG_PUBLIC)
    assert cb.messages[-1].text == "Hello world"
    assert cb.messages[-1].style == MSG_PUBLIC


def test_active_tab_default():
    cb = Chatbox()
    assert cb.active_tab == "All"


def test_set_active_tab():
    cb = Chatbox()
    cb.set_active_tab("Game")
    assert cb.active_tab == "Game"
