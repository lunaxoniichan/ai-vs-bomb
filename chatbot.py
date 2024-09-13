from langchain import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import chainlit as cl
import re
from common.file_helper import FileHelper
from common.constant import *
from dotenv import dotenv_values

config = dotenv_values(".env")

# load model configs

model_configs = FileHelper.read_json(PATH_MODEL_CONFIGS)
custom_prompt_template = FileHelper.read_txt(PATH_MODEL_PROMPT)

MODEL = "OpenAI"

def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt


# get the chain
def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type=model_configs["RetrievalChain"]["chain_type"],
                                           retriever=db.as_retriever(search_type=model_configs["RetrievalChain"]["search_type"],
                                                                     search_kwargs=model_configs["RetrievalChain"]["search_kwargs"]),
                                           return_source_documents=True,
                                           chain_type_kwargs={'prompt': prompt}
                                           )
    return qa_chain


# load the model
def load_llm():
    if MODEL == "OpenAI":
        llm = OpenAI(temperature=model_configs["llm"]["temperature"], api_key=config["OPENAI_API_KEY"])
        print(llm)
    else:
        llm = CTransformers(model=model_configs["llm"]["model"],
                            model_type=model_configs["llm"]["model_type"],
                            return_full_text=False,
                            num_return_sequences=1,
                            # eos_token_id=tokenizer.eos_token_id,
                            # logits_processor=LogitsProcessorList,
                            repetition_penalty=1.15,
                            max_length=4096,
                            max_new_tokens=model_configs["llm"]["max_new_tokens"],
                            temperature=model_configs["llm"]["temperature"])
    return llm


# qa model function
def qa_bot():
    embeddings = HuggingFaceEmbeddings(model_name=model_configs["embedding"]["model"],
                                       model_kwargs=model_configs["embedding"]["model_kwargs"])  # cpu, mps
    db = PGVector(collection_name=COLLECTION_NAME,
                  embedding_function=embeddings,
                  connection_string=CONNECTION_STRING)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)

    return qa


# op
def final_result(query):
    qa_result = qa_bot()
    response = qa_result({'query': query})
    return response


# chainlit framework code
@cl.on_chat_start
async def start():
    chain = qa_bot()
    msg = cl.Message(content='Starting the bot..')
    await msg.send()
    msg.content = "Welcome to Luna-chan UI"
    await msg.update()

    cl.user_session.set('chain', chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get('chain')
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=False,
        answer_prefix_tokens=['FINAL', 'ANSWER']
    )
    cb.answer_reached = True
    res = await chain.acall(message.content, callbacks=[cb])
    docs = res["source_documents"]
    print(docs)
    answer = ""
    if docs:
        answer += f"{res['result']}\n# REFERENCES #\n"
        ref = set()
        for i in range(len(docs)-1, -1, -1):
            ref_page = str(re.findall(r'\d+', docs[i].metadata["source"])[-1])
            if ref_page not in ref:
                answer += f"{str(ref_page)}\n"
                ref.add(ref_page)
    else:
        answer += "Sorry, I have no knowledge about this 😕"

    await cl.Message(content=answer).send()

#  chainlit run chatbot.py -w