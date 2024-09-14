# AI-RAG

![Diagram](./resources/diagram.jpg)

# PDF Processing System

This diagram illustrates the process of extracting and processing data from PDF files. The system extracts text, tables, and images, converts them into a usable format, and stores the formatted data in a VectorDB (Postgres). The system can then retrieve the data based on user prompts, process it using LLM (GPT-4o), and provide the response as an audio output via Text-to-Speech (TTS).

## Process Overview:

1. **PDF**:
   - The PDF file serves as the input source containing the data to be processed.

2. **Data Extraction**:
   - The system extracts three types of data from the PDF:
     - **Text**: The textual content extracted from the PDF.
     - **Tables**: Extracted tables are converted into images for further processing.
     - **Images**: Pictures directly extracted from the PDF.

3. **Convert to Image**:
   - Extracted tables are converted into images for further processing.

4. **Image2Text by Prompt**:
   - Both tables (converted into images) and extracted pictures are converted into text using image-to-text conversion, facilitated by prompts to ensure accuracy.

5. **Formatted Text Document**:
   - The extracted and processed content is then formatted into a structured document.

6. **VectorDB (Postgres)**:
   - The formatted document is stored in a VectorDB (Postgres) for easy retrieval and further analysis.

7. **User Prompt**:
   - The user interacts with the system by providing a prompt, typically a question or request for information.

8. **Pre-Prompt**:
   - The user’s prompt is pre-processed or refined before the data retrieval stage.

9. **Retriever**:
   - The retriever searches for relevant information from the VectorDB using the pre-processed prompt and forwards the results to the LLM (GPT-4).

10. **LLM (GPT-4)**:
    - GPT-4 processes the retrieved data and generates a response based on the user’s prompt.

11. **TTS (Text-to-Speech)**:
    - The generated response is then converted into audio using a Text-to-Speech (TTS) system.

12. **Output (Audio)**:
    - The system provides the response back to the user in the form of an audio output.

## Summary:
This system efficiently processes data from PDF files, extracting key content for analysis. Through the use of LLM (GPT-4o) and TTS, it delivers responses to user queries in audio format.

# Requirements
1) Docker
2) Conda
3) llm model in model/

# Get-Start
1) clone repo
2) install torch: https://pytorch.org/get-started/locally/
3) pip install -r requirements.txt

# Full-Tutorial by @lunaxoniichan
Summarize: https://www.youtube.com/watch?v=_K0lRd-4LpM&t=1s

How to Get-Start: https://www.youtube.com/live/z5kH4tCDgMA?si=yOyzSHH3MCXqaLge

# VectorDB (Postgres)
## How to use
1) docker-compose up -d
2) docker exec -it vector_store psql -U admin -d vector_store

## Commands
Show databases: 
> \d

# Chatbot UI
RUN
> chainlit run chatbot.py -w