import os

# Function to modify the content of the file
def truncate_file_at_here(file_path, marker="Copyright Notice"):
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
