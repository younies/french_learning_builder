import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class EETopicItem:
    """
    Data class to represent a single Expression Écrite topic with metadata
    """
    content: str
    source_url: str
    source_file: str
    task: str  # 'tache_1', 'tache_2', or 'tache_3'
    word_count: str  # e.g., '60-120', '120-150', '120-180'
    type: str  # e.g., 'message_personnel', 'article_blog', 'texte_argumentatif'
    documents: Optional[List[str]] = None  # For Task 3 only
    combination: Optional[str] = None  # Source combination number

class TCFExpressionEcriteParser:
    """
    Parser to read and organize TCF Canada Expression Écrite topics from JSON files
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the parser with the output directory containing JSON files
        """
        self.output_dir = output_dir
        self.task1_topics: List[EETopicItem] = []
        self.task2_topics: List[EETopicItem] = []
        self.task3_topics: List[EETopicItem] = []
        self.files_processed: List[str] = []
        self.total_topics_found = 0
        
    def load_all_topics(self) -> Tuple[List[EETopicItem], List[EETopicItem], List[EETopicItem]]:
        """
        Load all Expression Écrite topics from JSON files in the output directory
        Returns: (task1_topics, task2_topics, task3_topics)
        """
        print(f"🔍 Scanning directory for Expression Écrite topics: {self.output_dir}")
        
        # Get all Expression Écrite JSON files in the output directory
        json_files = [f for f in os.listdir(self.output_dir) 
                     if f.endswith('.json') and 'expression-ecrite' in f]
        
        if not json_files:
            print(f"❌ No Expression Écrite JSON files found in {self.output_dir}")
            return self.task1_topics, self.task2_topics, self.task3_topics
        
        # Sort files by date (newest to oldest)
        json_files_sorted = self._sort_files_by_date(json_files)
        
        print(f"📁 Found {len(json_files_sorted)} Expression Écrite JSON files (sorted by date - newest to oldest)")
        
        # Process each JSON file in chronological order
        for json_file in json_files_sorted:
            self._process_json_file(json_file)
        
        # Sort topics by chronological order (newest first)
        def sort_key(topic):
            # Extract date from source_file for sorting
            year, month = self._extract_date_from_filename(topic.source_file)
            return (-year, -month)  # Negative for reverse order (newest first)
        
        self.task1_topics.sort(key=sort_key)
        self.task2_topics.sort(key=sort_key)
        self.task3_topics.sort(key=sort_key)
        
        self._print_summary()
        
        return self.task1_topics, self.task2_topics, self.task3_topics
    
    def _sort_files_by_date(self, json_files: List[str]) -> List[str]:
        """
        Sort JSON files by date from newest to oldest
        Expected format: month-year-expression-ecrite.json
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
        Process a single Expression Écrite JSON file and extract topics
        """
        file_path = os.path.join(self.output_dir, json_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📄 Processing: {json_file}")
            
            source_url = data.get('source_url', 'Unknown')
            topics = data.get('topics', {})
            
            file_topic_count = 0
            
            # Process Task 1 topics
            tache_1 = topics.get('tache_1', [])
            for topic_data in tache_1:
                if isinstance(topic_data, dict):
                    content = topic_data.get('content', '')
                    combination = topic_data.get('combination', 'Unknown')
                    word_count = topic_data.get('word_count', '60-120')
                elif isinstance(topic_data, str):
                    content = topic_data
                    combination = 'Unknown'
                    word_count = '60-120'
                else:
                    continue
                
                cleaned_content = self._clean_topic_content(content)
                if cleaned_content:
                    topic_item = EETopicItem(
                        content=cleaned_content,
                        source_url=source_url,
                        source_file=json_file,
                        task='tache_1',
                        word_count=word_count,
                        type='message_personnel',
                        combination=combination
                    )
                    self.task1_topics.append(topic_item)
                    file_topic_count += 1
            
            # Process Task 2 topics
            tache_2 = topics.get('tache_2', [])
            for topic_data in tache_2:
                if isinstance(topic_data, dict):
                    content = topic_data.get('content', '')
                    combination = topic_data.get('combination', 'Unknown')
                    word_count = topic_data.get('word_count', '120-150')
                elif isinstance(topic_data, str):
                    content = topic_data
                    combination = 'Unknown'
                    word_count = '120-150'
                else:
                    continue
                
                cleaned_content = self._clean_topic_content(content)
                if cleaned_content:
                    topic_item = EETopicItem(
                        content=cleaned_content,
                        source_url=source_url,
                        source_file=json_file,
                        task='tache_2',
                        word_count=word_count,
                        type='article_blog',
                        combination=combination
                    )
                    self.task2_topics.append(topic_item)
                    file_topic_count += 1
            
            # Process Task 3 topics
            tache_3 = topics.get('tache_3', [])
            for topic_data in tache_3:
                if isinstance(topic_data, dict):
                    content = topic_data.get('content', '')
                    combination = topic_data.get('combination', 'Unknown')
                    documents = topic_data.get('documents', [])
                elif isinstance(topic_data, str):
                    content = topic_data
                    combination = 'Unknown'
                    documents = []
                else:
                    continue
                
                cleaned_content = self._clean_topic_content(content)
                if cleaned_content:
                    topic_item = EETopicItem(
                        content=cleaned_content,
                        source_url=source_url,
                        source_file=json_file,
                        task='tache_3',
                        word_count='120-180',
                        type='texte_argumentatif',
                        documents=documents if documents else None,
                        combination=combination
                    )
                    self.task3_topics.append(topic_item)
                    file_topic_count += 1
            
            self.files_processed.append(json_file)
            self.total_topics_found += file_topic_count
            print(f"   ✅ Extracted {file_topic_count} topics")
            
        except Exception as e:
            print(f"   ❌ Error processing {json_file}: {e}")
    
    def _clean_topic_content(self, content: str) -> Optional[str]:
        """
        Clean and validate Expression Écrite topic content
        """
        if not content or not isinstance(content, str):
            return None
        
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Skip very short content or navigation/menu items
        if len(content) < 15:
            return None
        
        # Skip specific non-topic prefixes for Expression Écrite
        starts_with_blacklist = [
            'AccueilSe connecter',
            'Nous utilisons des cookies',
            'Nos Contacts',
            '🎯 Nouveau Service Exceptionnel',
            'Sujets d\'actualité corrigés pour',
            'les méthodologiesCompréhension',
            'Les méthodologiesCompréhension',
            'Partager avec votre réseau',
            'Combinaison',
            'Tâche 1',
            'Tâche 2', 
            'Tâche 3',
            'Document 1',
            'Document 2',
            'mots minimum',
            'mots maximum',
            '/* <![CDATA[ */ var ldVars =',
            '/* <![CDATA[ */ var ldVars =',
            '/* <![CDATA['
        ]
        for prefix in starts_with_blacklist:
            if content.startswith(prefix):
                return None
        
        # Skip content that looks like navigation menus or metadata
        navigation_keywords = [
            'AccueilSe connecter', 'Compréhension écrite', 'Expression Orale',
            'Nos Formations', 'Cabinet d\'immigration', 'Contactez-nous',
            'Politique de retour', 'Mentions Légales', 'les pagesActualité',
            'Les pages', 'Nous acceptons', 'Paiment', 'Cliquez ici'
        ]
        
        for keyword in navigation_keywords:
            if keyword in content:
                return None
        
        # Skip content that contains too many navigation-like elements
        if content.count('Compréhension') > 1 or content.count('Expression') > 1:
            return None
        
        # Skip very long content that looks like concatenated menus/navigation
        if len(content) > 800 and any(nav in content for nav in navigation_keywords):
            return None
        
        return content.strip()
    
    def _print_summary(self) -> None:
        """
        Print a summary of the parsing results
        """
        print(f"\n{'='*60}")
        print("EXPRESSION ÉCRITE PARSING SUMMARY")
        print(f"{'='*60}")
        print(f"📁 Files processed: {len(self.files_processed)}")
        print(f"📊 Total topics found: {self.total_topics_found}")
        print(f"🎯 Task 1 topics: {len(self.task1_topics)}")
        print(f"🎯 Task 2 topics: {len(self.task2_topics)}")
        print(f"🎯 Task 3 topics: {len(self.task3_topics)}")
        
        print(f"\n📋 Files processed:")
        for file in self.files_processed:
            print(f"   - {file}")
    
    def get_task1_topics(self) -> List[EETopicItem]:
        """Get all Task 1 topics"""
        return self.task1_topics
    
    def get_task2_topics(self) -> List[EETopicItem]:
        """Get all Task 2 topics"""
        return self.task2_topics
    
    def get_task3_topics(self) -> List[EETopicItem]:
        """Get all Task 3 topics"""
        return self.task3_topics
    
    def get_topics_by_source(self, source_file: str) -> Tuple[List[EETopicItem], List[EETopicItem], List[EETopicItem]]:
        """
        Get topics from a specific source file
        """
        task1 = [topic for topic in self.task1_topics if topic.source_file == source_file]
        task2 = [topic for topic in self.task2_topics if topic.source_file == source_file]
        task3 = [topic for topic in self.task3_topics if topic.source_file == source_file]
        return task1, task2, task3
    
    def get_topics_by_task(self, task: str) -> List[EETopicItem]:
        """
        Get topics from a specific task
        """
        if task == 'tache_1':
            return self.task1_topics
        elif task == 'tache_2':
            return self.task2_topics
        elif task == 'tache_3':
            return self.task3_topics
        else:
            return []
    
    def export_organized_topics(self, output_file: str = "organized_ee_topics.json") -> None:
        """
        Export the organized Expression Écrite topics to a new JSON file
        """
        organized_data = {
            "summary": {
                "total_files_processed": len(self.files_processed),
                "total_topics": self.total_topics_found,
                "task1_topics_count": len(self.task1_topics),
                "task2_topics_count": len(self.task2_topics),
                "task3_topics_count": len(self.task3_topics),
                "files_processed": self.files_processed
            },
            "task1_topics": [
                {
                    "content": topic.content,
                    "source_url": topic.source_url,
                    "source_file": topic.source_file,
                    "task": topic.task,
                    "word_count": topic.word_count,
                    "type": topic.type,
                    "combination": topic.combination
                }
                for topic in self.task1_topics
            ],
            "task2_topics": [
                {
                    "content": topic.content,
                    "source_url": topic.source_url,
                    "source_file": topic.source_file,
                    "task": topic.task,
                    "word_count": topic.word_count,
                    "type": topic.type,
                    "combination": topic.combination
                }
                for topic in self.task2_topics
            ],
            "task3_topics": [
                {
                    "content": topic.content,
                    "source_url": topic.source_url,
                    "source_file": topic.source_file,
                    "task": topic.task,
                    "word_count": topic.word_count,
                    "type": topic.type,
                    "documents": topic.documents,
                    "combination": topic.combination
                }
                for topic in self.task3_topics
            ]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(organized_data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Organized Expression Écrite topics exported to: {output_file}")
        except Exception as e:
            print(f"\n❌ Error exporting topics: {e}")
    
    def display_sample_topics(self, sample_size: int = 3) -> None:
        """
        Display a sample of topics from each task
        """
        print(f"\n{'='*60}")
        print(f"SAMPLE EXPRESSION ÉCRITE TOPICS (showing first {sample_size} from each task)")
        print(f"{'='*60}")
        
        print(f"\n🎯 TASK 1 SAMPLE - Message Personnel ({len(self.task1_topics)} total):")
        print("-" * 50)
        for i, topic in enumerate(self.task1_topics[:sample_size], 1):
            print(f"\n{i}. [{topic.source_file} - {topic.word_count} mots]")
            print(f"   {topic.content[:200]}{'...' if len(topic.content) > 200 else ''}")
            if topic.combination:
                print(f"   📋 Source: {topic.combination}")
        
        print(f"\n🎯 TASK 2 SAMPLE - Article/Blog ({len(self.task2_topics)} total):")
        print("-" * 50)
        for i, topic in enumerate(self.task2_topics[:sample_size], 1):
            print(f"\n{i}. [{topic.source_file} - {topic.word_count} mots]")
            print(f"   {topic.content[:200]}{'...' if len(topic.content) > 200 else ''}")
            if topic.combination:
                print(f"   📋 Source: {topic.combination}")
        
        print(f"\n🎯 TASK 3 SAMPLE - Texte Argumentatif ({len(self.task3_topics)} total):")
        print("-" * 50)
        for i, topic in enumerate(self.task3_topics[:sample_size], 1):
            print(f"\n{i}. [{topic.source_file} - {topic.word_count} mots]")
            print(f"   {topic.content[:200]}{'...' if len(topic.content) > 200 else ''}")
            if topic.documents:
                print(f"   📄 Documents: {len(topic.documents)} document(s)")
                for j, doc in enumerate(topic.documents[:2], 1):  # Show first 2 documents
                    print(f"      Doc {j}: {doc[:100]}{'...' if len(doc) > 100 else ''}")
            if topic.combination:
                print(f"   📋 Source: {topic.combination}")

    def get_statistics(self) -> Dict[str, int]:
        """
        Get detailed statistics about the parsed topics
        """
        return {
            "total_files": len(self.files_processed),
            "total_topics": self.total_topics_found,
            "task1_count": len(self.task1_topics),
            "task2_count": len(self.task2_topics),
            "task3_count": len(self.task3_topics),
            "task3_with_documents": len([t for t in self.task3_topics if t.documents])
        }


def main():
    """
    Main function to demonstrate the Expression Écrite parser
    """
    print("🚀 Starting TCF Expression Écrite Topics Parser...")
    
    # Initialize parser
    parser = TCFExpressionEcriteParser(output_dir="output")
    
    # Load all topics
    task1_topics, task2_topics, task3_topics = parser.load_all_topics()
    
    # Display sample topics
    parser.display_sample_topics(sample_size=3)
    
    # Export organized topics
    parser.export_organized_topics("organized_ee_topics.json")
    
    # Display statistics
    stats = parser.get_statistics()
    print(f"\n📊 Detailed Statistics:")
    print(f"   - Total files processed: {stats['total_files']}")
    print(f"   - Total topics found: {stats['total_topics']}")
    print(f"   - Task 1 (Message Personnel): {stats['task1_count']} topics")
    print(f"   - Task 2 (Article/Blog): {stats['task2_count']} topics")
    print(f"   - Task 3 (Texte Argumentatif): {stats['task3_count']} topics")
    print(f"   - Task 3 with documents: {stats['task3_with_documents']} topics")
    
    print(f"\n🎉 Expression Écrite parsing complete!")
    print(f"📊 You now have:")
    print(f"   - {len(task1_topics)} Task 1 topics")
    print(f"   - {len(task2_topics)} Task 2 topics")
    print(f"   - {len(task3_topics)} Task 3 topics")
    print(f"   - All organized in parser.task1_topics, parser.task2_topics, and parser.task3_topics lists")


if __name__ == "__main__":
    main()
