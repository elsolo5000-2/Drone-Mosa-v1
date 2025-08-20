import os
from pathlib import Path

def get_directory_choice():
    """Get directory choice from user"""
    print("\nChoose directory to process:")
    print("1. Specific directory")
    print("2. Current directory")
    print("3. Script location")
    
    while True:
        dir_choice = input("Enter your choice (1-3): ").strip()
        
        if dir_choice == '1':
            directory = input("Enter the directory path: ").strip()
        elif dir_choice == '2':
            directory = os.getcwd()
            print(f"Using current directory: {directory}")
        elif dir_choice == '3':
            directory = os.path.dirname(os.path.abspath(__file__)) or '.'
            print(f"Using script location: {directory}")
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
            continue
            
        if not os.path.exists(directory):
            print(f"Directory '{directory}' does not exist. Please try again.")
            continue
            
        if not os.path.isdir(directory):
            print(f"'{directory}' is not a directory. Please enter a valid directory path.")
            continue
            
        return directory

def list_markdown_files(directory):
    """List all markdown files in the directory"""
    try:
        md_files = list(Path(directory).glob("*.md"))
        return md_files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def select_files_interactive(md_files):
    """Let user select files interactively"""
    if not md_files:
        print("No markdown files found.")
        return []
    
    print(f"\nFound {len(md_files)} markdown file(s):")
    for i, file_path in enumerate(md_files, 1):
        print(f"{i}. {file_path.name}")
    
    # Ask user which files to process
    print("\nOptions:")
    print("1. Process all files")
    print("2. Select specific files")
    
    while True:
        choice = input("Choose an option (1-2): ").strip()
        
        if choice == '1':
            return md_files
        elif choice == '2':
            selections = input("Enter file numbers to process (e.g., '1,3,5' or '1-3'): ").strip()
            try:
                files_to_process = []
                
                # Handle ranges and individual numbers
                parts = selections.split(',')
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        # Range
                        start, end = part.split('-')
                        start_idx = int(start) - 1
                        end_idx = int(end) - 1
                        files_to_process.extend(md_files[start_idx:end_idx+1])
                    else:
                        # Single number
                        idx = int(part) - 1
                        if 0 <= idx < len(md_files):
                            files_to_process.append(md_files[idx])
                
                return files_to_process
            except ValueError:
                print("Invalid selection format. Please use numbers separated by commas or ranges (e.g., '1,3,5' or '1-3').")
        else:
            print("Invalid choice. Please select 1 or 2.")

def main_file_selector():
    """Main function for file selection - can be imported by other scripts"""
    directory = get_directory_choice()
    md_files = list_markdown_files(directory)
    selected_files = select_files_interactive(md_files)
    return selected_files

if __name__ == "__main__":
    # Test the file selector
    files = main_file_selector()
    print(f"Selected {len(files)} files:")
    for file in files:
        print(f"  - {file}")