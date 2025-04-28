import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import chardet  # For smart encoding detection

# 1. Streamlit page config
st.set_page_config(layout='wide')

# 2. Custom background CSS
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 25%, #fbc2eb 50%, #a18cd1 75%, #fbc2eb 100%);
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Load environment variables
load_dotenv()

# 4. Chat with CSV function
def chat_with_csv(df, query):
    groq_api_key = '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'  # Directly updated API key

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-70b-8192",
        temperature=0.2
    )

    pandas_ai = SmartDataframe(df, config={"llm": llm})

    result = pandas_ai.chat(query)
    return result

# 5. Streamlit app layout
st.title("🌈 LLM-Powered CSV Chatbot:  Chat with CSVs, Explorer & Visualize")

# 6. Upload CSV files
input_csvs = st.sidebar.file_uploader("Upload your CSV files", type=['csv'], accept_multiple_files=True)

# 7. If files uploaded
if input_csvs:
    selected_file = st.selectbox("Select a CSV file", [file.name for file in input_csvs])
    selected_index = [file.name for file in input_csvs].index(selected_file)
    uploaded_file = input_csvs[selected_index]

    try:
        preview_bytes = uploaded_file.read(4096)  
        detected = chardet.detect(preview_bytes)
        encoding_used = detected['encoding'] if detected['encoding'] else 'utf-8'

        preview_text = preview_bytes.decode(encoding_used, errors='ignore')

        if '\t' in preview_text:
            sep_used = '\t'
        elif ';' in preview_text:
            sep_used = ';'
        else:
            sep_used = ','

        uploaded_file.seek(0)

        data = pd.read_csv(uploaded_file, encoding=encoding_used, sep=sep_used, engine='python')

        st.success(f"CSV loaded successfully! (Encoding: {encoding_used}, Separator: '{sep_used}')")
        st.dataframe(data.head(3), use_container_width=True)

        # Chat input
        st.info("Chat Below 👇")
        input_text = st.text_area("Enter your query:")

        if input_text and st.button("Chat with CSV"):
            st.info(f"Your Query: {input_text}")
            try:
                result = chat_with_csv(data, input_text)
                st.success(result)
            except Exception as chat_error:
                st.error(f"Error during chat: {chat_error}")

        # 📊 Dynamic Plotting Section
        st.subheader("📊 Auto-Generated Plots")

        numerical_cols = data.select_dtypes(include='number').columns.tolist()
        categorical_cols = data.select_dtypes(include='object').columns.tolist()

        if len(numerical_cols) >= 2:
            st.write("▶️ Seaborn Pairplot (First few numeric columns):")
            try:
                sns.pairplot(data[numerical_cols[:5]])
                st.pyplot()
            except Exception as e:
                st.error(f"Error in Pairplot: {e}")

            st.write("▶️ Plotly Scatter Plot:")
            fig = px.scatter(data, x=numerical_cols[0], y=numerical_cols[1], title=f"{numerical_cols[0]} vs {numerical_cols[1]}")
            st.plotly_chart(fig)

        if len(numerical_cols) >= 1:
            st.write("▶️ Histogram (First Numeric Column):")
            fig = px.histogram(data, x=numerical_cols[0], title=f"Distribution of {numerical_cols[0]}")
            st.plotly_chart(fig)

            st.write("▶️ Correlation Heatmap:")
            corr = data[numerical_cols].corr()
            fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
            st.plotly_chart(fig)

        if len(categorical_cols) >= 1:
            st.write("▶️ Bar Chart (First Categorical Column):")
            try:
                fig = px.bar(data[categorical_cols[0]].value_counts().reset_index(),
                             x='index', y=categorical_cols[0],
                             title=f"Count of {categorical_cols[0]}")
                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"Error in Bar chart: {e}")

            if len(numerical_cols) >= 1:
                st.write("▶️ Altair Box Plot (First Categorical vs First Numeric):")
                chart = alt.Chart(data).mark_boxplot().encode(
                    x=alt.X(categorical_cols[0], type='nominal'),
                    y=alt.Y(numerical_cols[0], type='quantitative')
                ).properties(title=f"{numerical_cols[0]} by {categorical_cols[0]}")
                st.altair_chart(chart, use_container_width=True)

        if len(numerical_cols) >= 3:
            st.write("▶️ 3D Scatter Plot (First 3 numeric columns):")
            fig = px.scatter_3d(data, x=numerical_cols[0], y=numerical_cols[1], z=numerical_cols[2],
                                color=numerical_cols[0], title=f"3D plot: {numerical_cols[0]}, {numerical_cols[1]}, {numerical_cols[2]}")
            st.plotly_chart(fig)

    except Exception as e:
        st.error(f"⚠️ Error loading CSV: {e}")