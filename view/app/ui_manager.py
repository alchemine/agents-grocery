"""UI Manager for streamlit app"""

from os import getenv
from uuid import uuid4
from pendulum import timezone

import streamlit as st
from elasticsearch import Elasticsearch

from config import CFG, ELASTICSEARCH_URL, ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD


TZ = timezone(getenv("TZ", "Asia/Seoul"))


class UIManager:
    def __init__(self):
        self.es = Elasticsearch(
            ELASTICSEARCH_URL,
            basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
        )

    def setup_page(self) -> None:
        """Setup the page config"""
        st.set_page_config(layout="wide")

    def init_session_state(self) -> None:
        """Initialize the session state"""
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "ai",
                    "content": "안녕하세요. 무엇이든 물어보세요! 무엇이 궁금하신가요?",
                }
            ]

    def render_sidebar(self) -> None:
        """Render the sidebar"""
        with st.sidebar:
            self.render_sidebar_content()

    def render_sidebar_content(self) -> None:
        """Render the sidebar content"""
        user_id = st.text_input("User ID", key="user_id", value="test")
        if not user_id:
            st.session_state.user_id = str(uuid4())
