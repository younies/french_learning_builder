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
    
    def __init__(self, api_key: Optional[str] = None, output_base_dir: Optional[str] = None):
        """
        Initialize the generator
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            output_base_dir: Base directory for output files. If None, defaults to
                             a sibling folder '../french_learning/tcf_canada/eo'
                             relative to the project root.
        """
        # Set up OpenAI client
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            self.client = OpenAI(api_key=api_key)
        
        # Resolve default output directory to sibling '../french_learning/tcf_canada/eo'
        if output_base_dir is None:
            project_root = Path(__file__).resolve().parent.parent  # .../french_learning_builder
            sibling_root = project_root.parent / 'french_learning' / 'tcf_canada' / 'eo'
            output_base_dir = str(sibling_root)
        
        self.output_base_dir = output_base_dir
        self.task2_dir = os.path.join(output_base_dir, "task2")
        self.task3_dir = os.path.join(output_base_dir, "task3")
        
        # State file to resume progress and numbering across runs
        self.state_file = os.path.join(output_base_dir, ".generation_state.json")
        self.state: Dict[str, int] = {
            "task2_index": 0,        # next topic index to start from (0-based)
            "task3_index": 0,
            "task2_sequence": 0,     # next file sequence number base for filenames
            "task3_sequence": 0
        }
        
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

    def _load_state(self) -> None:
        """Load resume state from disk if available."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Only update known keys to avoid issues
                for k in self.state.keys():
                    if k in data and isinstance(data[k], int) and data[k] >= 0:
                        self.state[k] = data[k]
                print(f"🧭 Resume state loaded: {self.state}")
            else:
                print("🧭 No prior state found. Starting from the beginning.")
        except Exception as e:
            print(f"⚠️ Could not load state: {e}. Starting fresh.")

    def _save_state(self) -> None:
        """Persist resume state to disk."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            print(f"💾 State saved: {self.state}")
        except Exception as e:
            print(f"⚠️ Could not save state: {e}")
    
    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt from file"""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    def _create_directories(self) -> None:
        """Create output directories if they don't exist and load state."""
        os.makedirs(self.task2_dir, exist_ok=True)
        os.makedirs(self.task3_dir, exist_ok=True)
        print(f"📁 Directories ready:\n   - Task 2: {self.task2_dir}\n   - Task 3: {self.task3_dir}")
        
        # Load prior state if any
        self._load_state()
        
        # Initialize sequence from existing files if larger than state
        try:
            def max_seq_in(dir_path: str, prefix: str) -> int:
                seq = 0
                for name in os.listdir(dir_path):
                    if name.startswith(prefix + "_"):
                        parts = name.split("_")
                        if len(parts) >= 2 and parts[1].isdigit():
                            seq = max(seq, int(parts[1]))
                return seq
            existing_t2 = max_seq_in(self.task2_dir, "task2")
            existing_t3 = max_seq_in(self.task3_dir, "task3")
            if existing_t2 > self.state["task2_sequence"]:
                self.state["task2_sequence"] = existing_t2
            if existing_t3 > self.state["task3_sequence"]:
                self.state["task3_sequence"] = existing_t3
        except Exception:
            pass
    
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
            task_key = topic_info.get('task', 'unknown')
            if task_key == 'tache_2':
                task_label = 'Tâche 2'
            elif task_key == 'tache_3':
                task_label = 'Tâche 3'
            else:
                task_label = str(task_key)
            part_raw = topic_info.get('part', 'unknown')
            part_label = part_raw
            try:
                # Format 'partie_2' -> 'Partie 2'
                if isinstance(part_raw, str) and '_' in part_raw:
                    left, right = part_raw.split('_', 1)
                    part_label = f"{left.capitalize()} {right}"
            except Exception:
                pass
            
            metadata = f"""---
# TCF Canada Expression Orale - Generated Practice
source_file: {topic_info.get('source_file', 'unknown')}
source_url: {topic_info.get('source_url', 'unknown')}
task: {task_key}
part: {topic_info.get('part', 'unknown')}
generated_at: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

# Informations
- Tâche: {task_label}
- Partie: {part_label}
- Source URL: {topic_info.get('source_url', 'unknown')}
- Source fichier: {topic_info.get('source_file', 'unknown')}

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
        Generate Task 2 practice content for given topics, resuming from last index.
        """
        start_idx = self.state.get("task2_index", 0)
        if start_idx >= len(topics):
            print("✅ All Task 2 topics already processed (or start index beyond list).")
            return
        end_idx = len(topics) if limit is None else min(len(topics), start_idx + max(0, limit))
        work_items = topics[start_idx:end_idx]
        print(f"\n🎯 Generating Task 2 content for topics {start_idx + 1} to {end_idx} (of {len(topics)})...")
        
        for offset, topic in enumerate(work_items):
            i_global = start_idx + offset + 1
            print(f"\n📝 Processing Task 2 topic {i_global}/{len(topics)}")
            print(f"   Content: {topic['content'][:80]}...")
            
            generated_content = self._call_openai(self.task2_prompt, topic['content'])
            
            if generated_content:
                # Increment persistent sequence and build filename
                self.state["task2_sequence"] = int(self.state.get("task2_sequence", 0)) + 1
                seq = self.state["task2_sequence"]
                filename = self._sanitize_filename(topic['content'])
                filepath = os.path.join(self.task2_dir, f"task2_{seq:03d}_{filename}")
                
                if self._save_markdown_file(generated_content, filepath, topic):
                    print(f"   ✅ Saved: {os.path.basename(filepath)}")
                    self.stats["task2_generated"] += 1
                else:
                    self.stats["errors"] += 1
            else:
                print(f"   ❌ Failed to generate content")
                self.stats["skipped"] += 1
            
            # Advance index and save state after each item
            self.state["task2_index"] = i_global
            self._save_state()
            time.sleep(0.5)
    
    def generate_task3_content(self, topics: List[Dict], limit: Optional[int] = None) -> None:
        """
        Generate Task 3 practice content for given topics, resuming from last index.
        """
        start_idx = self.state.get("task3_index", 0)
        if start_idx >= len(topics):
            print("✅ All Task 3 topics already processed (or start index beyond list).")
            return
        end_idx = len(topics) if limit is None else min(len(topics), start_idx + max(0, limit))
        work_items = topics[start_idx:end_idx]
        print(f"\n🎯 Generating Task 3 content for topics {start_idx + 1} to {end_idx} (of {len(topics)})...")
        
        for offset, topic in enumerate(work_items):
            i_global = start_idx + offset + 1
            print(f"\n📝 Processing Task 3 topic {i_global}/{len(topics)}")
            print(f"   Content: {topic['content'][:80]}...")
            
            generated_content = self._call_openai(self.task3_prompt, topic['content'])
            
            if generated_content:
                # Increment persistent sequence and build filename
                self.state["task3_sequence"] = int(self.state.get("task3_sequence", 0)) + 1
                seq = self.state["task3_sequence"]
                filename = self._sanitize_filename(topic['content'])
                filepath = os.path.join(self.task3_dir, f"task3_{seq:03d}_{filename}")
                
                if self._save_markdown_file(generated_content, filepath, topic):
                    print(f"   ✅ Saved: {os.path.basename(filepath)}")
                    self.stats["task3_generated"] += 1
                else:
                    self.stats["errors"] += 1
            else:
                print(f"   ❌ Failed to generate content")
                self.stats["skipped"] += 1
            
            # Advance index and save state after each item
            self.state["task3_index"] = i_global
            self._save_state()
            time.sleep(0.5)
    
    def generate_all_content(self, task2_limit: Optional[int] = None, task3_limit: Optional[int] = None) -> None:
        """
        Generate all content for both tasks
        """
        print("🚀 Starting TCF Orale Content Generation...")
        
        # Create directories and load/initialize state
        self._create_directories()
        print(f"🧭 Resume positions -> Task2 index: {self.state.get('task2_index', 0)}, Task3 index: {self.state.get('task3_index', 0)}")
        print(f"🔢 File sequences -> Task2: {self.state.get('task2_sequence', 0)}, Task3: {self.state.get('task3_sequence', 0)}")
        
        # Load topics
        task2_topics, task3_topics = self.load_organized_topics()
        
        if not task2_topics and not task3_topics:
            print("❌ No topics loaded. Exiting.")
            return
        
        # Generate Task 2 content
        if task2_topics and (task2_limit is None or task2_limit > 0):
            self.generate_task2_content(task2_topics, task2_limit)
        
        # Generate Task 3 content
        if task3_topics and (task3_limit is None or task3_limit > 0):
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
