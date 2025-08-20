import os
import re
from collections import defaultdict
from file_selector import main_file_selector
import json

def parse_mermaid_flowchart(mermaid_text):
    """Parse mermaid flowchart and return nodes and connections"""
    lines = mermaid_text.strip().split('\n')
    nodes = {}
    connections = []
    all_node_ids = set()
    
    for line in lines:
        line = line.strip()
        if line.startswith('graph'):
            continue
            
        # Find all node definitions in the line
        node_pattern = r'([A-Za-z0-9_]+)\[([^\]]*)\]'
        node_matches = re.findall(node_pattern, line)
        for node_id, node_label in node_matches:
            nodes[node_id] = node_label.strip()
            all_node_ids.add(node_id)
        
        # Find all connections in the line
        if '-->' in line:
            parts = line.split('-->')
            if len(parts) == 2:
                left_side = parts[0].strip()
                right_side = parts[1].strip()
                
                # Extract node IDs using regex to handle both A and A[Label]
                left_match = re.match(r'([A-Za-z0-9_]+)(?:\[[^\]]*\])?', left_side)
                right_match = re.match(r'([A-Za-z0-9_]+)(?:\[[^\]]*\])?', right_side)
                
                if left_match and right_match:
                    from_node = left_match.group(1)
                    to_node = right_match.group(1)
                    connections.append((from_node, to_node))
                    all_node_ids.add(from_node)
                    all_node_ids.add(to_node)
    
    # Ensure all referenced nodes exist in the nodes dict
    for node_id in all_node_ids:
        if node_id not in nodes:
            nodes[node_id] = node_id
    
    return nodes, connections

def build_complete_hierarchy(nodes, connections):
    """Build complete hierarchical structure with all relationships"""
    children = defaultdict(list)
    parents = defaultdict(list)
    
    # Build relationships
    for from_node, to_node in connections:
        children[from_node].append(to_node)
        parents[to_node].append(from_node)
    
    # Find root nodes (nodes with no parents)
    root_nodes = [node_id for node_id in nodes if node_id not in parents]
    
    # Build complete node info with all relationships
    node_info = {}
    for node_id in nodes:
        node_info[node_id] = {
            'id': node_id,
            'label': nodes[node_id],
            'parents': parents[node_id],
            'children': children[node_id],
            'depth': -1,  # To be calculated
            'is_root': node_id in root_nodes,
            'is_leaf': len(children[node_id]) == 0
        }
    
    # Calculate depths starting from roots
    def calculate_depth(node_id, current_depth):
        node_info[node_id]['depth'] = current_depth
        for child_id in children[node_id]:
            calculate_depth(child_id, current_depth + 1)
    
    for root_id in root_nodes:
        calculate_depth(root_id, 0)
    
    return node_info, root_nodes, children, parents

def create_json_structure(node_id, node_info, children, visited=None):
    """Create hierarchical JSON structure for visualization"""
    if visited is None:
        visited = set()
    
    if node_id in visited:
        return None
    
    visited.add(node_id)
    
    node_data = node_info[node_id].copy()
    node_data['children_objects'] = []
    
    # Recursively build children
    for child_id in children[node_id]:
        if child_id not in visited:
            child_structure = create_json_structure(child_id, node_info, children, visited.copy())
            if child_structure:
                node_data['children_objects'].append(child_structure)
    
    # Remove the list children since we have children_objects
    if 'children' in node_data:
        del node_data['children']
    if 'parents' in node_data:
        del node_data['parents']
    
    return node_data

def generate_text_from_json(node, is_root=True, is_last=True, prefix=""):
    """Generate text representation from JSON structure"""
    lines = []
    node_label = node['label']
    box_width = len(node_label) + 2
    
    if is_root:
        # Root node
        lines.append(f"┌{'─' * box_width}┐")
        lines.append(f"│ {node_label} │")
        lines.append(f"└{'─' * box_width}┘")
    else:
        # Child node
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}┌{'─' * box_width}┐")
        lines.append(f"{prefix}{' ' * 4 if is_last else '│   '}│ {node_label} │")
        lines.append(f"{prefix}{' ' * 4 if is_last else '│   '}└{'─' * box_width}┘")
    
    # Process children
    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node['children_objects']):
        child_is_last = (i == len(node['children_objects']) - 1)
        child_lines = generate_text_from_json(child, False, child_is_last, child_prefix)
        lines.extend(child_lines)
    
    return lines

def create_visual_flowchart(mermaid_text):
    """Create a visually pleasing text-based flowchart"""
    nodes, connections = parse_mermaid_flowchart(mermaid_text)
    node_info, root_nodes, children, parents = build_complete_hierarchy(nodes, connections)
    
    print("\n=== COMPLETE NODE INFO ===")
    for node_id, info in node_info.items():
        print(f"{node_id}: {json.dumps(info, indent=2, ensure_ascii=False)}")
    
    print(f"\nRoot nodes: {root_nodes}")
    print(f"Children: {dict(children)}")
    print(f"Parents: {dict(parents)}")
    
    if not root_nodes:
        return "Could not determine root node"
    
    # Build JSON structure for visualization
    json_structures = []
    visited = set()
    
    for root_id in root_nodes:
        if root_id not in visited:
            json_structure = create_json_structure(root_id, node_info, children, visited)
            if json_structure:
                json_structures.append(json_structure)
    
    print("\n=== JSON STRUCTURES ===")
    for i, struct in enumerate(json_structures):
        print(f"Structure {i+1}:\n{json.dumps(struct, indent=2, ensure_ascii=False)}")
    
    # Generate text representation
    all_lines = []
    for i, json_struct in enumerate(json_structures):
        if i > 0:
            all_lines.append("")
        lines = generate_text_from_json(json_struct)
        all_lines.extend(lines)
    
    return "\n".join(all_lines)

def convert_mermaid_in_file(file_path, output_suffix="_FC_visual", keep_original_mermaid=True):
    """Convert mermaid charts in a markdown file to visual flowcharts"""
    try:
        # Generate output filename
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        output_file = os.path.join(file_dir, f"{name}{output_suffix}{ext}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        new_lines = []
        in_mermaid_block = False
        mermaid_content = []
        mermaid_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == '```mermaid':
                in_mermaid_block = True
                mermaid_lines = [line]
                mermaid_content = []
                i += 1
                continue
            elif in_mermaid_block and line.strip() == '```':
                # End of mermaid block
                mermaid_lines.append(line)
                
                # Process the mermaid content
                mermaid_text = '\n'.join(mermaid_content)
                
                if 'graph TD' in mermaid_text or 'graph LR' in mermaid_text or mermaid_text.strip().startswith('graph'):
                    # Create visual chart
                    try:
                        visual_chart = create_visual_flowchart(mermaid_text)
                        
                        # Add visual chart
                        new_lines.append('```text')
                        new_lines.append('# Visual Flowchart')
                        new_lines.append(visual_chart)
                        new_lines.append('```')
                        
                        # Add original mermaid block if requested
                        if keep_original_mermaid:
                            new_lines.append('')
                            new_lines.append('<!-- Original Mermaid Chart -->')
                            new_lines.extend(mermaid_lines)
                    except Exception as e:
                        print(f"Warning: Could not parse mermaid chart: {e}")
                        new_lines.extend(mermaid_lines)
                else:
                    # Keep original if not TD/LR graph
                    new_lines.extend(mermaid_lines)
                
                in_mermaid_block = False
                mermaid_content = []
                mermaid_lines = []
                i += 1
                continue
            elif in_mermaid_block:
                mermaid_lines.append(line)
                # Only add non-marker lines to content for parsing
                if not line.strip().startswith('```mermaid') and not line.strip() == '```':
                    mermaid_content.append(line)
                i += 1
                continue
            else:
                new_lines.append(line)
                i += 1
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(new_lines))
        
        print(f"✓ Created visual version: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Main function for flowchart visualizer"""
    print("=== Mermaid Flowchart Visualizer ===")
    selected_files = main_file_selector()
    
    if not selected_files:
        print("No files selected for processing.")
        return
    
    # Ask user for options
    keep_mermaid_choice = input("Keep original mermaid code in output? (y/n, default=y): ").strip().lower()
    keep_original_mermaid = keep_mermaid_choice != 'n'
    
    print(f"\nProcessing {len(selected_files)} file(s)...")
    print(f"Keep original mermaid: {'Yes' if keep_original_mermaid else 'No'}")
    
    processed = 0
    for file_path in selected_files:
        if convert_mermaid_in_file(str(file_path), keep_original_mermaid=keep_original_mermaid):
            processed += 1
    
    print(f"\nCompleted! Processed {processed}/{len(selected_files)} files.")

if __name__ == "__main__":
    main()