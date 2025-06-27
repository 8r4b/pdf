import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from htmlTemplates import css, bot_template, user_template

import fitz  # PyMuPDF
from PIL import Image
import io
import pytesseract


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_bytes = pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()

            if page_text.strip():
                text += page_text + "\n"
            else:
                # No text found, render page as image and OCR it
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text + "\n"

        pdf.seek(0)  # Reset stream if needed
    return text


def get_pdf_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with PDFs", page_icon=":books:")

    # Initialize session state keys
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with Multiple PDFs")

    with st.sidebar:
        st.subheader("Upload your PDF files")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'",
            accept_multiple_files=True,
            type=['pdf']
        )

        if st.button("Process"):
            if pdf_docs:
                with st.spinner("Processing your PDFs..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_pdf_chunks(raw_text)
                    vectorstore = get_vectorstore(text_chunks)
                    st.session_state.conversation = get_conversation_chain(vectorstore)
                    st.success("PDFs processed successfully. You can now chat below!")

    if st.session_state.conversation:
        with st.form(key="question_form", clear_on_submit=True):
            user_question = st.text_input("Ask a question about your documents:")
            submit = st.form_submit_button("Send")

        if submit and user_question:
            handle_userinput(user_question)


if __name__ == "__main__":
    main()
