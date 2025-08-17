from typing import Literal

import streamlit as st
from streamlit_extras.bottom_container import bottom

from config import CFG
from src.common.request_utils import safe_request


CFG_STREAMLIT = CFG.streamlit
CFG_AGENTS = CFG.agents

ss = st.session_state


class App:
    def __init__(self) -> None:
        """Initialize the app"""
        self.initialize()

    def initialize(self) -> None:
        """Setup the page config"""
        st.set_page_config(layout="wide")
        if "agent_messages" not in ss:
            ss.agent_messages = {agent: [] for agent in CFG.service.agents}
        if "user_id" not in ss:
            ss.user_id = "test"

    def run(self) -> None:
        """Run the app"""
        # Render the sidebar
        with st.sidebar:
            st.text_input("User ID", key="user_id")

        # Render the tabs for each agent
        agent_names = list(CFG.service.agents)
        agent_names_disp = [
            CFG_AGENTS[agent_name].agent_name for agent_name in agent_names
        ]

        agent_tabs = st.tabs(agent_names_disp)
        for i, agent_name in enumerate(agent_names):
            with agent_tabs[i]:
                self._render_chat_interface(agent_name)

    def _render_chat_interface(self, agent_name: str) -> None:
        """Render the chat interface"""
        # Prepare header
        st.header(CFG_AGENTS[agent_name].onboarding_message)
        with st.container(height=CFG_STREAMLIT.default_container_height):
            for msg in ss.agent_messages[agent_name]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"], unsafe_allow_html=True)

        # Render the chat input
        query_key = f"{agent_name}_query"
        if query := st.chat_input("이곳에 입력해주세요.", key=query_key):
            self._append_message(agent_name, query, "user")
            with st.spinner("답변을 생성하는 중입니다.."):
                result = self._request_response(agent_name, query)
            self._append_message(agent_name, result["response"], "ai")
            # ss.contexts = result.get("contexts")
            st.rerun()

    def _append_message(
        self, agent_name: str, query: str, role: Literal["user", "ai"]
    ) -> None:
        ss.agent_messages[agent_name].append({"role": role, "content": query})

    def _request_response(self, agent_name: str, query: str) -> dict:
        """Request response from Agents API"""
        return safe_request(
            url=CFG.service.agents[agent_name].url,
            json={"query": query, "user_id": ss.user_id},
            return_data=True,
        )


if __name__ == "__main__":
    app = App()
    app.run()
