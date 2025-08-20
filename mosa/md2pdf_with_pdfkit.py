import markdown
import pdfkit
import os
from pathlib import Path
from file_selector import main_file_selector

def convert_md_to_pdf_simple(md_file_path, custom_css=None):
    """Convert Markdown to PDF using pdfkit (wkhtmltopdf)"""
    
    # Read markdown file
    with open(md_file_path, 'r', encoding='utf-8') as file:
        md_content = file.read()
    
    # Convert MD to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
    
    # Add CSS styling
    if custom_css:
        css_content = custom_css
    else:
        css_content = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        @page {
            margin: 2cm;
        }
        h1 { 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 15px;
            font-size: 28pt;
            margin-top: 0;
        }
        h2 { 
            color: #2c3e50; 
            border-bottom: 1px solid #bdc3c7; 
            padding-bottom: 8px;
            font-size: 20pt;
            page-break-after: avoid;
        }
        h3 { 
            color: #2c3e50;
            font-size: 16pt;
            page-break-after: avoid;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        th, td {
            border: 1px solid #bdc3c7;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #ecf0f1;
            font-weight: bold;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10pt;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
            font-size: 9pt;
        }
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            color: #7f8c8d;
        }
        ul, ol {
            padding-left: 20px;
        }
        """
    
    # Create complete HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>{css_content}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generate output filename
    file_dir = os.path.dirname(md_file_path)
    file_name = os.path.basename(md_file_path)
    name, _ = os.path.splitext(file_name)
    output_file = os.path.join(file_dir, f"{name}.pdf")
    
    # Convert HTML to PDF
    try:
        # Configure pdfkit options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        pdfkit.from_string(full_html, output_file, options=options)
        print(f"✓ Created PDF: {output_file}")
        return output_file
    except Exception as e:
        print(f"✗ Error creating PDF for {md_file_path}: {e}")
        print("Make sure wkhtmltopdf is installed on your system!")
        return None

def batch_convert_md_to_pdf(selected_files):
    """Convert selected markdown files to PDF"""
    
    if not selected_files:
        print("No files selected for processing.")
        return []
    
    print(f"\nConverting {len(selected_files)} file(s) to PDF...")
    pdf_files = []
    
    for md_file in selected_files:
        pdf_file = convert_md_to_pdf_simple(str(md_file))
        if pdf_file:
            pdf_files.append(pdf_file)
    
    print(f"\nCompleted! Converted {len(pdf_files)}/{len(selected_files)} files to PDF.")
    return pdf_files

def main():
    """Main function for MD to PDF converter using file selector"""
    print("=== Markdown to PDF Converter ===")
    print("This converter uses your file selection system")
    
    # Use the shared file selector (only returns selected files)
    selected_files = main_file_selector()
    
    if not selected_files:
        print("No files selected. Exiting.")
        return
    
    print(f"\nSelected {len(selected_files)} file(s) for PDF conversion:")
    for i, file_path in enumerate(selected_files, 1):
        print(f"{i}. {file_path.name}")
    
    # Confirm conversion
    confirm = input(f"\nConvert these {len(selected_files)} files to PDF? (y/n): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        batch_convert_md_to_pdf(selected_files)
        print("\nPDF conversion completed!")
    else:
        print("PDF conversion cancelled.")

# Requirements:
# pip install markdown pdfkit
# 
# System requirements (install wkhtmltopdf):
# Windows: Download from https://wkhtmltopdf.org/downloads.html
# macOS: brew install wkhtmltopdf
# Linux: sudo apt-get install wkhtmltopdf

if __name__ == "__main__":
    main()