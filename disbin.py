import streamlit as st
import difflib
import streamlit.components.v1 as components

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
    st.set_page_config(page_title="File Comparison Tool", layout="wide")
    st.title("📄 File Comparison Tool")

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
