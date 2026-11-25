"""Exercise the managed session through Streamlit reruns."""
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from streamlit.testing.v1 import AppTest


class ChatbotTests(unittest.TestCase):
    def test_managed_session_reused_and_cleared(self):
        calls = []
        tokens = iter(("first-session", "second-session"))

        def reply(request, **_kwargs):
            body = json.loads(request.data) if request.data else None
            calls.append((request.get_method(), request.full_url, body, request.headers))
            if request.full_url.endswith("/rag/sessions"):
                payload = {"session_id": next(tokens)}
            elif request.get_method() == "DELETE":
                payload = None
            elif body["query"] == "Lượt lỗi":
                raise URLError("offline")
            else:
                payload = {"status": "needs_clarification", "answer": "Bạn muốn hỏi chủ đề nào?", "sources": []}
            response = MagicMock()
            response.__enter__.return_value.read.return_value = json.dumps(payload).encode() if payload else b""
            return response

        with patch("urllib.request.urlopen", side_effect=reply):
            chat = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
            chat.chat_input[0].set_value("Còn triệu chứng thì sao?").run()
            self.assertEqual(chat.info[0].value, "Bạn muốn hỏi chủ đề nào?")
            chat.chat_input[0].set_value("Lượt lỗi").run()
            self.assertTrue(chat.error)
            chat.chat_input[0].set_value("Mất ngủ").run()
            chat.button[0].click().run()
            self.assertEqual(len(chat.chat_message), 0)
            chat.chat_input[0].set_value("Còn nguyên nhân thì sao?").run()

        requests = [body for _, url, body, _ in calls if url.endswith("/rag/answer")]
        self.assertEqual([body["session_id"] for body in requests],
                         ["first-session", "first-session", "first-session", "second-session"])
        self.assertEqual([body["query"] for body in requests],
                         ["Còn triệu chứng thì sao?", "Lượt lỗi", "Mất ngủ", "Còn nguyên nhân thì sao?"])
        self.assertTrue(all("history" not in body for body in requests))
        deletes = [headers for method, _, _, headers in calls if method == "DELETE"]
        self.assertEqual(deletes[0]["X-yhct-session"], "first-session")

    def test_expired_session_stays_visible_until_cleared(self):
        def reply(request, **_kwargs):
            if request.full_url.endswith("/rag/answer"):
                raise HTTPError(request.full_url, 410, "Expired", {}, None)
            response = MagicMock()
            response.__enter__.return_value.read.return_value = b'{"session_id":"first-session"}'
            return response

        with patch("urllib.request.urlopen", side_effect=reply):
            chat = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
            chat.chat_input[0].set_value("Còn nguyên nhân thì sao?").run()
        self.assertIn("Phiên đã hết hạn", chat.error[0].value)
        self.assertEqual(chat.session_state.conversation_token, "first-session")


if __name__ == "__main__":
    unittest.main()
