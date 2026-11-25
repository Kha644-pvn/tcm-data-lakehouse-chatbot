"""Chatbot MVP giao tiếp với FastAPI POST /rag/answer.

Chạy: python -m streamlit run chatbot/app.py
"""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import streamlit as st

from api.services.manifest_service import baseline_source_ids
from rag.answer_view import to_display_markdown


st.set_page_config(page_title="Tra cứu Y học cổ truyền", page_icon="📚", layout="centered")

st.title("📚 Tra cứu tài liệu Y học cổ truyền")
st.caption("Data Lakehouse + RAG | Tra cứu học thuật có dẫn nguồn, không thay thế tư vấn y tế.")

with st.sidebar:
    st.subheader("Cấu hình")
    base_url = st.text_input("FastAPI URL", value="http://127.0.0.1:8000")
    method = st.selectbox("Phương pháp tìm kiếm", ["hybrid", "dense"], index=0)
    top_k = st.slider("Số đoạn context", min_value=1, max_value=10, value=5)
    available_documents = baseline_source_ids()
    selected_documents = st.multiselect(
        "Giới hạn tài liệu (để trống = tất cả nguồn thật)",
        available_documents, default=[]
    )
    clear_history = st.button("Xóa lịch sử hội thoại", use_container_width=True)
    st.caption("Hiển thị tên tài liệu và trang PDF; không công bố toàn văn nguồn đang chờ rà soát bản quyền.")


def request_api(path, *, method="POST", body=None, headers=None, timeout=15):
    request = Request(
        base_url.rstrip("/") + path,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None,
        headers={"Content-Type": "application/json; charset=utf-8", **(headers or {})},
        method=method,
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
            return json.loads(payload) if payload else None
    except HTTPError as error:
        if error.code == 410:
            raise RuntimeError("Phiên đã hết hạn. Bấm Xóa lịch sử hội thoại để bắt đầu lại.") from error
        if error.code == 409:
            raise RuntimeError("Phiên đang xử lý một câu hỏi khác. Hãy thử lại sau.") from error
        raise RuntimeError(f"API trả HTTP {error.code}.") from error
    except URLError as error:
        raise RuntimeError("Không thể kết nối FastAPI. Kiểm tra địa chỉ ở thanh bên.") from error


def get_answer(query: str) -> dict:
    if not st.session_state.get("conversation_token"):
        session = request_api("/rag/sessions")
        st.session_state.conversation_token = session["session_id"]
    payload = {
        "query": query, "method": method, "top_k": top_k,
        "session_id": st.session_state.conversation_token,
        "document_ids": selected_documents or list(available_documents),
    }
    return request_api("/rag/answer", body=payload, timeout=540)


def show_assistant(response: dict):
    status = response.get("status", "unknown")
    if status == "answered":
        st.markdown(to_display_markdown(response.get("answer") or ""))
        citations = response.get("citations") or []
        sources = response.get("sources") or []
        if not citations or not sources:
            st.warning("API báo answered nhưng thiếu trích dẫn; cần xem lại câu trả lời.")
        else:
            if response.get("answer_origin") == "pdf_transcription":
                st.caption("Định lượng được chép từ PDF để tra cứu học thuật. Không dùng làm đơn thuốc cá nhân.")
            elif response.get("answer_origin") == "treatment_section":
                st.caption("Các mục thuốc được trích từ tài liệu theo bệnh và thể bệnh. Mở nguồn để đối chiếu toàn bộ mục điều trị.")
            elif response.get("answer_origin") == "symptom_reference":
                st.caption("Đối chiếu với giáo trình YHCT. Việc xác định thể bệnh cần thăm khám.")
            elif response.get("answer_origin") == "reviewed_chapter":
                st.caption("Nội dung đối chiếu với các trang đã rà soát của giáo trình.")
            else:
                st.caption("Nguồn đã được API gắn nhãn; chưa xác minh tự động tính đúng y khoa.")
            with st.expander("Xem nguồn trích dẫn", expanded=True):
                for src in sources:
                    st.markdown(
                        f"**{src.get('source_label', '?')}** — "
                        f"{src.get('document_id', '?')}, "
                        f"{src.get('page_or_section', '?')}"
                    )
                    st.caption(f"{src.get('file_name', '?')} | Phiên bản {src.get('version', '?')} | "
                               f"Manifest {src.get('manifest_id', '?')} | Passage {src.get('passage_id', '?')}")
                    if all(src.get(field) for field in ("document_id", "passage_id", "version")):
                        document = quote(src["document_id"], safe="")
                        passage = quote(src["passage_id"], safe="")
                        version = urlencode({"version": src["version"]})
                        st.markdown(f"[Truy vết nguồn PDF]({base_url.rstrip('/')}/sources/{document}/traceability/{passage}?{version})")
    elif status == "needs_clarification":
        st.info(response["answer"])
    elif status == "urgent_care":
        st.error(response["answer"])
    elif status == "insufficient_context":
        st.info(response.get("answer") or "Chưa có đủ bằng chứng trong tài liệu để trả lời câu hỏi này.")
    elif status == "needs_review":
        st.warning("Câu trả lời chưa vượt qua kiểm tra trích dẫn hoặc tính nhất quán. Cần kiểm tra thêm trước khi hiển thị.")
    else:
        st.error(f"Không nhận được kết quả hợp lệ từ API (status: {status}).")
    topic = (response.get("conversation") or {}).get("topic")
    if topic:
        st.caption(f"Chủ đề đang tra cứu: {topic}")
    origin = response.get("answer_origin")
    generator = {"pdf_transcription": "Bản chép PDF", "treatment_section": "Mục thuốc trong tài liệu",
                 "reviewed_chapter": "Mục giáo trình đã đối chiếu"}.get(
        origin, response.get("model") or "—"
    )
    if origin not in {"symptom_intake", "symptom_reference"}:
        st.caption(f"Phương pháp: {response.get('method', '?')} | Nguồn trả lời: {generator} | Trạng thái: {status}")


if st.session_state.get("conversation_url") != base_url.rstrip("/"):
    st.session_state.conversation_url = base_url.rstrip("/")
    st.session_state.conversation_token = None
    st.session_state.messages = []

if clear_history:
    try:
        token = st.session_state.conversation_token
        if token:
            request_api("/rag/session", method="DELETE", headers={"X-YHCT-Session": token})
    except RuntimeError as error:
        st.error(str(error))
    else:
        st.session_state.messages = []
        st.session_state.conversation_token = None
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            show_assistant(message["response"])
        else:
            st.markdown(message["content"])

question = st.chat_input("Nhập câu hỏi về tài liệu Y học cổ truyền…", max_chars=1000)
if question and (question := question.strip()):
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Đang truy xuất tài liệu và tạo câu trả lời…"):
            try:
                answer = get_answer(question)
            except Exception as error:
                st.error(str(error))
            else:
                st.session_state.messages.extend([
                    {"role": "user", "content": question},
                    {"role": "assistant", "response": answer},
                ])
                show_assistant(answer)
