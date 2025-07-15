"""
Detailed LangGraph Workflow Debug Script

This script shows the state transformation at each step of the workflow.
"""

import json
from pprint import pprint
from graph import ArticleGenerationWorkflow
from services.llm_factory import MockLLMClient
from graph.nodes import PreProcessingNode, SectionPlannerNode, ContentGeneratorNode, PostProcessorNode

def debug_workflow_step_by_step():
    """Debug the workflow by running each node individually and showing state changes."""
    print("🔍 Detailed LangGraph Workflow Debug")
    print("=" * 60)
    
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
    
    # Initial state
    initial_state = {
        "project_analysis": sample_project_analysis,
        "config": sample_config,
        "extracted_content": None,
        "article_plan": None,
        "generated_sections": None,
        "final_article": None,
        "error": None
    }
    
    print("\n📋 Initial State:")
    print("-" * 30)
    print(f"• project_analysis: {type(initial_state['project_analysis'])}")
    print(f"• config: {type(initial_state['config'])}")
    print(f"• extracted_content: {initial_state['extracted_content']}")
    print(f"• article_plan: {initial_state['article_plan']}")
    print(f"• generated_sections: {initial_state['generated_sections']}")
    print(f"• final_article: {initial_state['final_article']}")
    print(f"• error: {initial_state['error']}")
    
    # Step 1: PreProcessingNode
    print("\n🔄 Step 1: PreProcessingNode")
    print("-" * 30)
    pre_processor = PreProcessingNode()
    state_after_preprocessing = pre_processor(initial_state.copy())
    
    print("✅ PreProcessingNode completed")
    print(f"• extracted_content keys: {list(state_after_preprocessing['extracted_content'].keys())}")
    print(f"• readme_content length: {len(state_after_preprocessing['extracted_content']['readme_content'])} chars")
    print(f"• config_content length: {len(state_after_preprocessing['extracted_content']['config_content'])} chars")
    print(f"• code_files_info length: {len(state_after_preprocessing['extracted_content']['code_files_info'])} chars")
    
    # Step 2: SectionPlannerNode
    print("\n🔄 Step 2: SectionPlannerNode")
    print("-" * 30)
    mock_llm = MockLLMClient("Test")
    section_planner = SectionPlannerNode(mock_llm)
    state_after_planning = section_planner(state_after_preprocessing.copy())
    
    print("✅ SectionPlannerNode completed")
    print(f"• article_plan keys: {list(state_after_planning['article_plan'].keys())}")
    print(f"• title: {state_after_planning['article_plan']['title']}")
    print(f"• sections count: {len(state_after_planning['article_plan']['sections'])}")
    print(f"• tone_notes: {state_after_planning['article_plan']['tone_notes']}")
    print(f"• audience_notes: {state_after_planning['article_plan']['audience_notes']}")
    
    # Show section details
    print("\n📝 Generated Sections Plan:")
    for i, section in enumerate(state_after_planning['article_plan']['sections']):
        print(f"  {i+1}. {section['heading']} ({section['content_type']})")
        print(f"     Key points: {', '.join(section['key_points'])}")
        print(f"     Length: {section['estimated_length']}")
    
    # Step 3: ContentGeneratorNode
    print("\n🔄 Step 3: ContentGeneratorNode")
    print("-" * 30)
    content_generator = ContentGeneratorNode(mock_llm)
    state_after_content = content_generator(state_after_planning.copy())
    
    print("✅ ContentGeneratorNode completed")
    print(f"• generated_sections count: {len(state_after_content['generated_sections'])}")
    
    # Show content preview for each section
    print("\n📄 Generated Content Preview:")
    for i, section_content in enumerate(state_after_content['generated_sections']):
        print(f"\n  Section {i+1}:")
        print(f"  Length: {len(section_content)} characters")
        print(f"  Preview: {section_content[:100]}...")
    
    # Step 4: PostProcessorNode
    print("\n🔄 Step 4: PostProcessorNode")
    print("-" * 30)
    post_processor = PostProcessorNode()
    final_state = post_processor(state_after_content.copy())
    
    print("✅ PostProcessorNode completed")
    print(f"• final_article length: {len(final_state['final_article'])} characters")
    
    # Show final article structure
    print("\n📄 Final Article Structure:")
    lines = final_state['final_article'].split('\n')
    for i, line in enumerate(lines[:20]):  # Show first 20 lines
        if line.strip():
            print(f"  {i+1:2d}: {line}")
    if len(lines) > 20:
        print(f"  ... and {len(lines) - 20} more lines")
    
    return final_state

def test_workflow_with_different_configs():
    """Test the workflow with different configurations."""
    print("\n🧪 Testing Different Configurations")
    print("=" * 50)
    
    # Test configurations
    configs = [
        {
            "name": "Explanatory + Beginner",
            "config": {
                "analysis_depth": "overview",
                "article_tone": "explanatory",
                "llm_provider": "Mock",
                "article_title": "Beginner-Friendly Project",
                "target_audience": "beginner"
            }
        },
        {
            "name": "Marketing + Advanced",
            "config": {
                "analysis_depth": "detailed",
                "article_tone": "marketing",
                "llm_provider": "Mock",
                "article_title": "Advanced Project Showcase",
                "target_audience": "advanced"
            }
        },
        {
            "name": "Conversational + Intermediate",
            "config": {
                "analysis_depth": "detailed",
                "article_tone": "conversational",
                "llm_provider": "Mock",
                "article_title": "My Cool Project",
                "target_audience": "intermediate"
            }
        }
    ]
    
    sample_project_analysis = {
        "file_tree": {
            "readme_files": [{"path": "README.md", "full_path": "/tmp/test/README.md"}],
            "config_files": [{"path": "requirements.txt", "full_path": "/tmp/test/requirements.txt"}],
            "code_files": [{"path": "main.py", "full_path": "/tmp/test/main.py"}],
            "files": [],
            "directories": []
        },
        "analysis_depth": "detailed",
        "total_files": 3,
        "code_files": 1,
        "readme_files": 1,
        "config_files": 1
    }
    
    workflow = ArticleGenerationWorkflow()
    
    for test_config in configs:
        print(f"\n🔧 Testing: {test_config['name']}")
        print("-" * 30)
        
        try:
            result = workflow.run_workflow(sample_project_analysis, test_config['config'])
            
            if result["success"]:
                print(f"✅ Success! Article length: {len(result['article'])} chars")
                
                # Show tone-specific content
                if "marketing" in test_config['config']['article_tone']:
                    if "🚀" in result['article'] or "amazing" in result['article'].lower():
                        print("✅ Marketing tone detected in content")
                elif "conversational" in test_config['config']['article_tone']:
                    if "I" in result['article'] and "you" in result['article']:
                        print("✅ Conversational tone detected in content")
                elif "explanatory" in test_config['config']['article_tone']:
                    if "This section provides" in result['article']:
                        print("✅ Explanatory tone detected in content")
                
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def main():
    """Run all debug tests."""
    # Step-by-step debug
    final_state = debug_workflow_step_by_step()
    
    # Test different configurations
    test_workflow_with_different_configs()
    
    print("\n🎉 Debug complete!")

if __name__ == "__main__":
    main() 