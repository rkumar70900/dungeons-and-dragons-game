"""
This script processes text files in a specified directory by performing two main tasks:
1. Truncating the content of each file at the first occurrence of a specified marker.
2. Formatting tables with tab-separated values into a markdown-like table format.
Functions:
    truncate_file_at_here(file_path, marker="Copyright Notice"):
    format_and_replace_table(file_path):
Usage:
    The script processes all .txt files in the specified directory.
    It first truncates the content of each file at the specified marker and then formats any tables found in the file.
    The directory path is defined by the 'directory' variable.
"""

import os

# Function to modify the content of the file
def truncate_file_at_here(file_path, marker="Copyright Notice"):
    """
    Truncates the content of a file at the first occurrence of a specified marker.
    Args:
        file_path (str): The path to the file to be truncated.
        marker (str): The marker string at which to truncate the file. Defaults to "Copyright Notice".
    Raises:
        Exception: If there is an error processing the file.
    Example:
        truncate_file_at_here('/path/to/file.txt', marker="End of Document")
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Find the marker and truncate the file
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                if marker in line:
                    break
                if not line.startswith("5e SRD >"):
                    file.write(line)

        print(f"Processed: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def format_and_replace_table(file_path):
    """
    Reads a text file, identifies and formats tables with tab-separated values into a markdown-like table format,
    and writes the formatted content back to the file.
    Args:
        file_path (str): The path to the text file to be formatted.
    Raises:
        Exception: If an error occurs during file reading or writing.
    Example:
        Given a file with the following content:
            Header1\tHeader2\tHeader3
            Value1\tValue2\tValue3
            Value4\tValue5\tValue6
        The function will format it to:
            Header1 | Header2 | Header3
            ------- | ------- | -------
            Value1  | Value2  | Value3
            Value4  | Value5  | Value6
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        formatted_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if the line could be a table header (based on tab or consistent column count)
            if '\t' in line.strip():
                columns = line.strip().split('\t')
                
                # If it's a header-like row (for instance, a line with more than 2 columns)
                if len(columns) > 2:
                    formatted_lines.append(" | ".join(columns))  # Convert header row to table format
                    formatted_lines.append(" | ".join(["-" * len(col) for col in columns]))  # Separator

                    # Process rows that follow a similar pattern
                    i += 1  # Skip to next row
                    while i < len(lines) and '\t' in lines[i].strip():  # Ensure it's a row in the table
                        row = lines[i].strip().split('\t')
                        formatted_lines.append(" | ".join(row))
                        i += 1
                    continue  # Skip the default handling below for this block of lines
            formatted_lines.append(line.strip())  # For non-table lines
            i += 1

        # Write the formatted content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("\n".join(formatted_lines))

        print(f"Formatted table in: {os.path.splitext(os.path.basename(file_path))[0]}")
    except Exception as e:
        print(f"Error formatting table in {file_path}: {e}")



# Directory containing the text files
directory = "C://Users//rajes//Documents//GitHub//dungeons-and-dragons-game//web_scraping//spells"

if not os.path.isdir(directory):
    print("Invalid directory path.")
else:
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Only process .txt files
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            truncate_file_at_here(file_path)
            format_and_replace_table(file_path)
