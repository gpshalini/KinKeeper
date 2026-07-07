import pytest
from app.agent import chat_parser

class MockContext:
    def __init__(self):
        self.state = {
            "parsed_messages": [],
            "skipped_messages": [],
            "media_skipped_count": 0
        }

def test_bracketed_timestamp_parsing():
    ctx = MockContext()
    chat_text = "[6/1/25, 8:12 AM] Sarah: Happy birthday Olivia 🎂"
    res = chat_parser(ctx, chat_text)
    assert len(res) == 1
    assert res[0]["sender"] == "Sarah"
    assert res[0]["content"] == "Happy birthday Olivia 🎂"
    assert res[0]["date"] == "6/1/25"
    assert res[0]["time"] == "8:12 AM"

def test_dash_timestamp_parsing():
    ctx = MockContext()
    chat_text = "7/3/26, 9:00:00 AM - Michael: Let's celebrate!"
    res = chat_parser(ctx, chat_text)
    assert len(res) == 1
    assert res[0]["sender"] == "Michael"
    assert res[0]["content"] == "Let's celebrate!"
    assert res[0]["date"] == "7/3/26"
    assert res[0]["time"] == "9:00:00 AM"

def test_multiline_merging():
    ctx = MockContext()
    chat_text = (
        "[6/1/25, 8:12 AM] Sarah: Line 1\n"
        "Line 2 continuation\n"
        "[6/1/25, 8:15 AM] Michael: Another message"
    )
    res = chat_parser(ctx, chat_text)
    assert len(res) == 2
    assert res[0]["sender"] == "Sarah"
    assert res[0]["content"] == "Line 1\nLine 2 continuation"
    assert res[1]["sender"] == "Michael"

def test_media_omitted_skipping():
    ctx = MockContext()
    chat_text = (
        "[6/1/25, 8:12 AM] Sarah: <image omitted>\n"
        "[6/1/25, 8:15 AM] Michael: Happy Birthday!"
    )
    res = chat_parser(ctx, chat_text)
    assert len(res) == 1  # ONLY Michael's message is kept
    assert ctx.state["media_skipped_count"] == 1
    assert len(ctx.state["skipped_messages"]) == 1
    assert ctx.state["skipped_messages"][0]["reason"] == "media_omitted"

def test_deleted_message_skipping():
    ctx = MockContext()
    chat_text = (
        "[6/1/25, 8:12 AM] Sarah: This message was deleted.\n"
        "[6/1/25, 8:15 AM] Michael: Happy Birthday!"
    )
    res = chat_parser(ctx, chat_text)
    assert len(res) == 1
    assert len(ctx.state["skipped_messages"]) == 1
    assert ctx.state["skipped_messages"][0]["reason"] == "deleted_message"

def test_system_message_skipping():
    ctx = MockContext()
    chat_text = (
        "[6/1/25, 8:12 AM] Sarah created this group\n"
        "[6/1/25, 8:15 AM] Michael: Happy Birthday!"
    )
    res = chat_parser(ctx, chat_text)
    assert len(res) == 1
    assert len(ctx.state["skipped_messages"]) == 1
    assert ctx.state["skipped_messages"][0]["reason"] == "unparsed_system_or_metadata"
