import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class TopicItem:
    """
    Data class to represent a single topic with metadata
    """
    content: str
    source_url: str
    source_file: str
    task: str  # 'tache_2' or 'tache_3'
    part: str  # 'partie_1', 'partie_2', etc.
    part_number: int

class TCFTopicsParser:
    """
    Parser to read and organize TCF Canada topics from JSON files
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the parser with the output directory containing JSON files
        """
        self.output_dir = output_dir
        self.task2_topics: List[TopicItem] = []
        self.task3_topics: List[TopicItem] = []
        self.files_processed: List[str] = []
        self.total_topics_found = 0
        
    def load_all_topics(self) -> Tuple[List[TopicItem], List[TopicItem]]:
        """
        Load all topics from JSON files in the output directory
        Returns: (task2_topics, task3_topics)
        """
        print(f"🔍 Scanning directory: {self.output_dir}")
        
        # Get all JSON files in the output directory
        json_files = [f for f in os.listdir(self.output_dir) if f.endswith('.json')]
        
        if not json_files:
            print(f"❌ No JSON files found in {self.output_dir}")
            return self.task2_topics, self.task3_topics
        
        # Sort files by date (newest to oldest)
        json_files_sorted = self._sort_files_by_date(json_files)
        
        print(f"📁 Found {len(json_files_sorted)} JSON files (sorted by date - newest to oldest)")
        
        # Process each JSON file in chronological order
        for json_file in json_files_sorted:
            self._process_json_file(json_file)
        
        # Sort topics by chronological order (newest first), then by part number
        def sort_key(topic):
            # Extract date from source_file for sorting
            year, month = self._extract_date_from_filename(topic.source_file)
            return (-year, -month, topic.part_number)  # Negative for reverse order
        
        self.task2_topics.sort(key=sort_key)
        self.task3_topics.sort(key=sort_key)
        
        self._print_summary()
        
        return self.task2_topics, self.task3_topics
    
    def _sort_files_by_date(self, json_files: List[str]) -> List[str]:
        """
        Sort JSON files by date from newest to oldest
        Expected format: month-year-expression-orale.json
        """
        # French month names to numbers mapping
        french_months = {
            'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12
        }
        
        def extract_date(filename: str) -> Tuple[int, int]:
            """
            Extract year and month from filename
            Returns: (year, month) tuple for sorting
            """
            try:
                # Remove the .json extension and split by hyphens
                base_name = filename.replace('.json', '')
                parts = base_name.split('-')
                
                if len(parts) >= 2:
                    month_name = parts[0].lower()
                    year_str = parts[1]
                    
                    if month_name in french_months and year_str.isdigit():
                        year = int(year_str)
                        month = french_months[month_name]
                        return (year, month)
            except:
                pass
            
            # If parsing fails, return a default date (very old)
            return (1900, 1)
        
        # Sort by date (newest first)
        sorted_files = sorted(json_files, key=extract_date, reverse=True)
        
        # Print the sorted order for verification
        print("📅 Files sorted by date (newest to oldest):")
        for i, filename in enumerate(sorted_files, 1):
            year, month = extract_date(filename)
            month_names = {v: k for k, v in french_months.items()}
            month_name = month_names.get(month, 'unknown')
            print(f"   {i:2d}. {filename} ({month_name.capitalize()} {year})")
        
        return sorted_files
    
    def _extract_date_from_filename(self, filename: str) -> Tuple[int, int]:
        """
        Extract year and month from filename for sorting
        """
        french_months = {
            'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12
        }
        
        try:
            base_name = filename.replace('.json', '')
            parts = base_name.split('-')
            
            if len(parts) >= 2:
                month_name = parts[0].lower()
                year_str = parts[1]
                
                if month_name in french_months and year_str.isdigit():
                    year = int(year_str)
                    month = french_months[month_name]
                    return (year, month)
        except:
            pass
        
        return (1900, 1)  # Default for unparseable filenames
    
    def _process_json_file(self, json_file: str) -> None:
        """
        Process a single JSON file and extract topics
        """
        file_path = os.path.join(self.output_dir, json_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📄 Processing: {json_file}")
            
            source_url = data.get('source_url', 'Unknown')
            topics = data.get('topics', {})
            
            file_topic_count = 0
            
            # Process Task 2 topics
            tache_2 = topics.get('tache_2', {})
            for part_name, part_topics in tache_2.items():
                part_number = self._extract_part_number(part_name)
                for topic_content in part_topics:
                    # Clean up the topic content
                    cleaned_content = self._clean_topic_content(topic_content)
                    if cleaned_content:  # Only add non-empty topics
                        topic_item = TopicItem(
                            content=cleaned_content,
                            source_url=source_url,
                            source_file=json_file,
                            task='tache_2',
                            part=part_name,
                            part_number=part_number
                        )
                        self.task2_topics.append(topic_item)
                        file_topic_count += 1
            
            # Process Task 3 topics
            tache_3 = topics.get('tache_3', {})
            for part_name, part_topics in tache_3.items():
                part_number = self._extract_part_number(part_name)
                for topic_content in part_topics:
                    # Clean up the topic content
                    cleaned_content = self._clean_topic_content(topic_content)
                    if cleaned_content:  # Only add non-empty topics
                        topic_item = TopicItem(
                            content=cleaned_content,
                            source_url=source_url,
                            source_file=json_file,
                            task='tache_3',
                            part=part_name,
                            part_number=part_number
                        )
                        self.task3_topics.append(topic_item)
                        file_topic_count += 1
            
            self.files_processed.append(json_file)
            self.total_topics_found += file_topic_count
            print(f"   ✅ Extracted {file_topic_count} topics")
            
        except Exception as e:
            print(f"   ❌ Error processing {json_file}: {e}")
    
    def _extract_part_number(self, part_name: str) -> int:
        """
        Extract the part number from part name (e.g., 'partie_1' -> 1)
        """
        try:
            if '_' in part_name:
                return int(part_name.split('_')[1])
            return 0
        except:
            return 0
    
    def _clean_topic_content(self, content: str) -> Optional[str]:
        """
        Clean and validate topic content
        """
        if not content or not isinstance(content, str):
            return None
        
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Strip leading 'Partie <number>' prefix if present (e.g., 'Partie 7', 'partie 12:')
        content = re.sub(r'^partie\s*\d+\s*[:\-–—]*\s*', '', content, flags=re.IGNORECASE)
        
        # Skip very short content or navigation/menu items
        if len(content) < 10:
            return None
        
        # Skip specific non-topic prefixes
        starts_with_blacklist = [
            'AccueilSe connecter',
            'Nous utilisons des cookies',
            'Nos Contacts',
            '🎯 Nouveau Service Exceptionnel',
            'Sujets d\'actualité corrigés pour',
            'les méthodologiesCompréhension',
            'Les méthodologiesCompréhension',
            'Partager avec votre réseau'
        ]
        for prefix in starts_with_blacklist:
            if content.startswith(prefix):
                return None
        
        # Skip content that looks like navigation menus
        navigation_keywords = [
            'AccueilSe connecter', 'Compréhension écrite', 'Expression Orale',
            'Nos Formations', 'Cabinet d\'immigration', 'Contactez-nous',
            'Politique de retour', 'Mentions Légales'
        ]
        
        for keyword in navigation_keywords:
            if keyword in content:
                return None
        
        # Strip leading 'Partie <number>' prefix case-insensitively
        match = re.match(r'^Partie\s+(\d+)', content, re.IGNORECASE)
        if match:
            content = content[len(match.group(0)):]
        
        # Skip content that starts with "Partie X" (these are usually concatenated headers)
        if content.startswith('Partie ') and len(content) > 500:
            return None
        
        return content.strip()
    
    def _print_summary(self) -> None:
        """
        Print a summary of the parsing results
        """
        print(f"\n{'='*60}")
        print("PARSING SUMMARY")
        print(f"{'='*60}")
        print(f"📁 Files processed: {len(self.files_processed)}")
        print(f"📊 Total topics found: {self.total_topics_found}")
        print(f"🎯 Task 2 topics: {len(self.task2_topics)}")
        print(f"🎯 Task 3 topics: {len(self.task3_topics)}")
        
        print(f"\n📋 Files processed:")
        for file in self.files_processed:
            print(f"   - {file}")
    
    def get_task2_topics(self) -> List[TopicItem]:
        """
        Get all Task 2 topics
        """
        return self.task2_topics
    
    def get_task3_topics(self) -> List[TopicItem]:
        """
        Get all Task 3 topics
        """
        return self.task3_topics
    
    def get_topics_by_source(self, source_file: str) -> Tuple[List[TopicItem], List[TopicItem]]:
        """
        Get topics from a specific source file
        """
        task2 = [topic for topic in self.task2_topics if topic.source_file == source_file]
        task3 = [topic for topic in self.task3_topics if topic.source_file == source_file]
        return task2, task3
    
    def get_topics_by_part(self, task: str, part_number: int) -> List[TopicItem]:
        """
        Get topics from a specific task and part
        """
        topics_list = self.task2_topics if task == 'tache_2' else self.task3_topics
        return [topic for topic in topics_list if topic.part_number == part_number]
    
    def export_organized_topics(self, output_file: str = "organized_topics.json") -> None:
        """
        Export the organized topics to a new JSON file
        """
        organized_data = {
            "summary": {
                "total_files_processed": len(self.files_processed),
                "total_topics": self.total_topics_found,
                "task2_topics_count": len(self.task2_topics),
                "task3_topics_count": len(self.task3_topics),
                "files_processed": self.files_processed
            },
            "task2_topics": [
                {
                    "content": topic.content,
                    "source_url": topic.source_url,
                    "source_file": topic.source_file,
                    "part": topic.part,
                    "part_number": topic.part_number
                }
                for topic in self.task2_topics
            ],
            "task3_topics": [
                {
                    "content": topic.content,
                    "source_url": topic.source_url,
                    "source_file": topic.source_file,
                    "part": topic.part,
                    "part_number": topic.part_number
                }
                for topic in self.task3_topics
            ]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(organized_data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Organized topics exported to: {output_file}")
        except Exception as e:
            print(f"\n❌ Error exporting topics: {e}")
    
    def display_sample_topics(self, sample_size: int = 3) -> None:
        """
        Display a sample of topics from each task
        """
        print(f"\n{'='*60}")
        print(f"SAMPLE TOPICS (showing first {sample_size} from each task)")
        print(f"{'='*60}")
        
        print(f"\n🎯 TASK 2 SAMPLE ({len(self.task2_topics)} total):")
        print("-" * 50)
        for i, topic in enumerate(self.task2_topics[:sample_size], 1):
            print(f"\n{i}. [{topic.source_file} - {topic.part}]")
            print(f"   {topic.content[:200]}{'...' if len(topic.content) > 200 else ''}")
        
        print(f"\n🎯 TASK 3 SAMPLE ({len(self.task3_topics)} total):")
        print("-" * 50)
        for i, topic in enumerate(self.task3_topics[:sample_size], 1):
            print(f"\n{i}. [{topic.source_file} - {topic.part}]")
            print(f"   {topic.content[:200]}{'...' if len(topic.content) > 200 else ''}")


def main():
    """
    Main function to demonstrate the parser
    """
    print("🚀 Starting TCF Topics Parser...")
    
    # Initialize parser
    parser = TCFTopicsParser(output_dir="output")
    
    # Load all topics
    task2_topics, task3_topics = parser.load_all_topics()
    
    # Display sample topics
    parser.display_sample_topics(sample_size=5)
    
    # Export organized topics
    parser.export_organized_topics("organized_topics.json")
    
    print(f"\n🎉 Parsing complete!")
    print(f"📊 You now have:")
    print(f"   - {len(task2_topics)} Task 2 topics")
    print(f"   - {len(task3_topics)} Task 3 topics")
    print(f"   - All organized in parser.task2_topics and parser.task3_topics lists")


if __name__ == "__main__":
    main()
