#!/usr/bin/env python3
"""
Generate Hugo content pages from moves.json
This script combines the functionality of movesIndexGenerator.js and movesPageGenerator.js
"""

import json
import os
import re
from pathlib import Path

# Configuration variables
INPUT_FILE_PATH = './data/moves.json'
INDEX_OUTPUT_PATH = './content/rules/move/_index.md'
PAGES_OUTPUT_DIR = './content/rules/move'
ICON_SIZE_INDEX = "20"
ICON_SIZE_PAGE = "75"

# Reserved names in Windows
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM0",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9", "LPT0"
}

def normalize_name(name):
    """
    Single function to normalize names consistently for both filenames and links.
    This ensures the index references match the actual file names.
    """
    # Convert to lowercase and replace spaces with hyphens
    normalized_name = name.lower().replace(' ', '-')
    
    # Remove all non-alphanumeric characters except hyphens and underscores
    normalized_name = re.sub(r'[^\w\-]', '', normalized_name)
    
    # Replace multiple consecutive hyphens with a single hyphen
    normalized_name = re.sub(r'-+', '-', normalized_name)
    
    # Remove leading and trailing hyphens
    normalized_name = normalized_name.strip('-')
    
    # Handle Windows reserved names
    if normalized_name.upper() in RESERVED_NAMES:
        normalized_name += '-move'
    
    return normalized_name

def format_name_for_hyperlink(name):
    """Use the same normalization for hyperlinks to ensure consistency."""
    return normalize_name(name)

def normalize_name_for_url(name):
    """Use the same normalization for URLs to ensure consistency."""
    return normalize_name(name)

def convert_to_relative_link(value):
    """Convert requires/replaces to relative links."""
    items = [item.strip() for item in value.split(',')]
    links = [f"[{item}]({normalize_name(item)}/)" for item in items]
    return ', '.join(links)

def generate_index_markdown(moves):
    """Generate the markdown content for the index from the JSON data."""
    no_class_moves = [move for move in moves if not move.get('class')]
    class_moves = [move for move in moves if move.get('class')]
    
    def sort_moves_by_name(moves_list):
        return sorted(moves_list, key=lambda x: x['name'])
    
    # Group moves by class and type
    grouped_moves = {}
    for move in class_moves:
        if not move.get('class'):
            continue
        
        move_type = move.get('type', '').lower()
        class_name = move['class']
        
        if class_name not in grouped_moves:
            grouped_moves[class_name] = {
                'optional': [],
                'starting': [],
                'advanced': [],
                'expert': []
            }
        
        if move_type in grouped_moves[class_name]:
            grouped_moves[class_name][move_type].append(move)
    
    # Sort moves within each group
    for class_name in grouped_moves:
        for move_type in grouped_moves[class_name]:
            grouped_moves[class_name][move_type] = sort_moves_by_name(grouped_moves[class_name][move_type])
    
    # Generate markdown
    markdown = """---
bookSearchExclude: true
bookHidden: true
---

"""
    
    # Basic moves section
    if no_class_moves:
        markdown += "## Basic Moves\n"
        for move in sort_moves_by_name(no_class_moves):
            link_name = normalize_name(move['name'])  # Use consistent naming
            icon = move.get('icon', 'default-icon')
            markdown += f'- {{{{< icon source="https://seiyria.com/gameicons-font/svg/{icon}.svg" name="{icon}" size="{ICON_SIZE_INDEX}" >}}}} [{move["name"]}]({{{{< ref "/rules/move/{link_name}" >}}}})\n'
        markdown += '\n'
    
    # Class moves sections
    classes = ['Bard', 'Fighter', 'Paladin', 'Ranger', 'Thief']
    for class_name in classes:
        if class_name in grouped_moves and any(grouped_moves[class_name].values()):
            markdown += f"## {class_name} Moves\n"
            
            for move_type in ['optional', 'starting', 'advanced', 'expert']:
                moves_of_type = grouped_moves[class_name][move_type]
                if moves_of_type:
                    markdown += f"### {move_type.capitalize()} Moves\n"
                    for move in moves_of_type:
                        link_name = normalize_name(move['name'])  # Use consistent naming
                        icon = move.get('icon', 'default-icon')
                        markdown += f'- {{{{< icon source="https://seiyria.com/gameicons-font/svg/{icon}.svg" name="{icon}" size="{ICON_SIZE_INDEX}" >}}}} [{move["name"]}]({{{{< ref "/rules/move/{link_name}" >}}}})\n'
                    markdown += '\n'
    
    return markdown

def generate_move_page(move):
    """Generate a markdown page for an individual move."""
    if not all(key in move for key in ['name', 'description', 'type']):
        print(f"Missing required fields in move: {move}")
        return None, None
    
    normalized_name = normalize_name(move['name'])  # Use consistent naming
    
    # YAML Front Matter
    md_content = f"""---
bookHidden: true
BookToC: false
title: "{move['name'].replace('"', '\\"')}"
type: "wiki"
infobox:
  header: "{move['name'].replace('"', '\\"')}"
  icon: "https://seiyria.com/gameicons-font/svg/{move.get('icon', 'default-icon')}.svg"
  iconSize: 50

  labels:
    - label: "Type"
      item: "{move['type']}\""""
    
    if move.get('class'):
        md_content += f"""
    - label: "Class"
      item: "{convert_to_relative_link(move['class'])}\""""
    
    if move.get('requires') or move.get('replaces'):
        md_content += """
    - divider: true"""
    
    if move.get('requires'):
        md_content += f"""
    - label: "Requires"
      item: "{convert_to_relative_link(move['requires'])}\""""
    
    if move.get('replaces'):
        md_content += f"""
    - label: "Replaces"
      item: "{convert_to_relative_link(move['replaces'])}\""""
    
    md_content += """
also:"""
    
    if move.get('class'):
        md_content += f"""
    - "{move['class']}\""""
    
    md_content += """
    - "how-to-play"
---"""
    
    # Content Body
    md_content += f"\n\n{{{{< infobox >}}}}\n\n{move['description']}"
    
    return normalized_name, md_content

def main():
    """Main function to generate both index and individual pages."""
    # Read the JSON file
    try:
        with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as file:
            moves = json.load(file)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE_PATH}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    
    # Create output directories
    os.makedirs(os.path.dirname(INDEX_OUTPUT_PATH), exist_ok=True)
    os.makedirs(PAGES_OUTPUT_DIR, exist_ok=True)
    
    # Generate index markdown
    print("Generating moves index...")
    index_markdown = generate_index_markdown(moves)
    
    # Write index file
    try:
        with open(INDEX_OUTPUT_PATH, 'w', encoding='utf-8') as file:
            file.write(index_markdown)
        print(f"Successfully generated: {INDEX_OUTPUT_PATH}")
    except Exception as e:
        print(f"Error writing index file: {e}")
        return
    
    # Generate individual move pages
    print("Generating individual move pages...")
    generated_files = set()  # Track generated files to detect duplicates
    
    for move in moves:
        result = generate_move_page(move)
        if result[0] is None:
            continue
        
        normalized_name, md_content = result
        
        # Check for duplicate filenames
        if normalized_name in generated_files:
            print(f"Warning: Duplicate filename detected for '{move['name']}' -> {normalized_name}")
            continue
        
        generated_files.add(normalized_name)
        file_path = os.path.join(PAGES_OUTPUT_DIR, f"{normalized_name}.md")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(md_content)
            print(f"Generated: {file_path}")
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
    
    print("All moves content generated successfully!")
    print(f"Generated {len(generated_files)} move pages.")

if __name__ == "__main__":
    main()