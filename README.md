# Azure AI Foundry Code Interpreter Demo

A Streamlit web application demonstrating the **Code Interpreter** tool capabilities of Azure AI Foundry agents. This demo allows you to interact with an AI agent that can generate charts, create CSV files, and perform data analysis using Python code execution.

## 🎯 Features

- 💬 **Interactive Chat Interface** - Natural conversation with the AI agent
- 📊 **Chart Generation** - Create bar charts, line plots, pie charts, and scatter plots
- 📁 **File Creation** - Generate CSV files and other data formats
- 🖼️ **Inline Display** - View generated charts directly in the UI
- 📥 **File Downloads** - Download all generated files
- 🔄 **Multi-turn Conversations** - Maintain context across multiple messages

## 🚀 Quick Start

### Prerequisites

1. **Azure AI Foundry Project** with:
   - A deployed model (e.g., GPT-4o)
   - Code Interpreter tool enabled

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

   Edit `.env` and add your Azure credentials:
   ```bash
   PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project-id
   MODEL_DEPLOYMENT_NAME=gpt-4o
   ```

### Finding Your Azure Credentials

#### Project Endpoint

1. Go to [Azure AI Foundry Portal](https://ai.azure.com/)
2. Select your project
3. Go to **Overview** or **Settings**
4. Copy the **Project connection string** or **Endpoint URL**
5. Format should be: `https://<resource-name>.services.ai.azure.com/api/projects/<project-id>`

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

## 💡 Usage Examples

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

## 🏗️ Project Structure

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

## 🔧 Configuration

### Environment Variables

- **PROJECT_ENDPOINT**: Your Azure AI Foundry project endpoint URL
- **MODEL_DEPLOYMENT_NAME**: Name of your deployed model

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

## 🛠️ Troubleshooting

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

## 📦 Dependencies

Core dependencies (see `requirements.txt`):
- `agent-framework` - Azure AI agent framework (pre-release)
- `streamlit` - Web application framework
- `python-dotenv` - Environment variable management
- `Pillow` - Image processing

The `agent-framework` includes:
- `azure-ai-projects` - Azure AI project client
- `azure-ai-agents` - Agent management SDK
- `azure-identity` - Azure authentication
- `azure-core` - Core Azure SDK functionality

## 🤝 Contributing

This is a demo application. Feel free to fork and customize for your needs!

## 📝 Notes

- Generated files are stored in the `downloads/` directory
- Old files are automatically cleaned up after 50 files
- Each chat session maintains conversation context
- Threads persist until you click "Clear Chat"

## 🔗 Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Agents Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/)
- [Code Interpreter Tool Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 📄 License

This project is for demonstration purposes. Modify and use as needed.

---

**Happy coding!** 🚀
