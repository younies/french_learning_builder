#!/usr/bin/env python3
"""
Example usage of the TCF Orale Generator

This script demonstrates different ways to use the orale_generator.py
"""

from orale_generator import TCFOraleGenerator

def example_basic_usage():
    """Basic usage example"""
    print("🔥 Example 1: Basic Usage")
    print("-" * 30)
    
    # Initialize generator (requires OPENAI_API_KEY environment variable)
    generator = TCFOraleGenerator()
    
    # Preview topics without generating
    generator.preview_topics(3)
    
    # Generate limited content (just 2 topics each for testing)
    generator.generate_all_content(task2_limit=2, task3_limit=2)

def example_custom_directory():
    """Example with custom output directory"""
    print("\n🔥 Example 2: Custom Directory")
    print("-" * 30)
    
    # Use custom output directory
    custom_dir = "/Users/youniesmahmoud/Desktop/tcf_practice"
    generator = TCFOraleGenerator(output_base_dir=custom_dir)
    
    # Generate content
    generator.generate_all_content(task2_limit=1, task3_limit=1)

def example_task_specific():
    """Example generating only specific task"""
    print("\n🔥 Example 3: Task-Specific Generation")
    print("-" * 30)
    
    generator = TCFOraleGenerator()
    
    # Load topics
    task2_topics, task3_topics = generator.load_organized_topics()
    
    # Generate only Task 2 content
    generator.generate_task2_content(task2_topics, limit=3)
    
    # Or generate only Task 3 content
    # generator.generate_task3_content(task3_topics, limit=3)

def example_with_api_key():
    """Example passing API key directly"""
    print("\n🔥 Example 4: Direct API Key")
    print("-" * 30)
    
    # Pass API key directly (alternative to environment variable)
    api_key = "your-openai-api-key-here"  # Replace with actual key
    
    try:
        generator = TCFOraleGenerator(api_key=api_key)
        generator.preview_topics(2)
    except ValueError as e:
        print(f"❌ {e}")
        print("💡 Replace 'your-openai-api-key-here' with your actual OpenAI API key")

def main():
    """Run examples"""
    print("🎓 TCF Orale Generator - Usage Examples")
    print("=" * 50)
    
    print("⚠️  Note: These examples require a valid OpenAI API key")
    print("   Set: export OPENAI_API_KEY='your-key-here'")
    print("   Or pass it directly to TCFOraleGenerator(api_key='...')")
    
    # Uncomment the examples you want to run:
    
    # example_basic_usage()
    # example_custom_directory() 
    # example_task_specific()
    example_with_api_key()  # Safe to run (just shows error message)

if __name__ == "__main__":
    main()
