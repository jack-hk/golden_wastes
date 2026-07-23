#!/usr/bin/env python3
"""
importMovesData.py
Purpose: Convert external file to moves.json or moves.md format with changelog tracking
Parameters:
1. Input file format (.md or .json)
2. Input file path
3. Output file format (.md or .json)
4. Output file path
5. Changelog output directory (optional, defaults to ./moves-changelog)
Command: python {project}/scripts/importMovesData.py {input_format} {input_file} {output_format} {output_file} [changelog_dir]
"""

import sys
import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from difflib import unified_diff


def validate_entry(entry: Dict[str, Any]) -> None:
    """Validate that every entry has required fields: icon, name, and type"""
    required_fields = ['icon', 'name', 'type']
    for field in required_fields:
        if not entry.get(field):
            raise ValueError(f"Entry validation failed. Missing required field '{field}' in entry: {json.dumps(entry)}")


def markdown_to_json(md_content: str) -> List[Dict[str, Any]]:
    """Convert Markdown content back to JSON format"""
    lines = md_content.split('\n')
    result = []
    current_entry = {}
    current_class = None
    current_type = None
    description_buffer = ''
    is_inside_description = False
    
    for line in lines:
        line = line.strip()
        
        # Class header (# Class Name)
        if line.startswith('# '):
            current_class = line.replace('# ', '').strip()
            
        # Type header (## Type Name)  
        elif line.startswith('## '):
            current_type = line.replace('## ', '').strip()
            
        # Move name (**Move Name**)
        elif line.startswith('**') and line.endswith('**'):
            # Save previous entry if it exists
            if current_entry:
                if 'description' not in current_entry:
                    current_entry['description'] = ''
                validate_entry(current_entry)
                result.append(current_entry)
            
            # Start new entry
            current_entry = {'name': line.replace('**', '').strip()}
            if current_class:
                current_entry['class'] = current_class
            if current_type:
                current_entry['type'] = current_type
            description_buffer = ''
            
        # Description start (contains { but not })
        elif '{' in line and '}' not in line:
            is_inside_description = True
            description_buffer += line.split('{')[1].strip() + '\n'
            
        # Description end (contains })
        elif '}' in line:
            description_buffer += line.split('}')[0].strip()
            current_entry['description'] = description_buffer.strip()
            is_inside_description = False
            
        # Description middle (inside description block)
        elif is_inside_description:
            description_buffer += line.strip() + '\n'
            
        # Required field
        elif line.startswith('Required:'):
            current_entry['required'] = line.replace('Required:', '').strip()
            
        # Replaces field
        elif line.startswith('Replaces:'):
            current_entry['replaces'] = line.replace('Replaces:', '').strip()
            
        # Icon field
        elif line.startswith('Icon:'):
            icon_match = re.search(r'<img src="(?:https://seiyria\.com/gameicons-font/svg/|/)?SVG/([^.]+)\.svg"[^>]*width="(\d+)"[^>]*/?>', line)
            if icon_match:
                current_entry['icon'] = icon_match.group(1).strip()
            else:
                raise ValueError(f"Failed to parse icon in line: {line}")
    
    # Add the last entry
    if current_entry:
        if 'description' not in current_entry:
            current_entry['description'] = ''
        validate_entry(current_entry)
        result.append(current_entry)
    
    # Clean up descriptions (remove remaining braces)
    for entry in result:
        if 'description' in entry and entry['description']:
            entry['description'] = re.sub(r'[{}]', '', entry['description']).strip()
    
    return result


def json_to_markdown(json_data: List[Dict[str, Any]]) -> str:
    """Convert JSON data to Markdown format"""
    if not json_data:
        return ""
    
    # Group entries by class and type
    grouped_data = {}
    for entry in json_data:
        class_name = entry.get('class', 'Unclassified')
        type_name = entry.get('type', 'Untyped')
        
        if class_name not in grouped_data:
            grouped_data[class_name] = {}
        if type_name not in grouped_data[class_name]:
            grouped_data[class_name][type_name] = []
        
        grouped_data[class_name][type_name].append(entry)
    
    # Generate markdown content
    markdown_lines = []
    
    for class_name in sorted(grouped_data.keys()):
        markdown_lines.append(f"# {class_name}")
        markdown_lines.append("")
        
        for type_name in sorted(grouped_data[class_name].keys()):
            markdown_lines.append(f"## {type_name}")
            markdown_lines.append("")
            
            for entry in sorted(grouped_data[class_name][type_name], key=lambda x: x['name']):
                # Move name
                markdown_lines.append(f"**{entry['name']}**")
                markdown_lines.append("")
                
                # Description (with braces if multi-line)
                description = entry.get('description', '')
                if description:
                    if '\n' in description or len(description) > 80:
                        markdown_lines.append("{")
                        markdown_lines.append(description)
                        markdown_lines.append("}")
                    else:
                        markdown_lines.append(f"{{{description}}}")
                    markdown_lines.append("")
                
                # Required field
                if entry.get('required'):
                    markdown_lines.append(f"Required: {entry['required']}")
                    markdown_lines.append("")
                
                # Replaces field
                if entry.get('replaces'):
                    markdown_lines.append(f"Replaces: {entry['replaces']}")
                    markdown_lines.append("")
                
                # Icon field
                if entry.get('icon'):
                    markdown_lines.append(f'Icon: <img src="/SVG/{entry["icon"]}.svg" width="32" />')
                    markdown_lines.append("")
                
                # Add extra line between moves
                markdown_lines.append("")
            
            # Add extra line between types
            markdown_lines.append("")
        
        # Add extra line between classes
        markdown_lines.append("")
    
    return '\n'.join(markdown_lines).strip()


def process_json_file(input_path: str) -> List[Dict[str, Any]]:
    """Process JSON input file"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate each entry if it's a list
        if isinstance(data, list):
            for entry in data:
                validate_entry(entry)
            return data
        else:
            raise ValueError("JSON file must contain an array of move entries")
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


def process_markdown_file(input_path: str) -> List[Dict[str, Any]]:
    """Process Markdown input file"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return markdown_to_json(content)
    except UnicodeDecodeError:
        raise ValueError("Unable to read markdown file. Please ensure it's UTF-8 encoded.")


def load_existing_data(output_file: str, output_format: str) -> List[Dict[str, Any]]:
    """Load existing output file data if it exists"""
    if not os.path.isfile(output_file):
        return []
    
    try:
        if output_format == '.json':
            with open(output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:  # .md
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return markdown_to_json(content)
    except (json.JSONDecodeError, IOError, ValueError):
        return []


def create_move_index(moves: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Create an index of moves by name for easier comparison"""
    return {move['name']: move for move in moves}


def compare_moves(old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare old and new move data and return differences"""
    old_index = create_move_index(old_data)
    new_index = create_move_index(new_data)
    
    old_names = set(old_index.keys())
    new_names = set(new_index.keys())
    
    changes = {
        'added': [],
        'removed': [],
        'modified': [],
        'has_changes': False
    }
    
    # Find added moves
    added_names = new_names - old_names
    for name in added_names:
        changes['added'].append(new_index[name])
    
    # Find removed moves
    removed_names = old_names - new_names
    for name in removed_names:
        changes['removed'].append(old_index[name])
    
    # Find modified moves
    common_names = old_names & new_names
    for name in common_names:
        old_move = old_index[name]
        new_move = new_index[name]
        
        if old_move != new_move:
            field_changes = {}
            all_fields = set(old_move.keys()) | set(new_move.keys())
            
            for field in all_fields:
                old_value = old_move.get(field, None)
                new_value = new_move.get(field, None)
                
                if old_value != new_value:
                    field_changes[field] = {
                        'old': old_value,
                        'new': new_value
                    }
            
            if field_changes:
                changes['modified'].append({
                    'name': name,
                    'changes': field_changes
                })
    
    # Determine if any changes were made
    changes['has_changes'] = bool(changes['added'] or changes['removed'] or changes['modified'])
    
    return changes


def generate_changelog(changes: Dict[str, Any], input_format: str, input_file: str, output_format: str) -> str:
    """Generate a formatted changelog"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    changelog = []
    changelog.append(f"# Moves Data Changelog")
    changelog.append(f"**Date:** {timestamp}")
    changelog.append(f"**Input Format:** {input_format}")
    changelog.append(f"**Output Format:** {output_format}")
    changelog.append(f"**Source File:** {os.path.basename(input_file)}")
    changelog.append("")
    
    # Summary
    summary = []
    if changes['added']:
        summary.append(f"{len(changes['added'])} added")
    if changes['removed']:
        summary.append(f"{len(changes['removed'])} removed")
    if changes['modified']:
        summary.append(f"{len(changes['modified'])} modified")
    
    changelog.append(f"**Summary:** {', '.join(summary)}")
    changelog.append("")
    
    # Added moves
    if changes['added']:
        changelog.append("## Added Moves")
        for move in changes['added']:
            changelog.append(f"- **{move['name']}** (Type: {move.get('type', 'N/A')}, Class: {move.get('class', 'N/A')})")
            if move.get('description'):
                # Truncate long descriptions
                desc = move['description'][:100] + "..." if len(move['description']) > 100 else move['description']
                changelog.append(f"  *{desc}*")
        changelog.append("")
    
    # Removed moves
    if changes['removed']:
        changelog.append("## Removed Moves")
        for move in changes['removed']:
            changelog.append(f"- **{move['name']}** (Type: {move.get('type', 'N/A')}, Class: {move.get('class', 'N/A')})")
        changelog.append("")
    
    # Modified moves
    if changes['modified']:
        changelog.append("## Modified Moves")
        for move_change in changes['modified']:
            changelog.append(f"- **{move_change['name']}**")
            for field, field_change in move_change['changes'].items():
                old_val = field_change['old'] or 'NULL'
                new_val = field_change['new'] or 'NULL'
                
                # Truncate long values for readability
                if isinstance(old_val, str) and len(old_val) > 80:
                    old_val = old_val[:80] + "..."
                if isinstance(new_val, str) and len(new_val) > 80:
                    new_val = new_val[:80] + "..."
                
                changelog.append(f"  - `{field}`: {old_val} → {new_val}")
        changelog.append("")
    
    return '\n'.join(changelog)


def save_changelog(changelog_content: str, changelog_dir: str) -> str:
    """Save changelog to a new file with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"moves_changelog_{timestamp}.md"
    filepath = os.path.join(changelog_dir, filename)
    
    # Ensure changelog directory exists
    if not os.path.exists(changelog_dir):
        os.makedirs(changelog_dir)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(changelog_content)
    
    return filepath


def write_output_file(data: List[Dict[str, Any]], output_file: str, output_format: str) -> None:
    """Write data to output file in specified format"""
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if output_format == '.json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:  # .md
        markdown_content = json_to_markdown(data)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)


def main():
    """Main function to handle command line arguments and process files"""
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print("Usage: python importMovesData.py <input_format> <input_file> <output_format> <output_file> [changelog_dir]")
        print("Input/Output formats: .md or .json")
        print("changelog_dir: Directory for changelog files (optional, defaults to ./moves-changelog)")
        print()
        print("Examples:")
        print("  python importMovesData.py .md input.md .json data/moves.json")
        print("  python importMovesData.py .json input.json .md data/moves.md")
        print("  python importMovesData.py .md input.md .json data/moves.json ./logs/changes")
        sys.exit(1)
    
    input_format = sys.argv[1].lower()
    input_file = sys.argv[2]
    output_format = sys.argv[3].lower()
    output_file = sys.argv[4]
    changelog_dir = sys.argv[5] if len(sys.argv) == 6 else './moves-changelog'
    
    # Validate formats
    valid_formats = ['.md', '.json']
    if input_format not in valid_formats:
        print(f"Error: Unsupported input format '{input_format}'. Use .md or .json")
        sys.exit(1)
    
    if output_format not in valid_formats:
        print(f"Error: Unsupported output format '{output_format}'. Use .md or .json")
        sys.exit(1)
    
    # Check if input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        sys.exit(1)
    
    try:
        # Load existing data for comparison
        existing_data = load_existing_data(output_file, output_format)
        
        # Process input file based on format
        if input_format == '.md':
            print(f"Processing Markdown file: {input_file}")
            new_data = process_markdown_file(input_file)
        else:  # .json
            print(f"Processing JSON file: {input_file}")
            new_data = process_json_file(input_file)
        
        # Compare data and generate changelog if needed
        changes = compare_moves(existing_data, new_data)
        
        if changes['has_changes']:
            print(f"Changes detected. Generating changelog...")
            changelog_content = generate_changelog(changes, input_format, input_file, output_format)
            changelog_file = save_changelog(changelog_content, changelog_dir)
            print(f"Changelog saved to: {changelog_file}")
        else:
            print("No changes detected. Skipping changelog generation.")
        
        # Write to output file in specified format
        write_output_file(new_data, output_file, output_format)
        
        format_name = "JSON" if output_format == '.json' else "Markdown"
        print(f"Successfully processed {len(new_data)} moves to {format_name} format: {output_file}")
        
        # Print summary of changes if any
        if changes['has_changes']:
            summary_parts = []
            if changes['added']:
                summary_parts.append(f"{len(changes['added'])} added")
            if changes['removed']:
                summary_parts.append(f"{len(changes['removed'])} removed")
            if changes['modified']:
                summary_parts.append(f"{len(changes['modified'])} modified")
            print(f"Changes summary: {', '.join(summary_parts)}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()