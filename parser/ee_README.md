# TCF Canada Expression Écrite Parser

A specialized parser for organizing and processing TCF Canada Expression Écrite (Written Expression) topics from JSON files.

## Overview

The Expression Écrite parser (`ee_parser.py`) processes JSON files containing topics for all three Expression Écrite tasks:

- **Tâche 1**: Message Personnel (60-120 mots)
- **Tâche 2**: Article/Blog (120-150 mots)  
- **Tâche 3**: Texte Argumentatif (120-180 mots)

## Features

### 🔍 **Multi-Task Support**
- Parses topics for all three Expression Écrite tasks
- Handles different data structures for each task type
- Extracts metadata including word counts, combinations, and documents

### 📅 **Chronological Organization**
- Automatically sorts files by date (newest to oldest)
- Supports French month names in filenames
- Maintains chronological order in organized output

### 🧹 **Content Cleaning**
- Removes navigation menus and website artifacts
- Filters out non-topic content
- Cleans up formatting and whitespace

### 📊 **Comprehensive Statistics**
- Tracks topics per task and file
- Provides detailed parsing summaries
- Counts Task 3 topics with documents

## Usage

### Basic Usage

```python
from parser.ee_parser import TCFExpressionEcriteParser

# Initialize parser
parser = TCFExpressionEcriteParser(output_dir="output")

# Load all topics
task1_topics, task2_topics, task3_topics = parser.load_all_topics()

# Display sample topics
parser.display_sample_topics(sample_size=3)

# Export organized topics
parser.export_organized_topics("organized_ee_topics.json")
```

### Advanced Usage

```python
# Get topics from specific source
task1, task2, task3 = parser.get_topics_by_source("aout-2025-expression-ecrite.json")

# Get all topics for a specific task
all_task1 = parser.get_topics_by_task('tache_1')

# Get detailed statistics
stats = parser.get_statistics()
print(f"Total topics: {stats['total_topics']}")
print(f"Task 3 with documents: {stats['task3_with_documents']}")
```

## Data Structure

### EETopicItem Class

Each topic is represented by an `EETopicItem` dataclass with the following fields:

```python
@dataclass
class EETopicItem:
    content: str                    # The topic content
    source_url: str                 # Original URL
    source_file: str                # Source JSON filename
    task: str                       # 'tache_1', 'tache_2', or 'tache_3'
    word_count: str                 # e.g., '60-120', '120-150', '120-180'
    type: str                       # Task type description
    documents: Optional[List[str]]  # For Task 3 only
    combination: Optional[str]      # Source combination number
```

### Task Types

- **Task 1**: `message_personnel` - Personal messages, emails, announcements
- **Task 2**: `article_blog` - Blog articles, experience sharing, informative texts  
- **Task 3**: `texte_argumentatif` - Argumentative texts with supporting documents

## File Format Support

The parser expects JSON files with the following structure:

```json
{
  "source_url": "https://example.com",
  "type": "expression_ecrite",
  "topics": {
    "tache_1": [
      {
        "content": "Topic content...",
        "combination": "Combinaison 1",
        "word_count": "60-120"
      }
    ],
    "tache_2": [...],
    "tache_3": [
      {
        "content": "Topic content...",
        "combination": "Combinaison 1", 
        "documents": ["Document 1 text...", "Document 2 text..."]
      }
    ]
  }
}
```

## Output Files

### organized_ee_topics.json

The parser exports a comprehensive organized file containing:

```json
{
  "summary": {
    "total_files_processed": 10,
    "total_topics": 533,
    "task1_topics_count": 221,
    "task2_topics_count": 258,
    "task3_topics_count": 54,
    "files_processed": ["file1.json", "file2.json", ...]
  },
  "task1_topics": [...],
  "task2_topics": [...],
  "task3_topics": [...]
}
```

## Statistics Example

Based on 10 files processed:

```
📊 Total topics found: 533
🎯 Task 1 topics: 221 (Message Personnel)
🎯 Task 2 topics: 258 (Article/Blog)
🎯 Task 3 topics: 54 (Texte Argumentatif)
```

## Integration

The parser integrates seamlessly with:

- **Expression Écrite Generator** (`ee_generator.py`) - Uses organized topics for content generation
- **Main EE Scraper** (`main_ee.py`) - Processes raw scraped data
- **GPT-5 Content Generation** - Provides structured input for AI generation

## Command Line Usage

```bash
# Run the parser directly
cd parser
python ee_parser.py

# Or from project root
python -c "from parser.ee_parser import main; main()"
```

## Content Quality

The parser includes robust content filtering to ensure high-quality topics:

- ✅ Removes navigation menus and website artifacts
- ✅ Filters out JavaScript and CSS code
- ✅ Validates minimum content length
- ✅ Preserves original formatting where appropriate
- ✅ Maintains source attribution and metadata

## Error Handling

- Graceful handling of malformed JSON files
- Continues processing even if individual files fail
- Detailed error reporting and logging
- Fallback mechanisms for missing data fields

---

*This parser is part of the TCF Canada French Learning Builder system, designed to help create comprehensive practice materials for Expression Écrite tasks.*
