import streamlit as st
import difflib
import streamlit.components.v1 as components

def get_custom_css():
    """
    Returns custom CSS styles for the application.
    """
    return """
        <style>
        .drag-and-drop {
            padding: 30px;
            border: 2px dashed #cccccc;
            border-radius: 10px;
            background-color: #fafafa;
            text-align: center;
            margin-bottom: 20px;
        }
        .drag-and-drop:hover {
            border-color: #666666;
            background-color: #f0f0f0;
        }
        table.diff {
            font-family: 'Courier New', Courier, monospace;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            width: 100%;
        }
        .diff_header {
            background-color: #f0f0f0;
            padding: 5px;
            border-bottom: 1px solid #e0e0e0;
        }
        td.diff_header {
            text-align: right;
            color: #666;
        }
        .diff_next {color: #666}
        .diff_add {
            background-color: #e6ffe6;
            border: 1px solid #a6f3a6;
        }
        .diff_chg {
            background-color: #fffff0;
            border: 1px solid #f3e3a6;
        }
        .diff_sub {
            background-color: #ffe6e6;
            border: 1px solid #f3a6a6;
        }
        </style>
    """

def format_hex_data(hex_data, bytes_per_line=16):
    """
    Formats hexadecimal data into a more readable form with spaces and newlines.
    """
    formatted_lines = []
    for i in range(0, len(hex_data), bytes_per_line * 2):
        line = ' '.join(hex_data[j:j + 2] for j in range(i, min(i + bytes_per_line * 2, len(hex_data)), 2))
        formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def load_file(file):
    """
    Reads the uploaded file and returns its content.
    """
    file_bytes = file.read()
    if file.name.endswith('.bin'):
        return file_bytes.hex()
    else:
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            st.error(f"Failed to decode {file.name}. Ensure it's a UTF-8 encoded text file or a .bin file.")
            return ""

def compare_files_side_by_side(file1_data, file2_data, file1_name, file2_name):
    """
    Compares two files and returns the side-by-side HTML view of the differences.
    """
    differ = difflib.HtmlDiff(wrapcolumn=80)
    diff_table = differ.make_table(
        file1_data.splitlines(),
        file2_data.splitlines(),
        fromdesc=file1_name,
        todesc=file2_name,
        context=True,
        numlines=2
    )
    return diff_table

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
