import streamlit as st
import difflib
import base64
from pathlib import Path
import streamlit.components.v1 as components
from typing import Tuple, Optional
import io
import logging
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
SUPPORTED_TEXT_EXTENSIONS = {'.c', '.h', '.cpp', '.txt', '.py', '.json', '.yaml', '.yml', '.md', '.css', '.html', '.js'}
SUPPORTED_BINARY_EXTENSIONS = {'.bin', '.hex'}
MAX_FILE_SIZE_MB = 10
LOGO_URL = "https://raw.githubusercontent.com/Puneeth-kmp/File-Comparison-Tool/main/Picsart_24-11-10_15-02-57-542.png"

class FileComparisonTool:
    def __init__(self):
        self.config = {
            'max_file_size_mb': MAX_FILE_SIZE_MB,
            'supported_text_extensions': SUPPORTED_TEXT_EXTENSIONS,
            'supported_binary_extensions': SUPPORTED_BINARY_EXTENSIONS,
        }
        
    @staticmethod
    def load_file_content(file) -> Tuple[Optional[str], Optional[str]]:
        """
        Load and validate file content
        Returns: (content, error_message)
        """
        try:
            # Check file size
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                return None, f"File size exceeds {MAX_FILE_SIZE_MB}MB limit"
            
            content = file.getvalue().decode("utf-8")
            return content, None
        except UnicodeDecodeError:
            return None, "File appears to be binary or contains invalid characters"
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            return None, f"Error loading file: {str(e)}"

    @staticmethod
    def format_hex_data(data: bytes, bytes_per_line: int = 16) -> str:
        """Format binary data as hex dump"""
        lines = []
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]
            hex_dump = ' '.join(f'{b:02x}' for b in chunk)
            ascii_dump = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            lines.append(f"{i:08x}:  {hex_dump:<{bytes_per_line*3}}  |{ascii_dump}|")
        return '\n'.join(lines)

    def generate_diff_html(self, file1_data: str, file2_data: str) -> str:
        """Generate HTML for side-by-side diff view with enhanced styling"""
        html_content = """
        <style>
            .diff-container { font-family: 'Monaco', 'Consolas', monospace; }
            .diff-table { width: 100%; border-collapse: collapse; border: 1px solid #ddd; }
            .diff-table td { padding: 5px 10px; vertical-align: top; border: 1px solid #ddd; }
            .line-num { 
                width: 50px;
                background-color: #f8f9fa;
                color: #6c757d;
                text-align: right;
                user-select: none;
                border-right: 1px solid #ddd;
            }
            .added { background-color: #e6ffe6; }
            .removed { background-color: #ffe6e6; }
            .modified { background-color: #fff5b1; }
            .diff-header { 
                background-color: #f8f9fa;
                font-weight: bold;
                text-align: center;
                padding: 10px;
                border-bottom: 2px solid #ddd;
            }
            .word-added { background-color: #a6f3a6; }
            .word-removed { background-color: #f8a6a6; }
            .word-modified { background-color: #fee090; }
        </style>
        <div class="diff-container">
        <table class="diff-table">
            <tr>
                <th colspan="2" class="diff-header">Original File</th>
                <th colspan="2" class="diff-header">Modified File</th>
            </tr>
        """
        
        file1_lines = file1_data.splitlines()
        file2_lines = file2_data.splitlines()
        line_diff = difflib.ndiff(file1_lines, file2_lines)
        
        line_num1, line_num2 = 1, 1
        
        for line in line_diff:
            tag = line[:2]
            content = line[2:]
            
            if tag == "  ":  # Unchanged line
                html_content += f"""
                    <tr>
                        <td class="line-num">{line_num1}</td>
                        <td>{content}</td>
                        <td class="line-num">{line_num2}</td>
                        <td>{content}</td>
                    </tr>
                """
                line_num1 += 1
                line_num2 += 1
                
            elif tag == "- ":  # Removed line
                html_content += f"""
                    <tr>
                        <td class="line-num">{line_num1}</td>
                        <td class="removed">{content}</td>
                        <td class="line-num"></td>
                        <td></td>
                    </tr>
                """
                line_num1 += 1
                
            elif tag == "+ ":  # Added line
                html_content += f"""
                    <tr>
                        <td class="line-num"></td>
                        <td></td>
                        <td class="line-num">{line_num2}</td>
                        <td class="added">{content}</td>
                    </tr>
                """
                line_num2 += 1

        html_content += "</table></div>"
        return html_content

@st.cache_data
def load_github_image(url: str) -> Optional[Image.Image]:
    """
    Load an image from a GitHub repository with caching
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Error loading logo: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Professional File Comparison Tool",
        page_icon="📄",
        layout="wide",  # Set the layout to "wide"
        initial_sidebar_state="expanded"
    )

    # Initialize the tool
    tool = FileComparisonTool()

    # Custom CSS for better UI
    st.markdown(""" 
        <style>
            .stApp {
                max-width: 100% !important;  /* Ensure full width */
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
                gap: 20px;
            }
            .header-text {
                color: #1E3A8A;
                margin: 0;
            }
            .stMarkdown {
                color: #4B5563;
            }
            /* Additional styling for full-width components */
            .stRadio, .stTextArea, .stFileUploader, .stButton {
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header with logo and title
    col1, col2 = st.columns([3, 1])
    with col1:
        logo = load_github_image(LOGO_URL)
        if logo:
            st.markdown(
                """
                <div class="logo-container" style="display: flex; justify-content: center; align-items: center;">
                    <img src="data:image/png;base64,{}" style="width: 30%;">
                    <h1 class="header-text"></h1>
                </div>
                """.format(
                    base64.b64encode(BytesIO(requests.get(LOGO_URL).content).read()).decode()
                ),
                unsafe_allow_html=True
            )
        else:
            st.title("File Comparison Tool")
    with col2:
        st.caption(f"Version 1.0.0\nLast updated: {datetime.now().strftime('%Y-%m-%d')}")

    # Input method selection with better styling
    input_method = st.radio(
        "Select comparison method:",
        ["Upload Files", "Paste Text"],
        horizontal=True,
        help="Choose how you want to compare your files"
    )

    # File upload method
    if input_method == "Upload Files":
        uploaded_file_1 = st.file_uploader("Upload Original File", type=list(SUPPORTED_TEXT_EXTENSIONS), label_visibility="visible")
        uploaded_file_2 = st.file_uploader("Upload Modified File", type=list(SUPPORTED_TEXT_EXTENSIONS), label_visibility="visible")

        if uploaded_file_1 and uploaded_file_2:
            content_1, error_1 = tool.load_file_content(uploaded_file_1)
            content_2, error_2 = tool.load_file_content(uploaded_file_2)
            if content_1 and content_2:
                html_diff = tool.generate_diff_html(content_1, content_2)
                st.markdown(html_diff, unsafe_allow_html=True)
            else:
                st.error("Error loading files: {} {}".format(error_1 or "", error_2 or ""))
    else:
        st.subheader("Paste text for comparison:")
        text_1 = st.text_area("Original Text", height=200)
        text_2 = st.text_area("Modified Text", height=200)
        
        if text_1 and text_2:
            html_diff = tool.generate_diff_html(text_1, text_2)
            st.markdown(html_diff, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
