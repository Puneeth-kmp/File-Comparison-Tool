import streamlit as st
import difflib
import streamlit.components.v1 as components
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
from typing import Optional

# Function to load an image from GitHub repository
def load_github_image(url: str) -> Optional[Image.Image]:
    """
    Load an image from a GitHub repository
    """
    try:
        # Convert GitHub blob URL to raw content URL
        raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        response = requests.get(raw_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")
        return None

# Function to load file content
def load_file(file):
    return file.getvalue().decode("utf-8")

# Function to format binary data (for '.bin' files)
def format_hex_data(data):
    return '\n'.join([f"{i:08x}: {data[i:i+16].hex()}" for i in range(0, len(data), 16)])

# Function to create a custom side-by-side diff view
def generate_side_by_side_diff(file1_data, file2_data):
    file1_lines = file1_data.splitlines()
    file2_lines = file2_data.splitlines()
    
    # Generate side-by-side comparison using difflib
    diff = difflib.ndiff(file1_lines, file2_lines)
    
    # HTML style and layout setup for side-by-side display
    html_content = """
    <style>
        .diff-table { width: 100%; border-collapse: collapse; }
        .diff-table td { padding: 5px; vertical-align: top; font-family: monospace; }
        .line-num { width: 5%; background-color: #f0f0f0; text-align: right; padding-right: 10px; }
        .added { background-color: #e8f5e9; }
        .removed { background-color: #ffebee; }
        .modified { background-color: #fff3e0; }
    </style>
    <table class="diff-table">
        <tr>
            <th>File 1</th>
            <th>File 2</th>
        </tr>
    """

    for line in diff:
        tag = line[:2]
        content = line[2:]

        if tag == "  ":  # No change
            html_content += f"<tr><td>{content}</td><td>{content}</td></tr>"
        elif tag == "- ":  # Line removed from file1
            html_content += f"<tr><td class='removed'>{content}</td><td></td></tr>"
        elif tag == "+ ":  # Line added in file2
            html_content += f"<tr><td></td><td class='added'>{content}</td></tr>"
        elif tag == "? ":  # Line modified
            html_content += f"<tr><td class='modified'>{content}</td><td class='modified'>{content}</td></tr>"

    html_content += "</table>"
    return html_content

# Main app function
def main():
    st.set_page_config(
        page_title="Professional File Comparison Tool",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize the tool
    st.title("📄 File Comparison Tool")

    # Custom CSS for better UI
    st.markdown("""
        <style>
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
            }
            .main {
                padding: 2rem;
            }
            .uploadedFile {
                border: 1px solid #ddd;
                padding: 1rem;
                border-radius: 5px;
            }
            .logo-container {
                display: flex;
                align-items: center;
                margin-bottom: 1rem;
            }
            .logo-container img {
                margin-right: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header with logo
    col1, col2 = st.columns([3, 1])
    with col1:
        logo_url = "https://github.com/Puneeth-kmp/File-Comparison-Tool/blob/main/Picsart_24-11-10_15-02-57-542.png"
        logo = load_github_image(logo_url)
        if logo:
            st.image(logo, width=150)
        else:
            st.error("Unable to load logo. Using text header instead.")
            st.title("📄 Professional File Comparison Tool")
    with col2:
        st.caption(f"Version 1.0.0\nLast updated: {datetime.now().strftime('%Y-%m-%d')}")

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
            if len(uploaded_files) == 2:
                file1, file2 = uploaded_files
                file1_data = load_file(file1)
                file2_data = load_file(file2)

                if file1.name.endswith('.bin'):
                    file1_data = format_hex_data(file1_data)
                if file2.name.endswith('.bin'):
                    file2_data = format_hex_data(file2_data)

                st.subheader(f"🔍 Comparing `{file1.name}` and `{file2.name}`:")
                if file1_data and file2_data:
                    diff_html = generate_side_by_side_diff(file1_data, file2_data)
                    components.html(diff_html, height=800, scrolling=True)
                else:
                    st.error("One or both files could not be read. Please ensure they are valid and try again.")

            else:
                st.warning("⚠️ Please upload exactly two files for comparison.")

    else:  # Paste Text
        col1, col2 = st.columns(2)
        
        with col1:
            text1 = st.text_area(
                "First text content",
                height=300,
                placeholder="Paste your first text here...",
                key="text1"
            )
            name1 = st.text_input("First text name (optional)", "Text 1")

        with col2:
            text2 = st.text_area(
                "Second text content",
                height=300,
                placeholder="Paste your second text here...",
                key="text2"
            )
            name2 = st.text_input("Second text name (optional)", "Text 2")

        # Compare button
        if st.button("🔍 Compare Texts", type="primary"):
            if text1 and text2:
                st.subheader(f"🔍 Comparing `{name1}` and `{name2}`:")
                diff_html = generate_side_by_side_diff(text1, text2)
                components.html(diff_html, height=800, scrolling=True)
            else:
                st.warning("Please enter text for both fields to compare.")

if __name__ == "__main__":
    main()
