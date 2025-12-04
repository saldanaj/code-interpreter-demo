# Azure AI Foundry Code Interpreter Demo

A Streamlit web application that demonstrates the **Code Interpreter** capabilities of Azure OpenAI models.  
The app uses the OpenAI Python SDK (Azure OpenAI integration) and the Assistants API to execute Python code, generate charts, and create downloadable files such as CSVs.

## Features

- **Interactive chat interface** – Natural conversation with an assistant backed by an Azure OpenAI deployment.
- **Chart generation** – Create bar charts, line plots, pie charts, scatter plots, and other visualizations.
- **File creation and downloads** – Generate CSV and other data files and download them from the UI.
- **Inline display** – Render generated images directly in the Streamlit app.
- **Multi-turn conversations** – Maintain conversation context across multiple messages.

## Quick Start

### Prerequisites

1. **Azure OpenAI model deployment**, typically created via Azure AI Foundry:
   - A deployed model (for example, `gpt-4o`) that supports the Code Interpreter tool.

2. **Azure CLI** installed and authenticated:
   ```bash
   az login
   ```

3. **Python 3.8+** installed

### Installation

1. **Clone or navigate to this repository**:
   ```bash
   cd code-interpreter-demo
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Azure settings:
   ```bash
   PROJECT_ENDPOINT=https://your-resource.openai.azure.com
   MODEL_DEPLOYMENT_NAME=<your-deployment-name>
   ```

   `PROJECT_ENDPOINT` can be either:
   - The Azure OpenAI endpoint (recommended), or
   - A model/deployment URL copied from Azure AI Foundry. Only the scheme and host are used.

### Finding Your Azure Settings

#### Azure OpenAI Endpoint

1. Go to [Azure AI Foundry Portal](https://ai.azure.com/)
2. Select your project
3. Go to **Models + endpoints** (or your Azure OpenAI resource in the Azure portal)
4. Copy the **Endpoint** for your Azure OpenAI resource  
   Format: `https://<resource-name>.openai.azure.com`

#### Model Deployment Name

1. In your Azure AI Foundry project
2. Go to **Deployments** (or **Models + endpoints**)
3. Find your deployed model
4. Copy the **Deployment name** (e.g., "gpt-4o", "gpt-4-turbo")

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## Usage Examples

Try these sample prompts (also available as buttons in the sidebar):

### Chart Generation
```
Create a bar chart showing quarterly sales: Q1=$100K, Q2=$150K, Q3=$120K, Q4=$200K
```

```
Generate a line plot showing temperature trends: Jan=32°F, Feb=35°F, Mar=45°F, Apr=58°F, May=68°F, Jun=78°F
```

```
Create a pie chart of market share: Company A=35%, B=25%, C=20%, D=15%, Others=5%
```

### Data Generation
```
Create a CSV file with 10 rows of sample customer data (name, email, purchase_amount)
```

### Data Analysis
```
Generate 100 random data points and create a histogram showing their distribution
```

## Project Structure

```
code-interpreter-demo/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create from .env.example)
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── utils/
│   ├── __init__.py           # Package initializer
│   ├── azure_agent.py        # Agent management and operations
│   └── file_handler.py       # File download and display utilities
└── downloads/                 # Generated files (created at runtime)
```

## Architecture and SDKs

This demo uses the following approach:

- **UI / Web framework**: `streamlit` for the chat-style web interface.
- **Model access**: `openai` Python SDK, using the `AzureOpenAI` client to call Azure OpenAI.
  - Uses the Assistants API with the `code_interpreter` tool enabled.
  - The assistant is created programmatically in `utils/azure_agent.py`.
- **Authentication**: `azure-identity` with `DefaultAzureCredential`, wrapped by `get_bearer_token_provider` to obtain tokens for Azure OpenAI.
- **Configuration**: `python-dotenv` to load `.env`.
- **Images and file handling**: `Pillow` and local utilities in `utils/file_handler.py` for saving and serving generated files.

Note: `agent-framework` is currently listed in `requirements.txt` but the demo uses the OpenAI SDK directly rather than the Agent Framework abstractions.

## Configuration

### Environment Variables

- `PROJECT_ENDPOINT`: Azure OpenAI endpoint (or model URL; only host is used).
- `MODEL_DEPLOYMENT_NAME`: Name of your deployed model.
- `DEBUG_AGENT_LOGS` (optional): Set to `true` to print detailed assistant and thread logs to the terminal while Streamlit is running.

#### Debug logging

To see detailed logs from the assistant and thread operations while the app is running, set the environment variable before starting Streamlit:

```bash
export DEBUG_AGENT_LOGS=true
streamlit run app.py
```

On Windows PowerShell:

```powershell
$env:DEBUG_AGENT_LOGS = "true"
streamlit run app.py
```

### Authentication

The application uses `DefaultAzureCredential` from Azure Identity SDK, which automatically handles authentication through:
1. Environment variables
2. Managed identity
3. Azure CLI authentication (`az login`)
4. Visual Studio Code authentication
5. Interactive browser authentication

For local development, ensure you're logged in via Azure CLI:
```bash
az login
```

## Troubleshooting

### "Failed to initialize agent"

**Solution**:
- Verify your `.env` file has correct values
- Ensure you're logged in to Azure CLI: `az login`
- Check that your Azure AI Foundry project has an active deployment

### "Authentication failed"

**Solution**:
- Run `az login` to authenticate with Azure
- Verify you have access to the Azure AI Foundry project
- Check your subscription and resource group permissions

### "Rate limit exceeded"

**Solution**:
- Your model deployment has quota limits
- Wait a few moments and try again
- Consider upgrading your deployment tier in Azure portal

### Files not downloading

**Solution**:
- Check that the `downloads/` directory has write permissions
- Ensure sufficient disk space
- Check browser download settings
- Enable `DEBUG_AGENT_LOGS=true` and inspect the terminal for any `Download error` messages

## Dependencies

Core dependencies (see `requirements.txt`):
- `streamlit` – web application framework
- `python-dotenv` – environment variable management
- `Pillow` – image processing
- `agent-framework` – currently used as a dependency source; the app itself calls the OpenAI SDK directly.

You will also need (directly or transitively):
- `openai` – Python client library providing `AzureOpenAI`
- `azure-identity` – authentication via `DefaultAzureCredential`

## Contributing

This is a demo application. Feel free to fork and customize for your needs!

## Notes

- Generated files are stored in the `downloads/` directory
- Old files are automatically cleaned up after 50 files
- Each chat session maintains conversation context
- Threads persist until you click "Clear Chat"

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Agents Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/)
- [Code Interpreter Tool Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)
- [Streamlit Documentation](https://docs.streamlit.io/)

## License

This project is for demonstration purposes. Modify and use as needed.
