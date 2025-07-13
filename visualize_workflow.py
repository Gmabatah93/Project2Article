"""
LangGraph Workflow Visualization

This script helps visualize the workflow structure and test individual components.
"""

import json
from pathlib import Path
from graph import ArticleGenerationWorkflow
from services.llm_factory import MockLLMClient
from services.parser import ProjectParser

def visualize_workflow_structure():
    """Visualize the LangGraph workflow structure."""
    print("🔄 LangGraph Workflow Structure")
    print("=" * 50)
    
    print("""
    ┌─────────────────┐
    │   Initial State │
    │  (project_analysis, config)
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ PreProcessingNode│
    │ • Extract README │
    │ • Extract config │
    │ • Extract code   │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │SectionPlannerNode│
    │ • Create outline │
    │ • Plan sections  │
    │ • Set tone/style │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ContentGenerator  │
    │ • Generate each  │
    │   section       │
    │ • Apply tone     │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ PostProcessorNode│
    │ • Assemble       │
    │ • Add metadata   │
    │ • Format output  │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  Final Article  │
    │  (Markdown)     │
    └─────────────────┘
    """)

def print_state_schema():
    """Print the workflow state schema."""
    print("\n📋 WorkflowState Schema")
    print("=" * 30)
    
    state_schema = {
        "project_analysis": "Dict - Results from file parsing",
        "config": "Dict - User settings (tone, depth, audience)",
        "extracted_content": "Optional[Dict] - README, config, code summaries",
        "article_plan": "Optional[Dict] - LLM-generated article outline",
        "generated_sections": "Optional[List[str]] - Content for each section",
        "final_article": "Optional[str] - Complete assembled article",
        "error": "Optional[str] - Any error messages"
    }
    
    for key, description in state_schema.items():
        print(f"• {key}: {description}")

def test_individual_nodes():
    """Test each node individually with sample data."""
    print("\n🧪 Testing Individual Nodes")
    print("=" * 30)
    
    # Sample data
    sample_project_analysis = {
        "file_tree": {
            "readme_files": [
                {"path": "README.md", "full_path": "/tmp/test/README.md"}
            ],
            "config_files": [
                {"path": "requirements.txt", "full_path": "/tmp/test/requirements.txt"}
            ],
            "code_files": [
                {"path": "main.py", "full_path": "/tmp/test/main.py"}
            ],
            "files": [],
            "directories": []
        },
        "analysis_depth": "overview",
        "total_files": 3,
        "code_files": 1,
        "readme_files": 1,
        "config_files": 1
    }
    
    sample_config = {
        "analysis_depth": "overview",
        "article_tone": "conversational",
        "llm_provider": "Mock",
        "article_title": "Test Project",
        "target_audience": "intermediate"
    }
    
    # Test PreProcessingNode
    print("\n1️⃣ Testing PreProcessingNode...")
    from graph.nodes import PreProcessingNode
    
    pre_processor = PreProcessingNode()
    initial_state = {
        "project_analysis": sample_project_analysis,
        "config": sample_config,
        "extracted_content": None,
        "article_plan": None,
        "generated_sections": None,
        "final_article": None,
        "error": None
    }
    
    try:
        result_state = pre_processor(initial_state)
        print("✅ PreProcessingNode completed successfully")
        print(f"   - Extracted content keys: {list(result_state['extracted_content'].keys())}")
    except Exception as e:
        print(f"❌ PreProcessingNode failed: {e}")
    
    # Test SectionPlannerNode
    print("\n2️⃣ Testing SectionPlannerNode...")
    from graph.nodes import SectionPlannerNode
    
    mock_llm = MockLLMClient("Test")
    planner = SectionPlannerNode(mock_llm)
    
    try:
        result_state = planner(result_state)
        print("✅ SectionPlannerNode completed successfully")
        print(f"   - Generated {len(result_state['article_plan']['sections'])} sections")
        print(f"   - Title: {result_state['article_plan']['title']}")
    except Exception as e:
        print(f"❌ SectionPlannerNode failed: {e}")
    
    # Test ContentGeneratorNode
    print("\n3️⃣ Testing ContentGeneratorNode...")
    from graph.nodes import ContentGeneratorNode
    
    generator = ContentGeneratorNode(mock_llm)
    
    try:
        result_state = generator(result_state)
        print("✅ ContentGeneratorNode completed successfully")
        print(f"   - Generated {len(result_state['generated_sections'])} sections")
    except Exception as e:
        print(f"❌ ContentGeneratorNode failed: {e}")
    
    # Test PostProcessorNode
    print("\n4️⃣ Testing PostProcessorNode...")
    from graph.nodes import PostProcessorNode
    
    post_processor = PostProcessorNode()
    
    try:
        result_state = post_processor(result_state)
        print("✅ PostProcessorNode completed successfully")
        print(f"   - Final article length: {len(result_state['final_article'])} characters")
    except Exception as e:
        print(f"❌ PostProcessorNode failed: {e}")
    
    return result_state

def test_full_workflow():
    """Test the complete LangGraph workflow."""
    print("\n🚀 Testing Complete LangGraph Workflow")
    print("=" * 40)
    
    # Create sample data
    sample_project_analysis = {
        "file_tree": {
            "readme_files": [
                {"path": "README.md", "full_path": "/tmp/test/README.md"}
            ],
            "config_files": [
                {"path": "requirements.txt", "full_path": "/tmp/test/requirements.txt"}
            ],
            "code_files": [
                {"path": "main.py", "full_path": "/tmp/test/main.py"}
            ],
            "files": [],
            "directories": []
        },
        "analysis_depth": "detailed",
        "total_files": 3,
        "code_files": 1,
        "readme_files": 1,
        "config_files": 1
    }
    
    sample_config = {
        "analysis_depth": "detailed",
        "article_tone": "marketing",
        "llm_provider": "Mock",
        "article_title": "Amazing Test Project",
        "target_audience": "advanced"
    }
    
    # Test workflow
    workflow = ArticleGenerationWorkflow()
    
    try:
        result = workflow.run_workflow(sample_project_analysis, sample_config)
        
        if result["success"]:
            print("✅ Full workflow completed successfully!")
            print(f"   - Article length: {len(result['article'])} characters")
            print(f"   - Workflow state keys: {list(result['workflow_state'].keys())}")
            
            # Show a preview of the generated article
            print("\n📄 Article Preview (first 500 chars):")
            print("-" * 50)
            print(result['article'][:500] + "...")
            
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")

def main():
    """Run all visualization and tests."""
    print("🔍 LangGraph Workflow Analysis")
    print("=" * 50)
    
    # 1. Visualize structure
    visualize_workflow_structure()
    
    # 2. Show state schema
    print_state_schema()
    
    # 3. Test individual nodes
    test_individual_nodes()
    
    # 4. Test full workflow
    test_full_workflow()
    
    print("\n🎉 Analysis complete!")

if __name__ == "__main__":
    main() 