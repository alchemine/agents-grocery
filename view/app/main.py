import streamlit as st
from streamlit_extras.bottom_container import bottom

from config import CFG
from app.ui_manager import UIManager
from src.common.request_utils import safe_request


CFG_STREAMLIT = CFG.streamlit


class App:
    def __init__(self) -> None:
        """Initialize the app"""
        self.ui = UIManager()
        self.ui.setup_page()
        self.ui.init_session_state()

    def run(self) -> None:
        """Run the app"""
        # Render the sidebar
        self.ui.render_sidebar()

        # Render the left column
        # left_col, _, right_col = st.columns([1, 0.01, 1])
        left_col, _ = st.columns([1, 0.01])

        # Render the chat input
        with st.spinner("Thinking..."):
            with bottom():
                if query := st.chat_input():
                    response, contexts = self._handle_message(
                        query, user_id=st.session_state.user_id
                    )
                    st.session_state.contexts = contexts
                    st.session_state.messages.extend(
                        [
                            {"role": "user", "content": query},
                            {"role": "assistant", "content": response},
                        ]
                    )
                    st.rerun()

        # Render the right column
        with left_col:
            self._render_chat_interface()

        # Render the right column
        # with right_col:
        #     self._render_context_interface()

    def _render_chat_interface(self) -> None:
        """Render the chat interface"""
        st.title("💭 Message History")
        st.caption("🚀 Powered by LLM")

        with st.container(height=CFG_STREAMLIT.default_container_height):
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"], unsafe_allow_html=True)

    def _render_context_interface(self) -> None:
        """Render the context interface"""
        st.title("🔍 Context Page")
        st.caption("🚀 Powered by PostgreSQL")

        with st.container(height=CFG_STREAMLIT.default_container_height):
            pass
            # text_units = st.session_state.text_units
            # for i, context in enumerate(text_units):
            #     with st.expander(f"참고 자료 {i+1}"):
            #         for c in context:
            #             st.write(c["pre_text"])
            #             st.image(c["img_path"])
            #             st.write(c["post_text"])

    def _handle_message(self, query: str, user_id: str) -> tuple[str, list[dict]]:
        """Get message from inflo-agent API"""
        result = safe_request(
            url=f"{CFG.service.agents.qa_agent.url}/chat/completions",
            json={"query": query, "user_id": user_id},
        )
        response, contexts = result["response"], result["contexts"]
        return response, contexts


if __name__ == "__main__":
    app = App()
    app.run()
