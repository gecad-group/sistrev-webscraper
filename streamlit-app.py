import logging
from io import StringIO
import streamlit as st
import datacleaner as dc

st.title("SistRev's Data Cleaner")
st.write("This is a simple data cleaner for bibliographic data in RIS format. Upload your RIS files and download a clean version.")

st.header("File Upload")
files = st.file_uploader("Upload your RIS file(s)", type=["ris"], accept_multiple_files=True)

# Create a StringIO based logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_stream = StringIO()
stream_handler = logging.StreamHandler(log_stream)
logger.addHandler(stream_handler)
logger.info("This is running in the Web Version of the Data Cleaner")

if files:
    st.subheader("Cleaner")
    cleaner = dc.DataCleaner(logger)
    for file in files:
        stringio = StringIO(file.read().decode("utf-8"))
        cleaner.add_file(stringio)

    st.write(f"Total entries: {cleaner.count_in_entries()}")

    if st.button("Clean Data"):
        with st.spinner("Cleaning Data..."):
            n_dup, n_no_title, n_no_abst, n_no_doi = cleaner.clean_entries()
            clean = cleaner.count_out_entries()
            st.success("Data cleaned!")

        st.write(f"Number of duplicated entries: {n_dup}")
        st.write(f"Number of entries without title: {n_no_title}")
        st.write(f"Number of entries without abstract: {n_no_abst}")
        st.write(f"Number of entries without doi: {n_no_doi}")
        st.write(f"Number of entries after cleanup: {clean}")

        st.subheader("Download Cleaned Data")
        cleaned_data = StringIO()
        cleaner.export_data_tofile(cleaned_data)
        cleaned_data.seek(0)
        st.download_button(
            label="Download Cleaned Data",
            data=cleaned_data.read().encode("utf-8"),
            file_name="cleaned_data.ris",
            mime="text/plain"
        )

        stream_handler.flush()
        log_stream.seek(0)
        st.download_button(
            label="Download Log",
            data=log_stream.read().encode("utf-8"),
            file_name="datacleaner.log",
            mime="text/plain"
        )





