import streamlit as st
import streamlit.components.v1 as components
from utils import load_file, format_hex_data, compare_files_side_by_side
from styles import get_custom_css

def display_content(content, file_name=None):
    """
    Displays content with appropriate formatting based on file type.
    """
    if file_name and file_name.endswith('.py'):
        st.code(content, language='python')
    else:
        st.text(content)

def main():
    st.set_page_config(page_title="File Comparison Tool", layout="wide")
    st.title("📄 File Comparison Tool")
    
    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Upload Files", "Paste Text"],
        horizontal=True
    )

    if input_method == "Upload Files":
        uploaded_files = st.file_uploader(
            "Drag and drop files here or click to select",
            type=["c", "h", "cpp", "txt", "bin", "py"],
            accept_multiple_files=True,
            help="Supported file types: .c, .h, .cpp, .txt, .bin, .py"
        )

        if uploaded_files:
            if len(uploaded_files) == 1:
                file = uploaded_files[0]
                file_data = load_file(file)
                if file.name.endswith('.bin'):
                    file_data = format_hex_data(file_data)
                st.subheader(f"📄 Content of `{file.name}`:")
                display_content(file_data, file.name)

            elif len(uploaded_files) == 2:
                file1, file2 = uploaded_files
                file1_data = load_file(file1)
                file2_data = load_file(file2)

                if file1.name.endswith('.bin'):
                    file1_data = format_hex_data(file1_data)
                if file2.name.endswith('.bin'):
                    file2_data = format_hex_data(file2_data)

                st.subheader(f"🔍 Comparing `{file1.name}` and `{file2.name}`:")
                if file1_data and file2_data:
                    diff_html = compare_files_side_by_side(
                        file1_data,
                        file2_data,
                        file1.name,
                        file2.name
                    )
                    components.html(diff_html, height=800, scrolling=True)
                else:
                    st.error("One or both files could not be read. Please ensure they are valid and try again.")

            else:
                st.warning("⚠️ Please upload no more than two files for comparison.")

    else:  # Paste Text
        col1, col2 = st.columns(2)
        
        with col1:
            text1 = st.text_area("First text content", height=300, placeholder="Paste your first text here...")
            name1 = st.text_input("First text name (optional)", "Text 1")

        with col2:
            text2 = st.text_area("Second text content", height=300, placeholder="Paste your second text here...")
            name2 = st.text_input("Second text name (optional)", "Text 2")

        if text1 or text2:
            if text1 and not text2:
                st.subheader(f"📄 Content of `{name1}`:")
                display_content(text1)
            elif text1 and text2:
                st.subheader(f"🔍 Comparing `{name1}` and `{name2}`:")
                diff_html = compare_files_side_by_side(text1, text2, name1, name2)
                components.html(diff_html, height=800, scrolling=True)

    # Usage instructions
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Choose your input method**:
           - Upload Files: Compare files by uploading them
           - Paste Text: Compare text by pasting it directly

        2. **For file upload**:
           - Drag and drop files into the upload area
           - Click to select files from your system
           - Supported types: .py, .c, .cpp, .h, .txt, .bin

        3. **For text paste**:
           - Paste your text directly into the text areas
           - Optionally provide names for your text content

        4. **Compare**:
           - Upload/paste one item to view its contents
           - Upload/paste two items to see a side-by-side comparison
        """)

if __name__ == "__main__":
    main()
