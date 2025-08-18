import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
import chromadb
from chromadb.utils import embedding_functions

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("book-rag-app")

# Initialize MCP
mcp = FastMCP("book-rag-app", host="127.0.0.1", port=8001)

# Path to the vector database
resources_dir = Path(__file__).parents[2] / "dss_farmers/resources"
db_path = resources_dir / "vectordb"

# Initialize ChromaDB client and collection
client = chromadb.PersistentClient(path=str(db_path))
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.get_collection(
    name="book_collection", embedding_function=embedding_function
)


@mcp.tool()
def query_book(query: str, top_k: int = 3) -> dict:
    """
    Query the book for information relevant to the farmer's question.

    Args:
        query: The farmer's question or query
        top_k: Number of most relevant passages to return

    Returns:
        Dictionary containing relevant passages from the book
    """
    if not query:
        logger.error("Query parameter is required.")
        return {"error": "Query parameter is required"}

    try:
        # Query the vector database
        results = collection.query(query_texts=[query], n_results=top_k)

        # Format the results
        passages = results.get("documents", [[]])[0]
        metadata = results.get("metadatas", [[]])[0]

        response = {
            "query": query,
            "matches": [
                {"text": passages[i], "source": metadata[i].get("source", "unknown")}
                for i in range(len(passages))
            ],
        }

        return response
    except Exception as e:
        logger.error(f"Error querying vector database: {e}")
        return {"error": f"Failed to query the book: {str(e)}"}


# Set up the SSE transport for MCP communication
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request) -> None:
    """Handle SSE connections from clients"""
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(reader, writer, _server.create_initialization_options())


# Create the Starlette app with multiple endpoints
app = Starlette(
    debug=True,
    routes=[
        # SSE endpoint for clients that use SSE transport
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
        # The regular MCP endpoint remains at /mcp
        # This is handled internally by FastMCP
    ],
)


if __name__ == "__main__":
    # Make sure the database exists
    if not db_path.exists():
        logger.error(
            f"Vector database not found at {db_path}. Please run create_vectordb.py first."
        )
        exit(1)

    # Get port from environment variable or use default
    port = int(os.getenv("PORT", "8001"))
    logger.info(f"Starting RAG server with database at {db_path} on port {port}")

    # Run the app with uvicorn instead of using mcp.run()
    uvicorn.run(app, host="127.0.0.1", port=port)
