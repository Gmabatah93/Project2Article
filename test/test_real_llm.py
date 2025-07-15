#!/usr/bin/env python3
"""
Test script for real LLM integration.

This script tests the LLM factory with real API keys to ensure
the integration is working correctly.
"""

import os
import sys
from dotenv import load_dotenv
from services.llm_factory import LLMFactory

# Load environment variables from .env file
load_dotenv()

def test_llm_integration():
    """Test LLM integration with different providers."""
    print("🧪 Testing Real LLM Integration")
    print("=" * 50)
    
    factory = LLMFactory()
    
    # Test providers
    providers = [
        ("OpenAI GPT-4", "OPENAI_API_KEY"),
        ("Anthropic Claude", "ANTHROPIC_API_KEY"), 
        ("Google Gemini", "GOOGLE_API_KEY")
    ]
    
    for provider_name, env_var in providers:
        print(f"\n🔍 Testing {provider_name}...")
        
        # Check if API key is available
        api_key = os.getenv(env_var)
        if not api_key:
            print(f"   ⚠️  {env_var} not found in environment")
            print(f"   📝 Using mock client for {provider_name}")
            
            # Test with mock client
            try:
                client = factory.create_client(provider_name)
                response = client.generate_content("Hello, this is a test!")
                print(f"   ✅ Mock client works: {type(response).__name__}")
                print(f"   📄 Response preview: {response.text[:100]}...")
            except Exception as e:
                print(f"   ❌ Mock client failed: {e}")
        else:
            print(f"   🔑 API key found: {api_key[:10]}...")
            
            # Test with real client
            try:
                client = factory.create_client(provider_name, api_key)
                print(f"   ✅ Real client created: {client.get_model_name()}")
                
                # Test a simple prompt
                test_prompt = "Write a one-sentence summary of Python programming."
                response = client.generate_content(test_prompt)
                print(f"   📄 Real response: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Real client failed: {e}")
                print(f"   🔄 Falling back to mock client...")
                
                # Fallback to mock
                try:
                    client = factory.create_client(provider_name)
                    response = client.generate_content("Hello, this is a test!")
                    print(f"   ✅ Mock fallback works")
                except Exception as e2:
                    print(f"   ❌ Mock fallback also failed: {e2}")
    
    print("\n" + "=" * 50)
    print("🎉 LLM Integration Test Complete!")

if __name__ == "__main__":
    test_llm_integration() 