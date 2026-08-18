#!/usr/bin/env python3
"""
PyTekt - Prompt Engineering and Management
==============================================

Prompt templates and helpers: predefined system and user templates, custom
prompts with variable substitution, multi-turn conversation building, code
extraction from model output, length validation, and prompt optimization.
Supports common research and code-review workflows.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import re
from typing import List, Dict, Tuple

def show_prompt(prompt_type: str) -> str:
    """Return and print the template for the given prompt type, or a default prompt if unknown."""
    prompts = get_prompt_templates()
    
    if prompt_type in prompts:
        prompt = prompts[prompt_type]
        print(f"{prompt_type.title()} prompt:\n{prompt}")
        return prompt
    else:
        default_prompt = "Hello, I need assistance with a task."
        print(f"Default prompt:\n{default_prompt}")
        return default_prompt


def get_prompt_templates() -> Dict[str, str]:
    """Return predefined AI prompt templates (system, code_review, debugging, etc.)."""
    return {
        "system": "You are PyTekt, an advanced AI assistant specialized in helping with software development, data science, and AI/ML tasks. You provide accurate, helpful, and detailed responses.",
        
        "code_review": "Please review the following code and provide feedback on:\n1. Code quality and best practices\n2. Potential bugs or issues\n3. Performance optimizations\n4. Readability improvements\n\nCode to review:",
        
        "debugging": "I'm encountering an issue with my code. Please help me debug it by:\n1. Identifying the problem\n2. Explaining why it occurs\n3. Providing a solution\n4. Suggesting prevention strategies\n\nCode and error:",
        
        "optimization": "Please help optimize this code for better performance, readability, or maintainability. Consider:\n1. Algorithm efficiency\n2. Memory usage\n3. Code structure\n4. Best practices\n\nCode to optimize:",
        
        "explanation": "Please explain the following code in detail:\n1. What it does\n2. How it works\n3. Key concepts used\n4. Potential use cases\n\nCode to explain:",
        
        "documentation": "Please help create comprehensive documentation for this code including:\n1. Function/class descriptions\n2. Parameter explanations\n3. Return value descriptions\n4. Usage examples\n\nCode to document:",
        
        "testing": "Please help create unit tests for this code. Include:\n1. Test cases for normal operation\n2. Edge case testing\n3. Error condition testing\n4. Mock data if needed\n\nCode to test:",
        
        "refactoring": "Please suggest refactoring improvements for this code:\n1. Extract methods/classes\n2. Improve naming\n3. Reduce complexity\n4. Follow SOLID principles\n\nCode to refactor:",
        
        "data_analysis": "Please help analyze this dataset or data-related code:\n1. Data exploration insights\n2. Statistical analysis\n3. Visualization suggestions\n4. Quality assessment\n\nData/code to analyze:",
        
        "ml_model": "Please help with this machine learning code:\n1. Model architecture review\n2. Training strategy\n3. Evaluation metrics\n4. Improvement suggestions\n\nML code:",
        
        "api_design": "Please help design or review this API:\n1. Endpoint structure\n2. Request/response formats\n3. Error handling\n4. Documentation\n\nAPI code/specification:"
    }


def create_custom_prompt(template: str, **kwargs) -> str:
    """Format template with {variable} placeholders using kwargs. Raises ValueError on missing key."""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required variable: {e}")


def build_conversation_prompt(messages: List[Dict[str, str]], system_prompt: str = None) -> str:
    """Build a single string from messages (role + content); optionally prepend system_prompt."""
    conversation = []
    
    if system_prompt:
        conversation.append(f"System: {system_prompt}")
    
    for message in messages:
        role = message.get("role", "user").title()
        content = message.get("content", "")
        conversation.append(f"{role}: {content}")
    
    return "\n\n".join(conversation)


def extract_code_from_prompt(prompt: str) -> List[str]:
    """Extract code from triple-backtick blocks and single-backtick inline code."""
    code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)\n?```', prompt, re.DOTALL)
    inline_code = re.findall(r'`([^`]+)`', prompt)
    
    all_code = code_blocks + inline_code
    return [code.strip() for code in all_code if code.strip()]


def validate_prompt_length(prompt: str, max_tokens: int = 4000) -> Tuple[bool, int]:
    """Return (is_valid, estimated_tokens) using ~4 chars per token."""
    estimated_tokens = len(prompt) // 4
    is_valid = estimated_tokens <= max_tokens
    
    return is_valid, estimated_tokens


def optimize_prompt_for_ai(prompt: str) -> str:
    """Add instruction phrasing and a structure request if missing."""
    optimized = prompt.strip()
    if not any(w in optimized.lower() for w in ["please", "help", "analyze", "explain", "create"]):
        optimized = f"Please help with the following: {optimized}"
    if "format" not in optimized.lower() and "structure" not in optimized.lower():
        optimized += "\n\nPlease provide a clear, structured response."
    return optimized