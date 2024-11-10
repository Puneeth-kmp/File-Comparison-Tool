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
        
        # Generate diff using difflib
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
        logger.error(f"Error loading logo: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Professional File Comparison Tool",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize the tool
    tool = FileComparisonTool()

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
                justify-content: center;
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

    # Input method selection with better styling
    input_method = st.radio(
        "Select comparison method:",
        ["Upload Files", "Paste Text"],
        horizontal=True,
        help="Choose how you want to compare content"
    )

    if input_method == "Upload Files":
        st.info(f"""
            📌 Supported file types:
            - Text files: {', '.join(tool.config['supported_text_extensions'])}
            - Binary files: {', '.join(tool.config['supported_binary_extensions'])}
            - Maximum file size: {tool.config['max_file_size_mb']}MB
        """)

        uploaded_files = st.file_uploader(
            "Upload files for comparison",
            type=[ext[1:] for ext in tool.config['supported_text_extensions'].union(tool.config['supported_binary_extensions'])],
            accept_multiple_files=True,
            help="Upload exactly two files to compare"
        )

        if uploaded_files:
            if len(uploaded_files) == 2:
                file1 = uploaded_files[0]
                file2 = uploaded_files[1]

                file1_data, error1 = tool.load_file_content(file1)
                file2_data, error2 = tool.load_file_content(file2)

                if error1 or error2:
                    st.error(f"Error loading files: {error1 or error2}")
                else:
                    if file1.name.endswith(tuple(SUPPORTED_TEXT_EXTENSIONS)):
                        diff_html = tool.generate_diff_html(file1_data, file2_data)
                        components.html(diff_html, height=500)
                    else:
                        st.text("Binary files cannot be diffed in this mode.")
            else:
                st.error("Please upload exactly two files for comparison.")

    elif input_method == "Paste Text":
        text1 = st.text_area("Paste the first text for comparison")
        text2 = st.text_area("Paste the second text for comparison")

        if text1 and text2:
            diff_html = tool.generate_diff_html(text1, text2)
            components.html(diff_html, height=500)

if __name__ == "__main__":
    main()
