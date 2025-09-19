import streamlit as st
import pandas as pd
import pdfplumber
from ollama import Client
import io

ollama_client = Client(host='http://localhost:11434')  

def extract_from_pdf(file):
    text = ""
    tables = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n\n"
            page_tables = page.extract_tables(table_settings={
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 5,  
                "intersection_tolerance": 2
            })
            for table in page_tables:
                cleaned_table = [[cell.strip().replace('�', '$').replace('!', '') if cell else '' for cell in row] for row in table]
                cleaned_table = [row for row in cleaned_table if any(row)]
                if not cleaned_table:
                    continue
                headers = cleaned_table[0]
                data = cleaned_table[1:]
                unique_headers = []
                count = {}
                for h in headers:
                    h_clean = h.strip()
                    if not h_clean:
                        h_clean = 'Unnamed'
                    if h_clean in count:
                        count[h_clean] += 1
                        unique_headers.append(f"{h_clean}_{count[h_clean]}")
                    else:
                        count[h_clean] = 0
                        unique_headers.append(h_clean)
                df = pd.DataFrame(data, columns=unique_headers)
                for col in df.columns:
                    df[col] = df[col].str.strip().str.replace('�', '$').str.replace('!', '')
                df = df.dropna(axis=1, how='all')
                df = df.dropna(how='all')
                tables.append(df)
    text = text.replace('�', '$').replace('!', '')
    return text, tables

def extract_from_excel(file):
    text = ""
    tables = []
    xls = pd.ExcelFile(file)
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        text += df.to_string() + "\n\n"
        tables.append(df)
    return text, tables

def query_llm(prompt, model='llama3.1:8b'):
    response = ollama_client.generate(model=model, prompt=prompt)
    return response['response']

st.title("Financial Document Q&A Assistant")

if "all_extracted_text" not in st.session_state:
    st.session_state.all_extracted_text = ""
if "all_extracted_tables" not in st.session_state:
    st.session_state.all_extracted_tables = []
if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False

uploaded_files = st.file_uploader("Upload financial documents (PDF or Excel)", type=['pdf', 'xlsx', 'xls'], accept_multiple_files=True)

if uploaded_files:
    try:
        st.write("Processing documents...")
        new_text = ""
        new_tables = []
        for uploaded_file in uploaded_files:
            file_type = uploaded_file.name.split('.')[-1].lower()
            st.write(f"Processing {uploaded_file.name}...")
            
            if file_type == 'pdf':
                file_bytes = io.BytesIO(uploaded_file.read())
                extracted_text, extracted_tables = extract_from_pdf(file_bytes)
            elif file_type in ['xlsx', 'xls']:
                file_bytes = io.BytesIO(uploaded_file.read())
                extracted_text, extracted_tables = extract_from_excel(file_bytes)
            else:
                st.warning(f"Unsupported file type for {uploaded_file.name}. Skipping.")
                continue
            
            new_text += f"\n\n--- Content from {uploaded_file.name} ---\n\n" + extracted_text
            new_tables.extend(extracted_tables)
            
            st.subheader(f"Extracted from {uploaded_file.name}")
            st.text_area("Text content", extracted_text, height=200)
            
            if extracted_tables:
                for i, df in enumerate(extracted_tables):
                    st.write(f"Table {i+1}")
                    st.dataframe(df)
            else:
                st.info("No tables extracted from this file.")
        
        if st.session_state.documents_processed:
            st.session_state.all_extracted_text += new_text
            st.session_state.all_extracted_tables.extend(new_tables)
        else:
            st.session_state.all_extracted_text = new_text
            st.session_state.all_extracted_tables = new_tables
            st.session_state.documents_processed = True
        
        context = st.session_state.all_extracted_text
        for df in st.session_state.all_extracted_tables:
            context += "\n" + df.to_csv(index=False)
        
        st.success("Documents processed successfully! Context now includes all uploaded files.")
        
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")
        st.stop()

    if st.session_state.documents_processed:
        st.subheader("Ask questions about the documents")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    add_more = st.checkbox("Upload additional documents to expand the context?", key=f"add_more_{len(st.session_state.messages)}")
                    if add_more:
                        st.session_state.clear()  
                        st.rerun()

        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    full_prompt = f"Context from financial documents:\n{context}\n\nUser question: {prompt}\n\nAnswer based on the context:"
                    try:
                        response = query_llm(full_prompt)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        add_more = st.checkbox("Upload additional documents to expand the context?", key=f"add_more_{len(st.session_state.messages)}")
                        if add_more:
                            st.session_state.clear()  
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")

else:
    st.info("Please upload one or more documents to begin.")
