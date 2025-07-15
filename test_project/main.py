#!/usr/bin/env python3
"""
Main application entry point for the sample project.

This demonstrates basic Python functionality including:
- File operations
- Error handling
- Configuration management
- Data processing
"""

import os
import sys
from pathlib import Path
from config import Config
from utils import process_data, save_results

def main():
    """Main application function."""
    print("🚀 Starting Sample Project")
    
    try:
        # Load configuration
        config = Config()
        print(f"✅ Configuration loaded: {config.get('app_name')}")
        
        # Process some sample data
        data = ["item1", "item2", "item3"]
        processed_data = process_data(data)
        print(f"✅ Processed {len(processed_data)} items")
        
        # Save results
        output_file = Path("output.txt")
        save_results(processed_data, output_file)
        print(f"✅ Results saved to {output_file}")
        
        print("🎉 Application completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 