"""
LLM Factory for provider-specific Chat models.

This module creates provider-specific Chat models (OpenAI, Anthropic, Google) via LangChain wrappers.
UI dropdown maps to provider-specific env keys (e.g., OPENAI_API_KEY).
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

# LangChain imports for real LLM integration
try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain packages not available. Install with: pip install langchain-openai langchain-anthropic langchain-google-genai")

# Configure logging
logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate_content(self, prompt: str) -> Any:
        """Generate content from a prompt."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name for this client."""
        pass


class MockLLMClient(LLMClient):
    """Mock LLM client for testing and development."""
    
    def __init__(self, provider_name: str = "Mock"):
        self.provider_name = provider_name
        logger.info(f"Initialized Mock LLM client for {provider_name}")
    
    def generate_content(self, prompt: str) -> Any:
        """Generate mock content for testing."""
        # Simple mock response based on prompt type
        if "planner" in prompt.lower():
            # Determine tone from prompt
            tone = "conversational"
            if "explanatory" in prompt.lower():
                tone = "explanatory"
            elif "marketing" in prompt.lower():
                tone = "marketing"
            
            # Determine depth from prompt
            depth = "overview"
            if "detailed" in prompt.lower():
                depth = "detailed"
            
            # Determine audience from prompt
            audience = "intermediate"
            if "beginner" in prompt.lower():
                audience = "beginner"
            elif "advanced" in prompt.lower():
                audience = "advanced"
            
            # Generate appropriate plan based on parameters
            if depth == "detailed":
                sections = [
                    {
                        "heading": "Introduction",
                        "content_type": "overview",
                        "key_points": ["Project overview", "Main features", "What you'll learn"],
                        "estimated_length": "short"
                    },
                    {
                        "heading": "Architecture Deep Dive",
                        "content_type": "code_analysis",
                        "key_points": ["Code structure", "Key components", "Design patterns"],
                        "estimated_length": "long"
                    },
                    {
                        "heading": "Getting Started",
                        "content_type": "setup",
                        "key_points": ["Prerequisites", "Installation", "Configuration"],
                        "estimated_length": "medium"
                    },
                    {
                        "heading": "Implementation Details",
                        "content_type": "code_analysis",
                        "key_points": ["Core functions", "Data flow", "Error handling"],
                        "estimated_length": "long"
                    },
                    {
                        "heading": "Advanced Features",
                        "content_type": "features",
                        "key_points": ["Advanced functionality", "Customization options", "Performance tips"],
                        "estimated_length": "medium"
                    },
                    {
                        "heading": "Conclusion",
                        "content_type": "conclusion",
                        "key_points": ["Summary", "Next steps", "Resources"],
                        "estimated_length": "short"
                    }
                ]
            else:
                sections = [
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
                ]
            
            plan = {
                "title": "Sample Project Article",
                "sections": sections,
                "tone_notes": f"Use {tone} tone",
                "audience_notes": f"Target {audience} developers"
            }
            
            return MockResponse(json.dumps(plan, indent=2))
        else:
            # Generate section content based on tone
            tone = "conversational"
            if "explanatory" in prompt.lower():
                tone = "explanatory"
            elif "marketing" in prompt.lower():
                tone = "marketing"
            
            if tone == "explanatory":
                content = """## Sample Section Content

This section provides a comprehensive overview of the project's key components and functionality. The implementation follows established best practices and demonstrates effective software engineering principles.

### Key Features

- **Feature 1**: A well-structured component that handles core functionality
- **Feature 2**: An efficient module that processes data with optimal performance
- **Feature 3**: A robust system that ensures reliability and maintainability

### Code Example

```python
def example_function():
    '''Demonstrates proper function documentation and implementation.
    Returns a boolean indicating success status.'''
    print("Hello, World!")
    return True
```

This example illustrates the project's coding standards and architectural patterns."""
            
            elif tone == "marketing":
                content = """## Revolutionary Project Features

Discover the game-changing capabilities that make this project stand out from the competition! You won't believe how this innovative solution can transform your development workflow.

### 🚀 Amazing Features

- **✨ Feature 1**: The most powerful component you've ever seen - it will blow your mind!
- **🔥 Feature 2**: Lightning-fast performance that leaves competitors in the dust
- **💎 Feature 3**: Premium quality that ensures your success every time

### 💻 Incredible Code Example

```python
def amazing_function():
    '''This function is absolutely incredible!'''
    print("Prepare to be amazed!")
    return True  # Guaranteed success!
```

This is just the beginning - wait until you see what else this project can do!"""
            
            else:  # conversational
                content = """## Let's Talk About This Section

Hey there! I'm excited to walk you through this part of the project. When I first started working on this, I had no idea how much fun it would be to build. Let me share what I've learned along the way.

### What I Love About This

- **Feature 1**: This is honestly one of my favorite parts - it just works so smoothly
- **Feature 2**: I spent way too much time on this, but it was totally worth it
- **Feature 3**: You're going to love how easy this makes everything

### Here's Some Code I'm Proud Of

```python
def my_favorite_function():
    '''This function is my baby - I'm really happy with how it turned out!'''
    print("Isn't this cool?")
    return True  # Works like a charm!
```

I hope you find this as useful as I do. Let me know if you have any questions!"""
            
            return MockResponse(content)
    
    def get_model_name(self) -> str:
        """Get the model name for this client."""
        return f"Mock-{self.provider_name}"


class MockResponse:
    """Mock response object to simulate LLM responses."""
    
    def __init__(self, text: str):
        self.text = text


class RealLLMResponse:
    """Real LLM response object."""
    
    def __init__(self, text: str, model_name: str = "Unknown"):
        self.text = text
        self.model_name = model_name


class OpenAILLMClient(LLMClient):
    """OpenAI LLM client using LangChain."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain OpenAI package not available")
        
        self.model = model
        self.client = ChatOpenAI(
            openai_api_key=api_key,
            model=model,
            temperature=0.7,
            max_tokens=4000
        )
        logger.info(f"Initialized OpenAI client with model {model}")
    
    def generate_content(self, prompt: str) -> RealLLMResponse:
        """Generate content using OpenAI."""
        try:
            response = self.client.invoke(prompt)
            return RealLLMResponse(response.content, self.model)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def get_model_name(self) -> str:
        """Get the model name for this client."""
        return self.model


class AnthropicLLMClient(LLMClient):
    """Anthropic LLM client using LangChain."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain Anthropic package not available")
        
        self.model = model
        self.client = ChatAnthropic(
            anthropic_api_key=api_key,
            model=model,
            temperature=0.7,
            max_tokens=4000
        )
        logger.info(f"Initialized Anthropic client with model {model}")
    
    def generate_content(self, prompt: str) -> RealLLMResponse:
        """Generate content using Anthropic."""
        try:
            response = self.client.invoke(prompt)
            return RealLLMResponse(response.content, self.model)
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def get_model_name(self) -> str:
        """Get the model name for this client."""
        return self.model


class GoogleLLMClient(LLMClient):
    """Google LLM client using LangChain."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain Google package not available")
        
        self.model = model
        self.client = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=0.7,
            max_output_tokens=4000
        )
        logger.info(f"Initialized Google client with model {model}")
    
    def generate_content(self, prompt: str) -> RealLLMResponse:
        """Generate content using Google."""
        try:
            response = self.client.invoke(prompt)
            return RealLLMResponse(response.content, self.model)
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise
    
    def get_model_name(self) -> str:
        """Get the model name for this client."""
        return self.model


class LLMFactory:
    """Factory for creating LLM clients based on provider selection."""
    
    def __init__(self):
        self.providers = {
            "OpenAI GPT-4": self._create_openai_client,
            "Anthropic Claude": self._create_anthropic_client,
            "Google Gemini": self._create_google_client
        }
    
    def create_client(self, provider_name: str, api_key: str = None) -> LLMClient:
        """
        Create an LLM client for the specified provider.
        
        Args:
            provider_name: Name of the LLM provider
            api_key: Optional API key (if not provided, will use environment variable)
            
        Returns:
            LLMClient instance
        """
        if provider_name not in self.providers:
            logger.warning(f"Unknown provider '{provider_name}', using mock client")
            return MockLLMClient(provider_name)
        
        try:
            if api_key and api_key != "your-openai-key-here" and api_key != "your-anthropic-key-here" and api_key != "your-google-api-key-here":
                # Use provided API key (only if it's not a placeholder)
                if provider_name == "OpenAI GPT-4":
                    return OpenAILLMClient(api_key, "gpt-4")
                elif provider_name == "Anthropic Claude":
                    return AnthropicLLMClient(api_key, "claude-3-sonnet-20240229")
                elif provider_name == "Google Gemini":
                    return GoogleLLMClient(api_key, "gemini-pro")
            else:
                # Use environment variables
                return self.providers[provider_name]()
        except Exception as e:
            logger.error(f"Failed to create {provider_name} client: {e}")
            logger.info("Falling back to mock client")
            return MockLLMClient(provider_name)
    
    def _create_openai_client(self) -> LLMClient:
        """Create OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found, using mock client")
            return MockLLMClient("OpenAI GPT-4")
        
        try:
            return OpenAILLMClient(api_key, "gpt-4")
        except Exception as e:
            logger.error(f"Failed to create OpenAI client: {e}")
            return MockLLMClient("OpenAI GPT-4")
    
    def _create_anthropic_client(self) -> LLMClient:
        """Create Anthropic client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not found, using mock client")
            return MockLLMClient("Anthropic Claude")
        
        try:
            return AnthropicLLMClient(api_key, "claude-3-sonnet-20240229")
        except Exception as e:
            logger.error(f"Failed to create Anthropic client: {e}")
            return MockLLMClient("Anthropic Claude")
    
    def _create_google_client(self) -> LLMClient:
        """Create Google client."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found, using mock client")
            return MockLLMClient("Google Gemini")
        
        try:
            return GoogleLLMClient(api_key, "gemini-pro")
        except Exception as e:
            logger.error(f"Failed to create Google client: {e}")
            return MockLLMClient("Google Gemini") 