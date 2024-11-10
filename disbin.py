import streamlit as st
import difflib
import streamlit.components.v1 as components

# Function to load file content
def load_file(file):
    return file.getvalue().decode("utf-8")

# Function to format binary data (for '.bin' files)
def format_hex_data(data):
    return '\n'.join([f"{i:08x}: {data[i:i+16].hex()}" for i in range(0, len(data), 16)])

# Function to compare files line by line and return the HTML diff
def compare_files_side_by_side(file1_data, file2_data, file1_name, file2_name):
    diff = difflib.HtmlDiff()
    diff_html = diff.make_file(file1_data.splitlines(), file2_data.splitlines(), file1_name, file2_name)
    return diff_html

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
            if len(uploaded_files) == 1:
                file = uploaded_files[0]
                file_data = load_file(file)
                if file.name.endswith('.bin'):
                    file_data = format_hex_data(file_data)
                st.subheader(f"📄 Content of `{file.name}`:")
                st.text(file_data)

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
                    diff_html = compare_files_side_by_side(file1_data, file2_data, file1.name, file2.name)
                    components.html(diff_html, height=800, scrolling=True)
                else:
                    st.error("One or both files could not be read. Please ensure they are valid and try again.")

            else:
                st.warning("⚠️ Please upload no more than two files for comparison.")

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
            if text1 or text2:
                if text1 and not text2:
                    st.subheader(f"📄 Content of `{name1}`:")
                    st.text(text1)
                elif text1 and text2:
                    st.subheader(f"🔍 Comparing `{name1}` and `{name2}`:")
                    diff_html = compare_files_side_by_side(text1, text2, name1, name2)
                    components.html(diff_html, height=800, scrolling=True)
                else:
                    st.warning("Please enter at least one text to display or two texts to compare.")

if __name__ == "__main__":
    main()
