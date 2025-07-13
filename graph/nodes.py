"""
LangGraph nodes for article generation workflow.

This module implements the nodes described in FR-3 using the actual LangGraph framework:
- Pre-processing node (code & metadata extractor)
- Section Planner node (decide headings based on depth & tone)
- Content Generator node (LLM writes each section with stream output)
- Post-processor node (assemble markdown & add code snippets with explanations)
"""

import json
import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from pathlib import Path

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Configure logging
logger = logging.getLogger(__name__)


# Define the state schema for our workflow
class WorkflowState(TypedDict):
    """State schema for the article generation workflow."""
    project_analysis: Dict
    config: Dict
    extracted_content: Optional[Dict]
    article_plan: Optional[Dict]
    generated_sections: Optional[List[str]]
    final_article: Optional[str]
    error: Optional[str]


class PreProcessingNode:
    """
    Node 1: Pre-processing → code & metadata extractor.

    This node's job is to read the project files and extract all the raw text needed for the AI to understand the project. 
    It doesn't use AI itself; it's purely for data preparation
    
    What it does:
    - Extracts content from README files
    - Extracts content from configuration files
    - Extracts summaries of code files
    - Creates a project structure summary
    - Stores the extracted content in the state

    How it works:
    - The node is initialized with a name
    - The node has a method to extract content from README files
    - The node has a method to extract content from configuration files
    - The node has a method to extract summaries of code files
    - The node has a method to create a project structure summary
    - The node has a method to store the extracted content in the state
    """
    
    def __init__(self):
        self.name = "pre_processor"
    
    # 1. Extract content from README files
    def extract_readme_content(self, file_tree: Dict) -> str:
        """Extract content from README files."""
        readme_content = ""
        
        for readme_file in file_tree.get("readme_files", []):
            try:
                file_path = Path(readme_file["full_path"])
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    readme_content += f"\n## {readme_file['path']}\n{content}\n"
            except Exception as e:
                logger.warning(f"Failed to read README file {readme_file['path']}: {e}")
        
        return readme_content.strip()
    
    def extract_config_content(self, file_tree: Dict) -> str:
        """Extract content from configuration files."""
        config_content = ""
        
        for config_file in file_tree.get("config_files", []):
            try:
                file_path = Path(config_file["full_path"])
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    config_content += f"\n## {config_file['path']}\n```\n{content}\n```\n"
            except Exception as e:
                logger.warning(f"Failed to read config file {config_file['path']}: {e}")
        
        return config_content.strip()
    
    def extract_code_summaries(self, file_tree: Dict, depth: str = "overview") -> str:
        """Extract summaries of code files based on analysis depth."""
        code_summaries = []
        
        for code_file in file_tree.get("code_files", []):
            try:
                file_path = Path(code_file["full_path"])
                if file_path.exists():
                    file_info = {
                        "path": code_file["path"],
                        "name": code_file["name"],
                        "size": code_file["size"]
                    }
                    
                    # For detailed depth, include code content
                    if depth == "detailed":
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            # Limit content to first 2000 characters to avoid token limits
                            file_info["content"] = content[:2000] + ("..." if len(content) > 2000 else "")
                            file_info["full_content"] = len(content) > 2000
                        except Exception as e:
                            logger.warning(f"Failed to read code file {code_file['path']}: {e}")
                            file_info["content"] = "# Error reading file content"
                    
                    code_summaries.append(file_info)
            except Exception as e:
                logger.warning(f"Failed to process code file {code_file['path']}: {e}")
        
        return json.dumps(code_summaries, indent=2)
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        """Run the pre-processing node."""
        logger.info("Starting pre-processing node")
        
        try:
            file_tree = state["project_analysis"]["file_tree"]
            
            # Extract content from different file types
            readme_content = self.extract_readme_content(file_tree)
            config_content = self.extract_config_content(file_tree)
            depth = state["project_analysis"]["analysis_depth"]
            code_files_info = self.extract_code_summaries(file_tree, depth)
            
            # Create project structure summary
            project_structure = {
                "total_files": len(file_tree["files"]),
                "directories": [d["path"] for d in file_tree["directories"]],
                "file_types": {}
            }
            
            # Count file types
            for file_info in file_tree["files"]:
                ext = Path(file_info["name"]).suffix
                project_structure["file_types"][ext] = project_structure["file_types"].get(ext, 0) + 1
            
            # Update state with extracted content
            state["extracted_content"] = {
                "readme_content": readme_content,
                "config_content": config_content,
                "code_files_info": code_files_info,
                "project_structure": json.dumps(project_structure, indent=2)
            }
            
            logger.info("Pre-processing node completed")
            
        except Exception as e:
            logger.error(f"Pre-processing failed: {e}")
            state["error"] = f"Pre-processing failed: {str(e)}"
        
        return state


class SectionPlannerNode:
    """
    Node 2: Section Planner → decide headings based on depth & tone.
    
    How it works:
    - The node is initialized with a name
    - The node has a method to load the planner prompt
    - The node has a method to format the planner prompt with project data
    - The node has a method to create a fallback plan if the LLM fails
    - The node has a method to call the LLM and parse the response
    - The node has a method to store the generated plan in the state
    """
    
    def __init__(self, llm_client):
        self.name = "section_planner"
        self.llm_client = llm_client
    
    # 1. Load the planner prompt
    def load_planner_prompt(self) -> str:
        """Load the planner prompt template."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "planner_prompt.txt"
        return prompt_path.read_text(encoding='utf-8')
    
    # 2. Format the planner prompt with project data
    def format_planner_prompt(self, state: WorkflowState) -> str:
        """Format the planner prompt with project data."""
        prompt_template = self.load_planner_prompt()
        
        analysis = state["project_analysis"]
        config = state["config"]
        
        # Format file lists for prompt
        readme_files_list = [f["path"] for f in analysis["file_tree"]["readme_files"]]
        config_files_list = [f["path"] for f in analysis["file_tree"]["config_files"]]
        code_files_list = [f["path"] for f in analysis["file_tree"]["code_files"]]
        
        return prompt_template.format(
            project_name=config.get("article_title", "Project"),
            analysis_depth=config["analysis_depth"],
            article_tone=config["article_tone"],
            target_audience=config["target_audience"],
            total_files=analysis["total_files"],
            code_files=analysis["code_files"],
            readme_files=analysis["readme_files"],
            config_files=analysis["config_files"],
            readme_files_list=readme_files_list,
            config_files_list=config_files_list,
            code_files_list=code_files_list
        )
    
    # IF LLM FAILS: Create a fallback plan if the LLM fails
    def create_fallback_plan(self, state: WorkflowState) -> Dict:
        """Create a fallback plan if LLM fails."""
        config = state["config"]
        
        return {
            "title": config.get("article_title", "Project Overview"),
            "sections": [
                {
                    "heading": "Introduction",
                    "content_type": "overview",
                    "key_points": ["Project overview", "Main features", "What you'll learn"],
                    "estimated_length": "short"
                },
                {
                    "heading": "Getting Started",
                    "content_type": "setup",
                    "key_points": ["Prerequisites", "Installation", "Configuration"],
                    "estimated_length": "medium"
                },
                {
                    "heading": "Features and Usage",
                    "content_type": "features",
                    "key_points": ["Main functionality", "Key features", "Usage examples"],
                    "estimated_length": "medium"
                },
                {
                    "heading": "Conclusion",
                    "content_type": "conclusion",
                    "key_points": ["Summary", "Next steps", "Resources"],
                    "estimated_length": "short"
                }
            ],
            "tone_notes": f"Use {config['article_tone'].lower()} tone",
            "audience_notes": f"Target {config['target_audience'].lower()} developers"
        }
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        """Run the section planner node."""
        logger.info("Starting section planner node")
        
        try:
            # Format the prompt
            prompt = self.format_planner_prompt(state)
            
            # Get response from LLM
            response = self.llm_client.generate_content(prompt)
            
            # Parse the JSON response
            try:
                plan = json.loads(response.text)
                state["article_plan"] = plan
                logger.info(f"Generated plan with {len(plan.get('sections', []))} sections")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Fallback to a basic plan
                state["article_plan"] = self.create_fallback_plan(state)
            
        except Exception as e:
            logger.error(f"Section planner failed: {e}")
            state["article_plan"] = self.create_fallback_plan(state)
        
        return state


class ContentGeneratorNode:
    """Node 3: Content Generator → LLM writes each section (stream output)."""
    
    def __init__(self, llm_client):
        self.name = "content_generator"
        self.llm_client = llm_client
    
    def load_section_prompt(self) -> str:
        """Load the section prompt template."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "section_prompt.txt"
        return prompt_path.read_text(encoding='utf-8')
    
    def format_section_prompt(self, section: Dict, state: WorkflowState) -> str:
        """Format the section prompt with section data."""
        prompt_template = self.load_section_prompt()
        
        config = state["config"]
        extracted_content = state["extracted_content"]
        
        return prompt_template.format(
            article_tone=config["article_tone"],
            target_audience=config["target_audience"],
            project_name=config.get("article_title", "Project"),
            section_heading=section["heading"],
            content_type=section["content_type"],
            key_points=", ".join(section["key_points"]),
            tone_notes=state["article_plan"]["tone_notes"],
            audience_notes=state["article_plan"]["audience_notes"],
            readme_content=extracted_content["readme_content"],
            config_content=extracted_content["config_content"],
            code_files_info=extracted_content["code_files_info"],
            project_structure=extracted_content["project_structure"]
        )
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        """Run the content generator node."""
        logger.info("Starting content generator node")
        
        try:
            sections_content = []
            plan = state["article_plan"]
            
            for i, section in enumerate(plan["sections"]):
                logger.info(f"Generating content for section {i+1}/{len(plan['sections'])}: {section['heading']}")
                
                try:
                    # Format the prompt for this section
                    prompt = self.format_section_prompt(section, state)
                    
                    # Get response from LLM
                    response = self.llm_client.generate_content(prompt)
                    
                    # Add section content
                    section_content = f"## {section['heading']}\n\n{response.text}\n\n"
                    sections_content.append(section_content)
                    
                except Exception as e:
                    logger.error(f"Failed to generate content for section '{section['heading']}': {e}")
                    # Add fallback content
                    fallback_content = f"## {section['heading']}\n\n*Content generation for this section encountered an error. Please review the project files manually.*\n\n"
                    sections_content.append(fallback_content)
            
            # Store generated content
            state["generated_sections"] = sections_content
            logger.info(f"Generated content for {len(sections_content)} sections")
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            state["error"] = f"Content generation failed: {str(e)}"
        
        return state


class PostProcessorNode:
    """Node 4: Post-processor → assemble markdown & add code snippets with explanations."""
    
    def __init__(self):
        self.name = "post_processor"
    
    def assemble_article(self, state: WorkflowState) -> str:
        """Assemble the final article from generated sections."""
        plan = state["article_plan"]
        sections_content = state["generated_sections"]
        
        # Start with title
        article = f"# {plan['title']}\n\n"
        
        # Add sections
        for section_content in sections_content:
            article += section_content
        
        # Add metadata footer
        article += self.add_metadata_footer(state)
        
        return article
    
    def add_metadata_footer(self, state: WorkflowState) -> str:
        """Add metadata footer to the article."""
        config = state["config"]
        analysis = state["project_analysis"]
        
        footer = f"""
---

## Article Information

- **Generated by**: Project-to-Article Generator
- **Analysis Depth**: {config['analysis_depth'].title()}
- **Article Tone**: {config['article_tone']}
- **Target Audience**: {config['target_audience']}
- **Project Files Analyzed**: {analysis['total_files']}
- **Code Files**: {analysis['code_files']}
- **README Files**: {analysis['readme_files']}
- **Configuration Files**: {analysis['config_files']}

*This article was automatically generated from your project files. Please review and edit as needed before publishing.*
"""
        return footer
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        """Run the post-processor node."""
        logger.info("Starting post-processor node")
        
        try:
            # Assemble the final article
            final_article = self.assemble_article(state)
            
            # Store the final article
            state["final_article"] = final_article
            
            logger.info("Post-processor node completed")
            
        except Exception as e:
            logger.error(f"Post-processor failed: {e}")
            state["error"] = f"Post-processor failed: {str(e)}"
        
        return state


def create_workflow_graph(llm_client) -> StateGraph:
    """Create the LangGraph workflow."""
    
    # Create the state graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    pre_processor = PreProcessingNode()
    section_planner = SectionPlannerNode(llm_client)
    content_generator = ContentGeneratorNode(llm_client)
    post_processor = PostProcessorNode()
    
    workflow.add_node("pre_processor", pre_processor)
    workflow.add_node("section_planner", section_planner)
    workflow.add_node("content_generator", content_generator)
    workflow.add_node("post_processor", post_processor)
    
    # Define the workflow edges
    workflow.set_entry_point("pre_processor")
    workflow.add_edge("pre_processor", "section_planner")
    workflow.add_edge("section_planner", "content_generator")
    workflow.add_edge("content_generator", "post_processor")
    workflow.add_edge("post_processor", END)
    
    # Compile the graph
    return workflow.compile(checkpointer=MemorySaver()) 