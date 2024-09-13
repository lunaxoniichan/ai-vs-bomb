from enum import Enum
import os
from langchain_community.vectorstores import PGVector


class Source(Enum):
    PDF = "pdf"


class Status(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


collection_names = {
    Source.PDF.value: "pdfs",
}


# DATA - CONFIG PATH
PATH_MODEL_CONFIGS = "configs/config.json"
PATH_MODEL_PROMPT = "configs/prompt.txt"
DIR_DATA_ETC = "docs/bomb"

# EMBEDDING
COLLECTION_NAME = "bomb"
CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
    host=os.environ.get("PGVECTOR_HOST", "localhost"),
    port=int(os.environ.get("PGVECTOR_PORT", "5432")),
    database=os.environ.get("PGVECTOR_DATABASE", "vector_store"),
    user=os.environ.get("PGVECTOR_USER", "admin"),
    password=os.environ.get("PGVECTOR_PASSWORD", "admin"),
)
