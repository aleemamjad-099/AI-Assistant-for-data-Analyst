import streamlit as st
import pandas as pd
from groq import Groq
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv # Naya import
import os

# .env file se variables load karein
load_dotenv()

# API Key ab environment se uhtayi jayegi
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Baqi sara code waisa hi rahega...

st.set_page_config(page_title="AI Data Analyst Pro", layout="wide", page_icon="📊")

st.title("📊 AI Data Analyst Assistant")

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None

# --- Sidebar: File Upload & Cleaning ---
with st.sidebar:
    st.header("📂 Data Hub")
    uploaded_file = st.file_uploader("Upload Data (CSV, Excel, JSON)", type=["csv", "xlsx", "json"])
    
    if uploaded_file:
        file_ext = uploaded_file.name.split(".")[-1]
        if st.session_state.df is None: # Sirf pehli baar load karne ke liye
            if file_ext == "csv":
                st.session_state.df = pd.read_csv(uploaded_file)
            elif file_ext == "xlsx":
                st.session_state.df = pd.read_excel(uploaded_file)
            elif file_ext == "json":
                st.session_state.df = pd.read_json(uploaded_file)
            st.success("File Loaded!")

    # Data Cleaning Options
    if st.session_state.df is not None:
        st.divider()
        st.subheader("🛠️ Data Cleaning")
        
        if st.button("Remove Duplicates"):
            old_len = len(st.session_state.df)
            st.session_state.df = st.session_state.df.drop_duplicates()
            st.warning(f"Removed {old_len - len(st.session_state.df)} duplicates!")

        if st.button("Fill Missing Values"):
            st.session_state.df = st.session_state.df.fillna(0)
            st.info("All missing values filled with 0.")

# --- Main Dashboard ---
if st.session_state.df is not None:
    df = st.session_state.df

    # 1. Data Summary Detail Cards
    st.subheader("📋 Data Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Duplicates", df.duplicated().sum())
    col4.metric("Missing Values", df.isnull().sum().sum())

    # 2. Data Preview (First 5 records)
    with st.expander("👀 View Data Preview (First 5 Rows)", expanded=True):
        st.dataframe(df.head(), use_container_width=True)

    st.divider()

    # 3. AI Chat Interface
    st.subheader("🤖 Ask Anything About Your Data")
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if user_query := st.chat_input("E.g.,'Give me summary statistics'"):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("AI analyzing..."):
                prompt = f"""
                You are a Data Scientist. DataFrame name is 'df'.
                Columns: {list(df.columns)}
                
                Task: Write Python code for: "{user_query}"
                Rules:
                1. Store text results in 'final_result'.
                2. Use 'st.pyplot(plt)' for graphs. 
                3. Only give Python code, no text.
                """

                try:
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    
                    clean_code = completion.choices[0].message.content.replace("```python", "").replace("```", "").strip()
                    
                    local_vars = {"df": df, "plt": plt, "sns": sns, "st": st}
                    exec(clean_code, {}, local_vars)

                    if "final_result" in local_vars:
                        res_text = str(local_vars["final_result"])
                        st.write(res_text)
                        st.session_state.messages.append({"role": "assistant", "content": res_text})
                
                except Exception as e:
                    st.error(f"Error: {e}")

else:
    st.info("👈 Sidebar se data file upload karein takay hum analysis shuru kar sakein!")