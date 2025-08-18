import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector-db-creator")


def determine_loader(file_path):
    """Determine the appropriate loader based on file extension"""
    if file_path.endswith(".txt"):
        return TextLoader(file_path)
    elif file_path.endswith(".pdf"):
        return PyPDFLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")


def create_vector_database(resources_dir, db_path):
    """
    Process all book files in resources_dir and create a single vector database
    """
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name="book_collection", embedding_function=embedding_function
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    book_files = list(Path(resources_dir).glob("*.pdf")) + list(
        Path(resources_dir).glob("*.txt")
    )
    logger.info(f"Found {len(book_files)} book files in {resources_dir}")

    doc_counter = 0
    for book_path in book_files:
        logger.info(f"Processing {book_path}")
        loader = determine_loader(str(book_path))
        documents = loader.load()
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Adding {len(chunks)} chunks from {book_path.name}")
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk.page_content],
                metadatas=[{"source": book_path.name}],
                ids=[f"{book_path.stem}_doc_{doc_counter}_{i}"],
            )
        doc_counter += 1

    logger.info("Vector database creation complete")
    return True


if __name__ == "__main__":
    resources_dir = Path(__file__).parents[2] / "dss_farmers/resources"
    db_path = resources_dir / "vectordb"
    create_vector_database(str(resources_dir), str(db_path))
