"""
Azure AI Foundry Code Interpreter Demo - Streamlit Application

This app demonstrates the Code Interpreter tool capabilities of Azure AI Foundry agents.
Users can ask the agent to generate charts, analyze data, and create files which can be
downloaded or displayed in the UI.
"""

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Import our custom modules
from utils.azure_agent import create_agent_from_env
from utils.file_handler import (
    download_files,
    get_file_display_name,
    read_file_bytes,
    get_mime_type,
    cleanup_old_files
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Azure AI Code Interpreter Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample prompts for users to try
SAMPLE_PROMPTS = [
    "Create a bar chart showing quarterly sales: Q1=$100K, Q2=$150K, Q3=$120K, Q4=$200K",
    "Generate a line plot showing temperature trends: Jan=32°F, Feb=35°F, Mar=45°F, Apr=58°F, May=68°F, Jun=78°F",
    "Create a pie chart of market share: Company A=35%, B=25%, C=20%, D=15%, Others=5%",
    "Make a scatter plot with 50 random data points showing correlation",
    "Create a CSV file with 10 rows of sample customer data (name, email, purchase_amount)",
]


def initialize_session_state():
    """Initialize all session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = None
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def initialize_agent():
    """Initialize the Azure AI agent if not already initialized."""
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing Azure AI Agent..."):
            try:
                agent_manager = create_agent_from_env()
                if agent_manager:
                    st.session_state.agent_manager = agent_manager
                    st.session_state.agent_initialized = True
                    st.success("✅ Agent initialized successfully!")
                    return True
                else:
                    st.error("❌ Failed to initialize agent. Please check your environment variables.")
                    return False
            except Exception as e:
                st.error(f"❌ Error initializing agent: {str(e)}")
                st.info("💡 Make sure you have:\n"
                       "1. Set PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME in your .env file\n"
                       "2. Logged in to Azure CLI: `az login`\n"
                       "3. Installed all requirements: `pip install -r requirements.txt`")
                return False
    return True


def display_message_with_files(role: str, content: str, files: list = None):
    """
    Display a chat message with optional file attachments.

    Args:
        role: 'user' or 'assistant'
        content: Message text content
        files: List of file information dictionaries
    """
    with st.chat_message(role):
        st.write(content)

        if files:
            for file_info in files:
                if not file_info.get('success', False):
                    continue

                local_path = file_info.get('local_path')
                if not local_path or not Path(local_path).exists():
                    continue

                file_type = file_info.get('type', 'file')
                display_name = get_file_display_name(file_info)

                # Display images inline
                if file_type == 'image':
                    st.image(local_path, caption=display_name, use_container_width=True)

                # Provide download button for all files
                file_bytes = read_file_bytes(local_path)
                if file_bytes:
                    mime_type = get_mime_type(file_info)
                    file_name = Path(local_path).name

                    st.download_button(
                        label=f"📥 Download {display_name}",
                        data=file_bytes,
                        file_name=file_name,
                        mime=mime_type,
                        key=f"download_{file_info['file_id']}"
                    )


def process_user_message(user_message: str):
    """
    Process a user message and get agent response.

    Args:
        user_message: The message from the user
    """
    if not st.session_state.agent_manager:
        st.error("Agent not initialized!")
        return

    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
        "files": []
    })

    # Display user message
    with st.chat_message("user"):
        st.write(user_message)

    # Show assistant "thinking"
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Send message to agent
            response = st.session_state.agent_manager.send_message(
                user_message=user_message,
                thread_id=st.session_state.thread_id
            )

            # Update thread_id if this was the first message
            if st.session_state.thread_id is None and st.session_state.agent_manager.thread_id:
                st.session_state.thread_id = st.session_state.agent_manager.thread_id

            # Handle response
            if response['status'] in ['success', 'completed']:
                assistant_text = response.get('text', 'No response')

                # Download any generated files
                files_info = response.get('files', [])
                downloaded_files = []

                if files_info:
                    with st.spinner("Downloading generated files..."):
                        downloaded_files = download_files(
                            st.session_state.agent_manager,
                            files_info
                        )

                # Display the response
                st.write(assistant_text)

                # Display files
                for file_info in downloaded_files:
                    if not file_info.get('success', False):
                        continue

                    local_path = file_info.get('local_path')
                    if not local_path or not Path(local_path).exists():
                        continue

                    file_type = file_info.get('type', 'file')
                    display_name = get_file_display_name(file_info)

                    # Display images inline
                    if file_type == 'image':
                        st.image(local_path, caption=display_name, use_container_width=True)

                    # Provide download button for all files
                    file_bytes = read_file_bytes(local_path)
                    if file_bytes:
                        mime_type = get_mime_type(file_info)
                        file_name = Path(local_path).name

                        st.download_button(
                            label=f"📥 Download {display_name}",
                            data=file_bytes,
                            file_name=file_name,
                            mime=mime_type,
                            key=f"download_{file_info['file_id']}"
                        )

                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "files": downloaded_files
                })

            else:
                # Error occurred
                error_msg = response.get('error', 'Unknown error occurred')
                st.error(f"Error: {error_msg}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {error_msg}",
                    "files": []
                })


def render_sidebar():
    """Render the sidebar with agent info and sample prompts."""
    with st.sidebar:
        st.title("🤖 Azure AI Agent")

        # Connection status
        if st.session_state.agent_initialized:
            st.success("✅ Connected")
            manager = st.session_state.agent_manager
            if manager and getattr(manager, "assistant", None):
                assistant_name = getattr(manager.assistant, "name", None) or "code-demo"
                st.info(f"**Assistant:** {assistant_name}")
                st.info(f"**Model (deployment):** {manager.model_name}")
        else:
            st.warning("⚠️ Not Connected")

        st.divider()

        # Sample prompts section
        st.subheader("💡 Try these prompts:")

        for i, prompt in enumerate(SAMPLE_PROMPTS):
            # Create a shorter label for the button
            label = prompt[:50] + "..." if len(prompt) > 50 else prompt

            if st.button(label, key=f"sample_{i}", use_container_width=True):
                st.session_state.pending_prompt = prompt

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = None
            cleanup_old_files(max_files=20)
            st.rerun()

        st.divider()

        # Instructions
        st.subheader("ℹ️ About")
        st.markdown("""
        This demo showcases Azure AI Foundry's **Code Interpreter** tool.

        The agent can:
        - Generate charts and visualizations
        - Create CSV files with data
        - Perform data analysis
        - Execute Python code safely

        Generated files are displayed inline and available for download.
        """)


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main content area
    st.title("🤖 Azure AI Code Interpreter Demo")
    st.markdown("Ask the agent to create charts, analyze data, or generate files!")

    # Initialize agent if needed
    if not st.session_state.agent_initialized:
        if not initialize_agent():
            st.stop()

    # Display chat history
    for message in st.session_state.messages:
        display_message_with_files(
            role=message["role"],
            content=message["content"],
            files=message.get("files", [])
        )

    # Handle pending prompt from sample buttons
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        process_user_message(prompt)
        st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask the agent to generate charts or analyze data..."):
        process_user_message(prompt)
        st.rerun()


if __name__ == "__main__":
    main()
