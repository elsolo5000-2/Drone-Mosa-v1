import os
from file_selector import main_file_selector

def format_markdown_table(table_text):
    """Format a markdown table with proper spacing"""
    lines = table_text.strip().split('\n')
    lines = [line for line in lines if line.strip()]
    if not lines:
        return table_text
    
    rows = []
    for line in lines:
        if '|' in line:
            cells = line.split('|')
            if cells[0] == '' and cells[-1] == '':
                cells = cells[1:-1]
            elif cells[0] == '':
                cells = cells[1:]
            elif cells[-1] == '':
                cells = cells[:-1]
            rows.append([cell.strip() for cell in cells])
    
    if not rows:
        return table_text
    
    try:
        max_widths = [max(len(row[i]) if i < len(row) else 0 for row in rows) for i in range(len(rows[0]))]
    except IndexError:
        return table_text
    
    formatted_rows = []
    for i, row in enumerate(rows):
        while len(row) < len(max_widths):
            row.append('')
        
        formatted_row = '| ' + ' | '.join(cell.ljust(max_widths[j]) for j, cell in enumerate(row)) + ' |'
        formatted_rows.append(formatted_row)
        
        if i == 0:
            separator = '|-' + '-|-'.join('-' * width for width in max_widths) + '-|'
            formatted_rows.append(separator)
    
    return '\n'.join(formatted_rows)

def process_file_for_tables(file_path, output_suffix="&table_format"):
    """Process a single markdown file and format tables"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        formatted_lines = []
        in_table = False
        table_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if '|' in line and line.count('|') >= 3:
                table_lines = [line]
                j = i + 1
                
                while j < len(lines) and '|' in lines[j] and lines[j].count('|') >= 3:
                    table_lines.append(lines[j])
                    j += 1
                
                if len(table_lines) >= 2:
                    table_content = '\n'.join(table_lines)
                    formatted_table = format_markdown_table(table_content)
                    formatted_lines.append(formatted_table)
                    i = j
                    continue
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
            
            i += 1
        
        # Create output filename
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        output_file = os.path.join(file_dir, f"{name}_formatted{ext}")
        output_file = os.path.join(file_dir, f"{name}{output_suffix}{ext}")
        
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(formatted_lines))
        
        print(f"✓ Created formatted version: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Main function for table formatter"""
    print("=== Markdown Table Formatter ===")
    selected_files = main_file_selector()
    
    if not selected_files:
        print("No files selected for processing.")
        return
    
    print(f"\nProcessing {len(selected_files)} file(s)...")
    processed = 0
    for file_path in selected_files:
        if process_file_for_tables(str(file_path)):
            processed += 1
    
    print(f"\nCompleted! Processed {processed}/{len(selected_files)} files.")

if __name__ == "__main__":
    main()