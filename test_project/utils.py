"""
Utility functions for the sample project.

This module provides common utility functions including:
- Data processing
- File operations
- Error handling
"""

import json
from pathlib import Path
from typing import List, Any, Dict

def process_data(data: List[str]) -> List[Dict[str, Any]]:
    """
    Process a list of data items.
    
    Args:
        data: List of string items to process
        
    Returns:
        List of processed data dictionaries
    """
    processed = []
    
    for i, item in enumerate(data):
        processed_item = {
            "id": i + 1,
            "original": item,
            "processed": f"processed_{item}",
            "length": len(item),
            "uppercase": item.upper()
        }
        processed.append(processed_item)
    
    return processed

def save_results(data: List[Dict[str, Any]], output_file: Path):
    """
    Save processed data to a file.
    
    Args:
        data: List of processed data dictionaries
        output_file: Path to output file
    """
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Also save a summary
    summary_file = output_file.parent / f"{output_file.stem}_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Processed {len(data)} items\n")
        f.write("=" * 30 + "\n")
        for item in data:
            f.write(f"ID: {item['id']}, Original: {item['original']}\n")

def validate_data(data: List[str]) -> bool:
    """
    Validate input data.
    
    Args:
        data: List of data items to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(data, list):
        return False
    
    if len(data) == 0:
        return False
    
    for item in data:
        if not isinstance(item, str):
            return False
        if len(item.strip()) == 0:
            return False
    
    return True

def format_output(data: List[Dict[str, Any]]) -> str:
    """
    Format processed data as a readable string.
    
    Args:
        data: List of processed data dictionaries
        
    Returns:
        Formatted string representation
    """
    lines = ["Processed Data Summary", "=" * 25]
    
    for item in data:
        lines.append(f"ID: {item['id']}")
        lines.append(f"  Original: {item['original']}")
        lines.append(f"  Processed: {item['processed']}")
        lines.append(f"  Length: {item['length']}")
        lines.append(f"  Uppercase: {item['uppercase']}")
        lines.append("")
    
    return "\n".join(lines) 