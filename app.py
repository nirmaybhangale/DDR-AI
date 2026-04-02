import streamlit as st
from pipeline import run_pipeline
import os

st.set_page_config(page_title="AI Report Generator", layout="centered")

st.title("DDR Generator")

with st.sidebar:
    st.header("Upload Files")
    insp = st.file_uploader("Inspection PDF", type="pdf")
    ther = st.file_uploader("Thermal PDF", type="pdf")

if st.button("🚀 Generate Detailed Diagnosis Report"):
    if insp and ther:
        # Save temp files for processing
        with open("temp_insp.pdf", "wb") as f: f.write(insp.getbuffer())
        with open("temp_ther.pdf", "wb") as f: f.write(ther.getbuffer())

        with st.spinner("Analyzing documents and generating a detailed report..."):
            report_md = run_pipeline("temp_insp.pdf", "temp_ther.pdf")

        st.success("DDR Generated Successfully!")

        #DOWNLOAD BUTTON
        st.download_button(
            label="📥 Download Markdown (Raw)",
            data=report_md,
            file_name="DDR.md",
            mime="text/markdown"
        )

        st.divider()
        st.header("📋 Report Preview")
        st.markdown(report_md)
        
        # Cleanup temp files
        if os.path.exists("temp_insp.pdf"): os.remove("temp_insp.pdf")
        if os.path.exists("temp_ther.pdf"): os.remove("temp_ther.pdf")