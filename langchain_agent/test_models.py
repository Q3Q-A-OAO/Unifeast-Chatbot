"""
Test OpenAI Models Availability
==============================

Simple script to check which OpenAI models you have access to.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_openai_models():
    """Test which OpenAI models are available."""
    print("🧪 Testing OpenAI Models Availability")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Create OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Test different models
    models_to_test = [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ]
    
    print("\n🔍 Testing model availability:")
    print("-" * 50)
    
    available_models = []
    
    for model in models_to_test:
        try:
            print(f"Testing {model}...", end=" ")
            
            # Try to create a simple completion
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            print("✅ AVAILABLE")
            available_models.append(model)
            
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg.lower():
                print("❌ QUOTA EXCEEDED")
            elif "model_not_found" in error_msg.lower():
                print("❌ NOT FOUND")
            elif "rate_limit" in error_msg.lower():
                print("⚠️ RATE LIMITED")
            else:
                print(f"❌ ERROR: {error_msg[:50]}...")
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    
    if available_models:
        print("✅ Available models:")
        for model in available_models:
            print(f"   - {model}")
    else:
        print("❌ No models available")
        print("\nPossible reasons:")
        print("1. API quota exceeded - add billing info to OpenAI account")
        print("2. API key invalid - check your OpenAI API key")
        print("3. Account suspended - check OpenAI account status")
    
    print("\n💡 Recommended next steps:")
    print("1. Go to https://platform.openai.com/account/billing")
    print("2. Add payment method to increase quota")
    print("3. Check usage at https://platform.openai.com/usage")
    
    return available_models

def test_simple_completion():
    """Test a simple completion with available models."""
    print("\n🧪 Testing Simple Completion")
    print("=" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Try with gpt-4o-mini (usually has higher quota)
    try:
        print("Testing simple completion with gpt-4o-mini...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Hello from UniFeast!'"}],
            max_tokens=20
        )
        
        print("✅ SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    available_models = test_openai_models()
    test_simple_completion() 