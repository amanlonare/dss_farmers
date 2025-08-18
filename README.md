# DSS Farmers Assistant

A Decision Support System for farmers that combines real-time weather data, agricultural knowledge, and AI to provide personalized farming recommendations.

## Features

- **Real-time Weather Integration**: Access current weather data and forecasts for your location
- **Agricultural Knowledge Base**: Query a rich database of farming knowledge
- **AI-Powered Recommendations**: Generate personalized advice based on your specific crop, soil conditions, and weather
- **Interactive Console Interface**: Easy-to-use text-based interface for asking questions

## Installation

This project uses `uv` for dependency management.

```bash
# Install uv if you don't have it already
pip install uv

# Clone the repository
git clone https://github.com/yourusername/dss_farmers.git
cd dss_farmers

# Create a virtual environment and install dependencies
uv venv
uv pip install -e .
```

## Creating Vector Database

The system uses a vector database to store and retrieve agricultural information. You can create this database with your own agricultural PDFs or text files:

1. Place your agricultural PDFs/TXTs in the resources folder
2. Run the vector database creation script:

```bash
python -m dss_farmers.rag.create_vector_db
```

This script will:

- Process all PDF and TXT files in the resources directory
- Split them into chunks of text
- Embed them using Sentence Transformers
- Store them in a ChromaDB vector database at vectordb

> **Note**: The quality of recommendations depends significantly on the agricultural documents you provide. Include documents related to crops, farming practices, pest management, etc.

## Setting Up Environment Variables

Create a `.env` file in the project root:

```
WEATHER_API=your_weatherapi_key_here
```

You can get a free API key from [WeatherAPI.com](https://www.weatherapi.com/).

## Running the System

### 1. Start the MCP Servers

You need to start both MCP servers in separate terminal windows:

#### Weather Server

```bash
python -m dss_farmers.mcp_servers.weather_server
```

This server will run on port 8000 and provide weather data via the `/mcp` and `/sse` endpoints.

#### Document RAG Server

```bash
python -m dss_farmers.mcp_servers.document_rag_server
```

This server will run on port 8001 and provide access to the agricultural knowledge base.

### 2. Run the DSS Farmers Chatbot

Once both servers are running, start the chatbot in a third terminal:

```bash
python -m dss_farmers.mcp_client.dss_farmers_chatbot
```

The chatbot will:

1. Connect to both MCP servers
2. Load the LLM model (may take a few minutes depending on your hardware)
3. Prompt you for input about your farming situation
4. Generate personalized recommendations

## Customization

### Using Different Language Models

The system is configured to use a lightweight model by default, but you can use more powerful models by modifying config.py:

```python
# LLM Configuration
LLM_CONFIG = {
    "model_name": "Xianjun/PLLaMa-7b-base",  # Change to your preferred model
    "generation_params": {
        "max_new_tokens": 1024,
        "temperature": 0.7,
        "do_sample": True,
        "top_p": 0.9,
    },
}
```

For powerful open-source alternatives, consider:

- [PLLaMa models](https://huggingface.co/papers/2401.01600)
- Llama 2
- Mistral
- Phi-2

Adjust the generation parameters based on your model's capabilities and your specific needs.

## Architecture Details

This project uses MCP (Machine Conversation Protocol) servers for a modular architecture:

### Weather Server

- Provides real-time weather data and forecasts
- Connects to WeatherAPI.com for data
- Exposes the `get_weather` tool via MCP
- Supports both HTTP and SSE (Server-Sent Events) transports

### Document RAG Server

- Provides Retrieval-Augmented Generation capabilities
- Uses ChromaDB as the vector store
- Searches through agricultural texts to find relevant information
- Exposes the `query_book` tool via MCP
- Supports both HTTP and SSE transports

### DSS Farmers Chatbot

- Collects input from farmers about their crops, soil, and concerns
- Fetches relevant weather and agricultural information from the MCP servers
- Generates a comprehensive prompt for the language model
- Returns personalized recommendations based on all available information

## Troubleshooting

- **Vector Database Errors**: If you encounter errors with the RAG server, ensure you've created the vector database using create_vector_db.py
- **Weather API Errors**: Verify your WeatherAPI key is correctly set in the `.env` file
- **Model Loading Errors**: For large models, ensure you have sufficient RAM and disk space
- **Server Connection Errors**: Make sure both servers are running before starting the chatbot

## Requirements

- Python 3.11+
- Sufficient RAM for running LLM models (8GB+ recommended)
- Internet connection (for weather data)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
