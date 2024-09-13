from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from common.constant import *
import re
import json


def load_documents(path):
    loader = DirectoryLoader(path, glob='*.txt', loader_cls=TextLoader)
    docs_loader = loader.load()
    text_spitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                  chunk_overlap=50)
    return text_spitter.split_documents(documents=docs_loader)


def load_embedding_model():
    """create embeddings & store in vector db"""
    with open("configs/config.json") as f:
        model_configs = json.load(f)
    return HuggingFaceEmbeddings(model_name=model_configs["embedding"]["model"],
                                 model_kwargs=model_configs["embedding"]["model_kwargs"])


def update_docs(embeddings, collection_name, connection_string, ids, pre_delete_collection=False, docs=None):
    pgv = PGVector(embedding_function=embeddings, connection_string=connection_string, collection_name=COLLECTION_NAME)
    pgv.delete(ids)
    if docs:
        db = PGVector.from_documents(
            embedding=embeddings,
            documents=docs,
            collection_name=collection_name,
            connection_string=connection_string,
            pre_delete_collection=pre_delete_collection,
            ids=ids
        )
        return db


def update_vector_store(embeddings, collection_name, connection_string, insert_update_ids, delete_ids,
                        insert_update_texts, insert_update_metadata):
    pgv = PGVector(
        embedding_function=embeddings,
        connection_string=connection_string,
        collection_name=collection_name,
    )

    pgv.delete(insert_update_ids + delete_ids)
    pgv.add_texts(
        texts=insert_update_texts,
        metadatas=insert_update_metadata,
        ids=insert_update_ids,
    )
    return pgv


if __name__ == '__main__':
    # todo: modify this to scope files
    get_messages = {
        "non-delete": {"5", "6", "11"},  # To create-update related file in vectorDB
        "delete": {}  # To delete related file from vectorDB
    }

    # text2vec
    texts = load_documents(path=DIR_DATA_ETC)
    non_delete_ids = []
    insert_update_ids = []
    insert_update_texts = []
    insert_update_metadata = []
    delete_ids = []
    for doc in texts:
        pageId = str(re.findall(r'\d+', doc.metadata["source"])[-1])
        page_content = doc.page_content
        if (pageId in get_messages["non-delete"]) or ("all" in get_messages["non-delete"]):
            non_delete_ids.append(pageId)
            insert_update_ids.append(pageId)
            insert_update_texts.append(doc.page_content)
            insert_update_metadata.append(doc.metadata)
        elif pageId in get_messages["delete"]:
            delete_ids.append(pageId)
        else:
            pass  # no update / delete

    embeddings = load_embedding_model()
    # add & update docs vector
    pgv_db = update_vector_store(embeddings, COLLECTION_NAME, CONNECTION_STRING,
                                 insert_update_ids=insert_update_ids,
                                 delete_ids=delete_ids,
                                 insert_update_texts=insert_update_texts,
                                 insert_update_metadata=insert_update_metadata
                                 )
    pgv_db.documents = insert_update_texts
    # >>> for tuning threshold
    query = "There have 3 wires. The last wire is white. What should I do ?"
    docs_with_score = pgv_db.similarity_search_with_relevance_scores(query, k=2)
    print(query)
    for doc, score in docs_with_score:
        print("-" * 80)
        print("Score: ", score)
        print(doc.page_content)
        print("-" * 80)

