"""
Simplified Azure AI Agent using the OpenAI SDK against Azure OpenAI.

This module expects PROJECT_ENDPOINT to be an Azure OpenAI endpoint or any
URL under it (for example, a model/deployment URL). The host portion will
be used to construct the AzureOpenAI client endpoint.
"""

import os
from typing import Dict, Optional, Any
from urllib.parse import urlparse

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def _normalize_azure_endpoint(endpoint: str) -> str:
    """
    Normalize a PROJECT_ENDPOINT or model URI to the Azure OpenAI resource endpoint.

    Accepts either a full resource endpoint (e.g., https://name.openai.azure.com),
    a deployment/model URL, or a legacy project URL and returns the scheme and host
    portion suitable for AzureOpenAI.azure_endpoint.
    """
    parsed = urlparse(endpoint)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid PROJECT_ENDPOINT; expected a full https URL.")
    return f"{parsed.scheme}://{parsed.netloc}"


DEBUG_AGENT_LOGS = os.environ.get("DEBUG_AGENT_LOGS", "").lower() in ("1", "true", "yes", "on")


class AzureAgentManager:
    """Simple agent manager using OpenAI SDK"""

    def __init__(self, endpoint: str, model_name: str):
        self.endpoint = endpoint
        self.model_name = model_name
        self.client = None
        self.assistant = None
        self.thread_id = None

    def initialize(self) -> bool:
        """Initialize OpenAI client and create assistant"""
        try:
            if DEBUG_AGENT_LOGS:
                print(f"[DEBUG] Initializing AzureAgentManager with endpoint={self.endpoint}, model={self.model_name}")

            # Get token provider
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default"
            )

            # Normalize to Azure OpenAI resource endpoint (scheme + host)
            azure_endpoint = _normalize_azure_endpoint(self.endpoint)

            self.client = AzureOpenAI(
                azure_ad_token_provider=token_provider,
                api_version="2024-05-01-preview",
                azure_endpoint=azure_endpoint
            )

            # Create assistant
            self.assistant = self.client.beta.assistants.create(
                model=self.model_name,
                name="code-demo",
                instructions="You are a data visualization assistant. Create clear charts using Python and matplotlib.",
                tools=[{"type": "code_interpreter"}]
            )
            if DEBUG_AGENT_LOGS:
                print(f"[DEBUG] Assistant created: {self.assistant.id}")
            else:
                print(f"✓ Assistant created: {self.assistant.id}")
            return True

        except Exception as e:
            print(f"✗ Init error: {e}")
            return False

    def create_thread(self) -> Optional[str]:
        """Create conversation thread"""
        try:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
            if DEBUG_AGENT_LOGS:
                print(f"[DEBUG] Created thread: {self.thread_id}")
            return self.thread_id
        except Exception as e:
            print(f"Thread error: {e}")
            return None

    def send_message(self, user_message: str, thread_id: Optional[str] = None) -> Optional[Dict]:
        """Send message and get response"""
        try:
            tid = thread_id or self.thread_id
            if not tid:
                tid = self.create_thread()

            if DEBUG_AGENT_LOGS:
                print(f"[DEBUG] Sending message to assistant {self.assistant.id} on thread {tid}: {user_message}")

            # Create message
            self.client.beta.threads.messages.create(
                thread_id=tid,
                role="user",
                content=user_message
            )

            # Run and poll
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=tid,
                assistant_id=self.assistant.id
            )

            if DEBUG_AGENT_LOGS:
                print(f"[DEBUG] Run status: {run.status}")

            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=tid)

                for msg in messages.data:
                    if msg.role == "assistant":
                        text = []
                        files = []

                        for content in msg.content:
                            # Text content (and embedded annotations)
                            if hasattr(content, "text") and content.text:
                                text.append(content.text.value)

                                # Look for file-related annotations (file_path, file_citation)
                                annotations = getattr(content.text, "annotations", []) or []
                                for ann in annotations:
                                    ann_type = getattr(ann, "type", None)
                                    if ann_type == "file_path":
                                        file_obj = getattr(ann, "file_path", None)
                                    elif ann_type == "file_citation":
                                        file_obj = getattr(ann, "file_citation", None)
                                    else:
                                        file_obj = None

                                    file_id = getattr(file_obj, "file_id", None) if file_obj else None
                                    if file_id:
                                        files.append({
                                            "type": "file",
                                            "file_id": file_id,
                                            "text": getattr(ann, "text", "") or "",
                                        })

                            # Image output from code interpreter
                            if hasattr(content, "image_file") and content.image_file:
                                files.append({
                                    "type": "image",
                                    "file_id": content.image_file.file_id,
                                    "extension": ".png",
                                })
                        if DEBUG_AGENT_LOGS:
                            try:
                                print("[DEBUG] Raw assistant message:")
                                # Many OpenAI types support model_dump_json; fall back to repr
                                print(msg.model_dump_json(indent=2))  # type: ignore[attr-defined]
                            except Exception:
                                print(msg)
                            print(f"[DEBUG] Parsed text: {' '.join(text)}")
                            print(f"[DEBUG] Parsed files: {files}")

                        return {
                            "status": "success",
                            "text": "\n".join(text),
                            "files": files,
                        }

            return {'status': 'failed', 'error': f'Run status: {run.status}'}

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def download_file(self, file_id: str, file_path: str) -> bool:
        """Download file"""
        try:
            content = self.client.files.content(file_id)
            with open(file_path, 'wb') as f:
                f.write(content.read())
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False

    def cleanup(self):
        """Delete assistant"""
        try:
            if self.assistant:
                self.client.beta.assistants.delete(self.assistant.id)
        except:
            pass


def create_agent_from_env() -> Optional[AzureAgentManager]:
    """Create agent from environment variables"""
    endpoint = os.environ.get("PROJECT_ENDPOINT")
    model = os.environ.get("MODEL_DEPLOYMENT_NAME")

    if not endpoint or not model:
        return None

    manager = AzureAgentManager(endpoint, model)
    return manager if manager.initialize() else None
