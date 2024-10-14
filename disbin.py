import streamlit as st
import difflib
import streamlit.components.v1 as components

def load_file(file):
    """
    Reads the uploaded file and returns its content.
    If the file is binary (.bin), it returns the hexadecimal representation.
    Otherwise, it decodes the content to a UTF-8 string.
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

def format_hex_data(hex_data, bytes_per_line=16):
    """
    Formats hexadecimal data into a more readable form with spaces and newlines.
    """
    formatted_lines = []
    for i in range(0, len(hex_data), bytes_per_line * 2):  # 2 hex characters per byte
        line = ' '.join(hex_data[j:j + 2] for j in range(i, min(i + bytes_per_line * 2, len(hex_data)), 2))
        formatted_lines.append(line)
    return '\n'.join(formatted_lines)

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

def main():
    st.set_page_config(page_title="File Comparison Tool", layout="wide")
    st.title("📄 File Upload and Comparison Tool")

    # File uploader for .c, .h, .cpp, .txt, .bin files
    uploaded_files = st.file_uploader(
        "Upload up to two files to compare",
        type=["c", "h", "cpp", "txt", "bin"],
        accept_multiple_files=True
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
            file1, file2 = uploaded_files  # Unpack the two files

            file1_data = load_file(file1)
            file2_data = load_file(file2)

            if file1.name.endswith('.bin'):
                file1_data = format_hex_data(file1_data)
            if file2.name.endswith('.bin'):
                file2_data = format_hex_data(file2_data)

            st.subheader(f"🔍 Comparing `{file1.name}` and `{file2.name}`:")

            if file1_data and file2_data:
                # Generate side-by-side diff table
                diff_html = compare_files_side_by_side(
                    file1_data,
                    file2_data,
                    file1.name,
                    file2.name
                )

                # Optional: Add some custom CSS for better styling
                custom_css = """
                <style>
                table.diff {font-family:Arial, sans-serif;border:medium;}
                .diff_header {background-color:#e0e0e0}
                td.diff_header {text-align:right}
                .diff_next {color:black}
                .diff_add {background-color:#aaffaa}
                .diff_chg {background-color:#ffff77}
                .diff_sub {background-color:#ffaaaa}
                </style>
                """

                # Combine CSS and diff table HTML
                full_html = f"{custom_css}{diff_html}"

                # Render the HTML in Streamlit using components.html
                components.html(full_html, height=600, scrolling=True)
            else:
                st.error("One or both files could not be read. Please ensure they are valid and try again.")

        else:
            st.warning("⚠️ Please upload no more than two files for comparison.")

if __name__ == "__main__":
    main()
    