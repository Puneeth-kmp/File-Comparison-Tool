import streamlit as st
import difflib
import streamlit.components.v1 as components

# Function to load file content
def load_file(file):
    return file.getvalue().decode("utf-8")

# Function to format binary data for '.bin' files
def format_hex_data(data):
    return '\n'.join([f"{i:08x}: {data[i:i+16].hex()}" for i in range(0, len(data), 16)])

# Function to generate side-by-side diff with line and word highlights
def generate_side_by_side_diff(file1_data, file2_data):
    file1_lines = file1_data.splitlines()
    file2_lines = file2_data.splitlines()
    
    # Generate line-by-line diff
    diff = difflib.ndiff(file1_lines, file2_lines)
    
    # Initialize HTML layout with line numbering and word highlights
    html_content = """
    <style>
        .diff-table { width: 100%; border-collapse: collapse; }
        .diff-table td { padding: 5px; vertical-align: top; font-family: monospace; }
        .line-num { width: 5%; background-color: #f0f0f0; text-align: right; padding-right: 10px; }
        .added { background-color: #e6ffe6; }
        .removed { background-color: #ffe6e6; }
        .modified { background-color: #ffffcc; }
    </style>
    <table class="diff-table">
        <tr>
            <th>File 1 (Line No)</th>
            <th>File 1 Content</th>
            <th>File 2 (Line No)</th>
            <th>File 2 Content</th>
        </tr>
    """
    
    # Track line numbers for each file
    line_num1, line_num2 = 1, 1

    # Process each diff line with word-level changes
    for line in diff:
        tag = line[:2]
        content = line[2:]
        
        if tag == "  ":  # No change
            left = f"<td class='line-num'>{line_num1}</td><td>{content}</td>"
            right = f"<td class='line-num'>{line_num2}</td><td>{content}</td>"
            line_num1 += 1
            line_num2 += 1
        elif tag == "- ":  # Line removed
            left = f"<td class='line-num'>{line_num1}</td><td class='removed'>{content}</td>"
            right = "<td></td><td></td>"  # No corresponding line in File 2
            line_num1 += 1
        elif tag == "+ ":  # Line added
            left = "<td></td><td></td>"  # No corresponding line in File 1
            right = f"<td class='line-num'>{line_num2}</td><td class='added'>{content}</td>"
            line_num2 += 1
        elif tag == "? ":  # Word modifications within lines
            if line_num1 - 1 < len(file1_lines) and line_num2 - 1 < len(file2_lines):
                left_words, right_words = highlight_words(file1_lines, file2_lines, line_num1, line_num2)
                left = f"<td class='line-num'>{line_num1}</td><td class='modified'>{left_words}</td>"
                right = f"<td class='line-num'>{line_num2}</td><td class='modified'>{right_words}</td>"
            line_num1 += 1
            line_num2 += 1

        html_content += f"<tr>{left}{right}</tr>"

    html_content += "</table>"
    return html_content

# Helper function for word-level highlighting
def highlight_words(file1_lines, file2_lines, line_num1, line_num2):
    s = difflib.SequenceMatcher(None, file1_lines[line_num1 - 1], file2_lines[line_num2 - 1])
    output1, output2 = [], []
    
    for opcode, i1, i2, j1, j2 in s.get_opcodes():
        word1 = file1_lines[line_num1 - 1][i1:i2]
        word2 = file2_lines[line_num2 - 1][j1:j2]
        if opcode == 'equal':
            output1.append(word1)
            output2.append(word2)
        elif opcode == 'insert':
            output2.append(f"<span class='added'>{word2}</span>")
        elif opcode == 'delete':
            output1.append(f"<span class='removed'>{word1}</span>")
        elif opcode == 'replace':
            output1.append(f"<span class='modified'>{word1}</span>")
            output2.append(f"<span class='modified'>{word2}</span>")

    return " ".join(output1), " ".join(output2)

# Main app function
def main():
    st.set_page_config(page_title="File Comparison Tool", layout="wide")
    
    # Add the logo
    logo_url = "https://github.com/Puneeth-kmp/File-Comparison-Tool/blob/main/Picsart_24-11-10_15-02-57-542.png?raw=true"
    st.image(logo_url, use_column_width=True)  # Logo fits the column width

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

                # Format binary files
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
