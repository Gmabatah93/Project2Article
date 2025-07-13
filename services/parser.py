"""
File parsing and project analysis service.

This module handles:
- File upload processing (FR-1)
- Project parsing and analysis pipeline (FR-2)
- File tree generation with ignore patterns

Its primary role is to take a compressed project file, such as a .zip or .tar.gz, 
and produce a structured, machine-readable summary of its contents that can be used by the AI workflow.
"""

import os
import zipfile
import tarfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectParser:
    """Handles project file parsing and analysis."""
    
    def __init__(self, max_size_mb: int = 20):
        """
        Initialize the parser with configuration.
        
        Args:
            max_size_mb: Maximum allowed file size in MB
        """
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Common ignore patterns from FR-2
        self.ignore_patterns = [
            '.git',
            '__pycache__',
            '.pytest_cache',
            '.venv',
            'venv',
            'env',
            'node_modules',
            '.DS_Store',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.coverage',
            '.tox',
            '.mypy_cache',
            '.ruff_cache'
        ]
    
    def validate_upload(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file according to FR-1 requirements.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size
        if uploaded_file.size > self.max_size_bytes:
            return False, f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size ({self.max_size_mb}MB)"
        
        # Check file type
        allowed_extensions = ['.zip', '.tar.gz', '.tgz']
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension not in allowed_extensions and not uploaded_file.name.endswith('.tar.gz'):
            return False, f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        
        return True, ""
    
    def extract_archive(self, uploaded_file) -> Optional[Path]:
        """
        Extract uploaded archive to temporary directory.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Path to extracted directory or None if extraction fails
        """
        try:
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix="project_analysis_"))
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # Extract based on file type
            file_name = uploaded_file.name.lower()
            
            if file_name.endswith('.zip'):
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
            elif file_name.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(fileobj=uploaded_file, mode='r:gz') as tar_ref:
                    tar_ref.extractall(temp_dir)
            else:
                logger.error(f"Unsupported file type: {file_name}")
                return None
            
            logger.info(f"Successfully extracted archive to {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to extract archive: {str(e)}")
            return None
    
    def should_ignore_path(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if path should be ignored
        """
        path_str = str(path)
        
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                # Handle wildcard patterns
                if path_str.endswith(pattern[1:]):
                    return True
            else:
                # Handle directory/file patterns
                if pattern in path_str:
                    return True
        
        return False
    
    def generate_file_tree(self, project_dir: Path, depth: str = "overview") -> Dict:
        """
        Generate file tree structure based on analysis depth.
        
        Args:
            project_dir: Path to extracted project directory
            depth: Analysis depth ("overview" or "detailed")
            
        Returns:
            Dictionary containing file tree and metadata
        """
        file_tree = {
            "root": str(project_dir),
            "files": [],
            "directories": [],
            "readme_files": [],
            "config_files": [],
            "code_files": []
        }
        
        try:
            # Walk through the project directory
            for root, dirs, files in os.walk(project_dir):
                root_path = Path(root)
                
                # Filter directories
                dirs[:] = [d for d in dirs if not self.should_ignore_path(root_path / d)]
                
                # Process files: loop through all files in the project directory
                for file in files:
                    file_path = root_path / file
                    
                    if self.should_ignore_path(file_path):
                        continue
                    
                    relative_path = file_path.relative_to(project_dir)
                    file_info = {
                        "name": file,
                        "path": str(relative_path),
                        "full_path": str(file_path),
                        "size": file_path.stat().st_size if file_path.exists() else 0
                    }
                    
                    file_tree["files"].append(file_info)
                    
                    # Categorize files based on depth requirements
                    if depth == "overview":
                        # For overview depth, focus on key files (FR-2)
                        if file.lower().startswith('readme'):
                            file_tree["readme_files"].append(file_info)
                        elif file in ['package.json', 'requirements.txt', 'setup.py', 'pyproject.toml', 'Cargo.toml', 'go.mod']:
                            file_tree["config_files"].append(file_info)
                        elif file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
                            # Only top-level code files for overview
                            if len(relative_path.parts) <= 2:
                                file_tree["code_files"].append(file_info)
                    else:
                        # For detailed depth, include all code files
                        if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.html', '.css', '.scss', '.sql']:
                            file_tree["code_files"].append(file_info)
                
                # Add directory information
                for dir_name in dirs:
                    dir_path = root_path / dir_name
                    relative_dir_path = dir_path.relative_to(project_dir)
                    file_tree["directories"].append({
                        "name": dir_name,
                        "path": str(relative_dir_path)
                    })
            
            logger.info(f"Generated file tree with {len(file_tree['files'])} files")
            return file_tree
            
        except Exception as e:
            logger.error(f"Failed to generate file tree: {str(e)}")
            return file_tree
    
    def cleanup_temp_directory(self, temp_dir: Path) -> None:
        """
        Clean up temporary directory after processing.
        
        Args:
            temp_dir: Path to temporary directory to remove
        """
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temporary directory {temp_dir}: {str(e)}")
    
    def process_project(self, uploaded_file, depth: str = "overview") -> Optional[Dict]:
        """
        Main method to process uploaded project file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            depth: Analysis depth ("overview" or "detailed")
            
        Returns:
            Dictionary with project analysis results or None if processing fails
        """
        # Validate upload
        is_valid, error_msg = self.validate_upload(uploaded_file)
        if not is_valid:
            logger.error(f"Upload validation failed: {error_msg}")
            return None
        
        # Extract archive
        temp_dir = self.extract_archive(uploaded_file)
        if temp_dir is None:
            return None
        
        try:
            # Generate file tree
            file_tree = self.generate_file_tree(temp_dir, depth)
            
            # Add metadata
            result = {
                "file_tree": file_tree,
                "analysis_depth": depth,
                "total_files": len(file_tree["files"]),
                "code_files": len(file_tree["code_files"]),
                "readme_files": len(file_tree["readme_files"]),
                "config_files": len(file_tree["config_files"])
            }
            
            return result
            
        finally:
            # Clean up temporary directory
            self.cleanup_temp_directory(temp_dir) 