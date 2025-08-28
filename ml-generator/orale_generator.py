import json
import os
from openai import OpenAI
from typing import List, Dict, Optional, Tuple
import time
import re
from pathlib import Path

class TCFOraleGenerator:
    """
    Generator for TCF Canada Expression Orale practice materials using OpenAI
    """
    
    def __init__(self, api_key: Optional[str] = None, output_base_dir: str = "/Users/youniesmahmoud/study/french_learning/tcf_canada/eo"):
        """
        Initialize the generator
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            output_base_dir: Base directory for output files
        """
        # Set up OpenAI client
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            self.client = OpenAI(api_key=api_key)
        
        self.output_base_dir = output_base_dir
        self.task2_dir = os.path.join(output_base_dir, "task2")
        self.task3_dir = os.path.join(output_base_dir, "task3")
        
        # Load prompts
        self.task2_prompt = self._load_prompt("ml-generator/eo_task2_prompt.txt")
        self.task3_prompt = self._load_prompt("ml-generator/eo_task3_prompt.txt")
        
        # Statistics
        self.stats = {
            "task2_generated": 0,
            "task3_generated": 0,
            "total_api_calls": 0,
            "errors": 0,
            "skipped": 0
        }
    
    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt from file"""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    def _create_directories(self) -> None:
        """Create output directories if they don't exist"""
        os.makedirs(self.task2_dir, exist_ok=True)
        os.makedirs(self.task3_dir, exist_ok=True)
        print(f"📁 Created directories:")
        print(f"   - Task 2: {self.task2_dir}")
        print(f"   - Task 3: {self.task3_dir}")
    
    def _sanitize_filename(self, content: str, max_length: int = 100) -> str:
        """
        Create a safe filename from topic content
        """
        # Take first part of content for filename
        filename = content[:max_length]
        
        # Remove or replace unsafe characters
        filename = re.sub(r'[^\w\s\-.]', '', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('_')
        
        # Ensure it's not empty
        if not filename:
            filename = "topic"
        
        return filename + ".md"
    
    def _call_openai(self, prompt: str, topic_content: str, max_retries: int = 3) -> Optional[str]:
        """
        Make API call to OpenAI with retry logic
        """
        full_prompt = f"{prompt}\n\n---\n\n**TOPIC:** {topic_content}"
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper option
                    messages=[
                        {"role": "system", "content": "You are a French language expert and TCF Canada examiner."},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                
                self.stats["total_api_calls"] += 1
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Handle rate limit errors
                if "rate limit" in error_str or "quota" in error_str:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"   ⏳ Rate limit hit, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                
                # Handle API errors
                elif "api" in error_str or "request" in error_str:
                    print(f"   ❌ API Error (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        self.stats["errors"] += 1
                        return None
                    time.sleep(1)
                    continue
                
                # Handle other errors
                else:
                    print(f"   ❌ Unexpected error (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        self.stats["errors"] += 1
                        return None
                    time.sleep(1)
                    continue
        
        return None
    
    def _save_markdown_file(self, content: str, filepath: str, topic_info: Dict) -> bool:
        """
        Save generated content to markdown file with metadata
        """
        try:
            # Add metadata header
            metadata = f"""---
# TCF Canada Expression Orale - Generated Practice
source_file: {topic_info.get('source_file', 'unknown')}
source_url: {topic_info.get('source_url', 'unknown')}
task: {topic_info.get('task', 'unknown')}
part: {topic_info.get('part', 'unknown')}
generated_at: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

# Original Topic
{topic_info.get('content', 'No content available')}

---

"""
            
            full_content = metadata + content
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving file {filepath}: {e}")
            return False
    
    def load_organized_topics(self, json_file: str = "organized_topics.json") -> Tuple[List[Dict], List[Dict]]:
        """
        Load topics from organized_topics.json
        
        Returns:
            (task2_topics, task3_topics)
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            task2_topics = data.get('task2_topics', [])
            task3_topics = data.get('task3_topics', [])
            
            print(f"📊 Loaded topics:")
            print(f"   - Task 2: {len(task2_topics)} topics")
            print(f"   - Task 3: {len(task3_topics)} topics")
            
            return task2_topics, task3_topics
            
        except FileNotFoundError:
            print(f"❌ File not found: {json_file}")
            return [], []
        except Exception as e:
            print(f"❌ Error loading topics: {e}")
            return [], []
    
    def generate_task2_content(self, topics: List[Dict], limit: Optional[int] = None) -> None:
        """
        Generate Task 2 practice content for given topics
        """
        if limit:
            topics = topics[:limit]
        
        print(f"\n🎯 Generating Task 2 content for {len(topics)} topics...")
        
        for i, topic in enumerate(topics, 1):
            print(f"\n📝 Processing Task 2 topic {i}/{len(topics)}")
            print(f"   Content: {topic['content'][:80]}...")
            
            # Generate content with OpenAI
            generated_content = self._call_openai(self.task2_prompt, topic['content'])
            
            if generated_content:
                # Create filename
                filename = self._sanitize_filename(topic['content'])
                filepath = os.path.join(self.task2_dir, f"task2_{i:03d}_{filename}")
                
                # Save file
                if self._save_markdown_file(generated_content, filepath, topic):
                    print(f"   ✅ Saved: {os.path.basename(filepath)}")
                    self.stats["task2_generated"] += 1
                else:
                    self.stats["errors"] += 1
            else:
                print(f"   ❌ Failed to generate content")
                self.stats["skipped"] += 1
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
    
    def generate_task3_content(self, topics: List[Dict], limit: Optional[int] = None) -> None:
        """
        Generate Task 3 practice content for given topics
        """
        if limit:
            topics = topics[:limit]
        
        print(f"\n🎯 Generating Task 3 content for {len(topics)} topics...")
        
        for i, topic in enumerate(topics, 1):
            print(f"\n📝 Processing Task 3 topic {i}/{len(topics)}")
            print(f"   Content: {topic['content'][:80]}...")
            
            # Generate content with OpenAI
            generated_content = self._call_openai(self.task3_prompt, topic['content'])
            
            if generated_content:
                # Create filename
                filename = self._sanitize_filename(topic['content'])
                filepath = os.path.join(self.task3_dir, f"task3_{i:03d}_{filename}")
                
                # Save file
                if self._save_markdown_file(generated_content, filepath, topic):
                    print(f"   ✅ Saved: {os.path.basename(filepath)}")
                    self.stats["task3_generated"] += 1
                else:
                    self.stats["errors"] += 1
            else:
                print(f"   ❌ Failed to generate content")
                self.stats["skipped"] += 1
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
    
    def generate_all_content(self, task2_limit: Optional[int] = None, task3_limit: Optional[int] = None) -> None:
        """
        Generate all content for both tasks
        """
        print("🚀 Starting TCF Orale Content Generation...")
        
        # Create directories
        self._create_directories()
        
        # Load topics
        task2_topics, task3_topics = self.load_organized_topics()
        
        if not task2_topics and not task3_topics:
            print("❌ No topics loaded. Exiting.")
            return
        
        # Generate Task 2 content
        if task2_topics:
            self.generate_task2_content(task2_topics, task2_limit)
        
        # Generate Task 3 content
        if task3_topics:
            self.generate_task3_content(task3_topics, task3_limit)
        
        # Print final statistics
        self._print_final_stats()
    
    def _print_final_stats(self) -> None:
        """Print generation statistics"""
        print(f"\n{'='*60}")
        print("GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"📊 Statistics:")
        print(f"   - Task 2 files generated: {self.stats['task2_generated']}")
        print(f"   - Task 3 files generated: {self.stats['task3_generated']}")
        print(f"   - Total API calls made: {self.stats['total_api_calls']}")
        print(f"   - Errors encountered: {self.stats['errors']}")
        print(f"   - Topics skipped: {self.stats['skipped']}")
        
        total_generated = self.stats['task2_generated'] + self.stats['task3_generated']
        print(f"   - Total files created: {total_generated}")
        
        print(f"\n📁 Output directories:")
        print(f"   - Task 2: {self.task2_dir}")
        print(f"   - Task 3: {self.task3_dir}")
    
    def preview_topics(self, num_samples: int = 3) -> None:
        """
        Preview some topics without generating content
        """
        print("👀 Previewing topics...")
        
        task2_topics, task3_topics = self.load_organized_topics()
        
        print(f"\n🎯 Task 2 Sample Topics ({len(task2_topics)} total):")
        for i, topic in enumerate(task2_topics[:num_samples], 1):
            print(f"   {i}. {topic['content'][:100]}...")
        
        print(f"\n🎯 Task 3 Sample Topics ({len(task3_topics)} total):")
        for i, topic in enumerate(task3_topics[:num_samples], 1):
            print(f"   {i}. {topic['content'][:100]}...")


def main():
    """
    Main function with example usage
    """
    print("🎓 TCF Canada Expression Orale Generator")
    print("=" * 50)
    
    # Initialize generator
    try:
        generator = TCFOraleGenerator()
    except ValueError as e:
        print(f"❌ {e}")
        print("💡 Set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Preview topics
    generator.preview_topics(5)
    
    # Ask user for limits
    print(f"\n🔧 Configuration:")
    
    try:
        task2_limit = input("Enter limit for Task 2 topics (press Enter for all): ").strip()
        task2_limit = int(task2_limit) if task2_limit else None
        
        task3_limit = input("Enter limit for Task 3 topics (press Enter for all): ").strip()
        task3_limit = int(task3_limit) if task3_limit else None
        
        print(f"\n📋 Will generate:")
        print(f"   - Task 2: {task2_limit or 'all'} topics")
        print(f"   - Task 3: {task3_limit or 'all'} topics")
        
        confirm = input("\nProceed with generation? (y/N): ").strip().lower()
        
        if confirm == 'y':
            # Generate content
            generator.generate_all_content(task2_limit, task3_limit)
        else:
            print("❌ Generation cancelled.")
            
    except KeyboardInterrupt:
        print("\n❌ Generation interrupted by user.")
    except Exception as e:
        print(f"❌ Error during generation: {e}")


if __name__ == "__main__":
    main()
