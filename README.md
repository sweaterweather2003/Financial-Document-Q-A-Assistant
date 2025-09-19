# Financial-Document-Q-A-Assistant
A web application that can process financial documents (PDF and Excel formats) and provide an interactive question-answering system for users to query financial data using natural language.

## Key features:
- Document Processing: Handles PDF and Excel files, extracts text and tables using `pdfplumber` for PDFs and `pandas` for Excel.
- Data Cleaning: Cleans extracted data by handling encoding issues (e.g., replacing '�' with '$'), removing duplicates, and dropping empty rows/columns.
- Q&A System: Uses Ollama with a local model (llama3.1:8b) for conversational responses based on the document context.
- User Interface: Intuitive Streamlit-based UI with file uploader, extracted content display, chat interface, and an "Add More Documents" checkbox that appears after each Q&A     for expanding the context.
- Conversational Support: Maintains chat history and allows follow-up questions.
- Error Handling: Provides feedback for unsupported files, processing errors, and LLM response issues.

## Requirements:
- Python 3.8+
- Ollama installed and running locally (download from https://ollama.com)
- A compatible LLM model pulled via Ollama ( ollama pull llama3.1:8b)

## Installation:
1. Clone the repository: git clone https://github.com/sweaterweather2003/Financial-Document-Q-A-Assistant.git
                         cd Financial-Document-Q-A-Assistant
   (use your own username in place of sweaterweather2003 which is my username)
   
2. Install dependencies:  python -m venv venv source venv/bin/activate (set up environment on system)
                          pip install -r requirements.txt

3. Set up Ollama: Download Ollama from https://ollama.com
                           ollama pull llama3.1:8b

## Usage
1. Run the app:
    streamlit run app.py
   This will open the app in your browser (default: http://localhost:8501).

3. Upload Documents:
- Use the file uploader to select one or more PDF/Excel files (financial statements like Apple's or Samsung's, they're the document's I have used to try).
- The app processes the files, displays extracted text and tables, and builds a combined context for Q&A, after cleaning the tables to remove any empty rows and columns.

3. Add More Documents:
- After processing, an "Add More Documents" checkbox appears.
- Check it to upload additional files, which append to the existing context.
- Uncheck to proceed to Q&A.
- The checkbox reappears below each assistant response in the chat for ongoing additions.

4. Ask Questions:
- Use the chat input to query the documents ("What was Apple's net sales in FY23?" or "Compare Samsung's total assets from 2023 to 2024").
- Responses are generated based on the extracted context.
- Follow ups are supported via chat history.

NOTE: Supported File Types: .pdf, .xlsx, .xls

## Troubleshooting
- Model Not Found: Ensure the model is pulled (e.g., `ollama list`) and matches the code (default: 'llama3.1:8b'). Run `ollama pull llama3.1:8b` if missing.
- Ollama Errors: Verify Ollama is running on http://localhost:11434 (check with `ollama serve`).
- Extraction Issues: For poor PDF tables, increase `snap_tolerance` in `extract_from_pdf` or switch to camelot-py (`pip install camelot-py[base]`).
- App Crashes: Check dependency versions or increase upload size with `--server.maxUploadSize=500`.

## Repository Structure
- `app.py`: Main application script.
- `requirements.txt`: List of dependencies.
- `venv`: The system environment


   
