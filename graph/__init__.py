"""
LangGraph workflow for article generation.

This module implements the main workflow that orchestrates the article generation process
using the actual LangGraph framework.

By placing the ArticleGenerationWorkflow class in the __init__.py file, we can easily import it into other modules.

Example:
    from graph import ArticleGenerationWorkflow
    workflow = ArticleGenerationWorkflow()
    workflow.run_workflow(project_analysis, config)
"""

import logging
from typing import Dict, Any
from .nodes import create_workflow_graph, WorkflowState
from services.llm_factory import LLMFactory

# Configure logging
logger = logging.getLogger(__name__)


class ArticleGenerationWorkflow:
    """Main workflow for generating articles from project analysis using LangGraph."""
    
    def __init__(self):
        self.llm_factory = LLMFactory() # responsible for creating a client for a specific LLM provider
        self._workflow = None           # responsible for creating the workflow graph
    
    def _get_workflow(self, llm_client):
        """Get or create the LangGraph workflow."""
        if self._workflow is None:
            self._workflow = create_workflow_graph(llm_client) # creates the workflow graph
        return self._workflow
    
    def create_workflow_state(self, project_analysis: Dict, config: Dict) -> WorkflowState:
        """Create the initial state for the workflow."""
        return {
            "project_analysis": project_analysis,  # contains info about the project files
            "config": config,                      # desired tone and depth
            "extracted_content": None,
            "article_plan": None,
            "generated_sections": None,
            "final_article": None,
            "error": None
        }
    
    def run_workflow(self, project_analysis: Dict, config: Dict) -> Dict:
        """
        Run the complete article generation workflow using LangGraph.
        
        Args:
            project_analysis: Results from project parsing
            config: User configuration (tone, depth, etc.)
            
        Returns:
            Dictionary containing the final article and workflow state
        """
        logger.info("Starting LangGraph article generation workflow")
        
        try:
            # Create LLM client
            api_key = config.get("api_key")
            llm_client = self.llm_factory.create_client(config["llm_provider"], api_key)
            
            # Get the LangGraph workflow
            workflow = self._get_workflow(llm_client)
            
            # Create initial state
            initial_state = self.create_workflow_state(project_analysis, config)
            
            # Run the workflow with thread_id for checkpointing
            logger.info("Executing LangGraph workflow")
            result = workflow.invoke(initial_state, {"configurable": {"thread_id": "test-thread"}})
            
            # Check for errors
            if result.get("error"):
                logger.error(f"Workflow failed: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "article": "# Error Generating Article\n\nAn error occurred during article generation. Please try again."
                }
            
            # Extract the final article
            final_article = result.get("final_article", "# Error: No article generated")
            
            logger.info("LangGraph workflow completed successfully")
            
            return {
                "success": True,
                "article": final_article,
                "workflow_state": result
            }
            
        except Exception as e:
            logger.error(f"LangGraph workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "article": "# Error Generating Article\n\nAn error occurred during article generation. Please try again."
            }
    
    def get_workflow_status(self, state: WorkflowState) -> Dict:
        """Get the current status of the workflow."""
        return {
            "pre_processing_complete": state.get("extracted_content") is not None,
            "planning_complete": state.get("article_plan") is not None,
            "content_generation_complete": state.get("generated_sections") is not None,
            "post_processing_complete": state.get("final_article") is not None,
            "has_error": state.get("error") is not None
        } 