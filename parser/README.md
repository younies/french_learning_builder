# TCF Canada Topics Parser

A comprehensive Python parser for organizing and processing TCF Canada oral expression topics from JSON files.

## 📋 Overview

This parser reads JSON files containing TCF Canada topics (scraped from various monthly pages) and organizes them into two main lists:
- **Task 2 Topics**: Conversational scenarios
- **Task 3 Topics**: Opinion/discussion questions

The parser automatically sorts files chronologically (newest to oldest) and provides rich metadata for each topic.

## 🚀 Features

### ✅ Core Functionality
- **Automatic JSON file discovery** in the output directory
- **Chronological sorting** (newest to oldest) based on French month names
- **Two organized lists**: Task 2 and Task 3 topics
- **Rich metadata** for each topic (source URL, file, part number, etc.)
- **Smart content cleaning** (removes navigation menus, duplicates, etc.)
- **Export capabilities** to organized JSON format

### ✅ Date Intelligence
- **French month recognition**: `janvier`, `février`, `mars`, `avril`, `mai`, `juin`, `juillet`, `août`, `septembre`, `octobre`, `novembre`, `décembre`
- **Multi-year support**: Handles both 2024 and 2025 files
- **Automatic sorting**: Files processed from newest to oldest

### ✅ Data Quality
- **Content validation**: Filters out short, irrelevant, or navigation content
- **Duplicate removal**: Prevents duplicate topics within the same part
- **Error handling**: Graceful handling of malformed JSON or unexpected formats

## 📁 File Structure

```
parser/
├── parser.py          # Main parser implementation
├── README.md          # This documentation
└── __pycache__/       # Python cache (auto-generated)
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.7+
- Standard library only (no external dependencies)

### File Requirements
The parser expects JSON files in the `output/` directory with the naming pattern:
```
{month}-{year}-expression-orale.json
```

Examples:
- `aout-2025-expression-orale.json`
- `novembre-2024-expression-orale.json`
- `mars-2025-expression-orale.json`

## 📖 Usage

### Basic Usage

```python
from parser.parser import TCFTopicsParser

# Initialize the parser
parser = TCFTopicsParser()

# Load all topics
task2_topics, task3_topics = parser.load_all_topics()

print(f"Found {len(task2_topics)} Task 2 topics")
print(f"Found {len(task3_topics)} Task 3 topics")

# Access individual topics
for topic in task2_topics[:5]:  # First 5 Task 2 topics
    print(f"From {topic.source_file}: {topic.content}")
```

### Advanced Usage

```python
# Initialize with custom directory
parser = TCFTopicsParser(output_dir="custom_output_folder")

# Load topics
task2_topics, task3_topics = parser.load_all_topics()

# Get topics from specific source file
nov_task2, nov_task3 = parser.get_topics_by_source("novembre-2024-expression-orale.json")

# Get topics from specific part
part_1_task2 = parser.get_topics_by_part('tache_2', 1)

# Export organized data
parser.export_organized_topics("my_organized_topics.json")

# Display sample topics
parser.display_sample_topics(sample_size=3)
```

### Command Line Usage

```bash
# Run the parser directly
python parser/parser.py

# This will:
# 1. Process all JSON files in output/
# 2. Display chronological file order
# 3. Show processing progress
# 4. Display sample topics
# 5. Export to organized_topics.json
```

## 📊 Data Structure

### TopicItem Class
Each topic is represented as a `TopicItem` with the following attributes:

```python
@dataclass
class TopicItem:
    content: str          # The actual topic text
    source_url: str       # Original website URL
    source_file: str      # JSON filename it came from
    task: str            # 'tache_2' or 'tache_3'
    part: str            # 'partie_1', 'partie_2', etc.
    part_number: int     # Numeric part for sorting
```

### Expected JSON Input Format
```json
{
  "source_url": "https://reussir-tcfcanada.com/aout-2025-expression-orale/",
  "topics": {
    "tache_2": {
      "partie_1": ["topic1", "topic2", ...],
      "partie_2": ["topic1", "topic2", ...]
    },
    "tache_3": {
      "partie_1": ["topic1", "topic2", ...],
      "partie_2": ["topic1", "topic2", ...]
    }
  },
  "summary": { ... }
}
```

### Exported JSON Format
```json
{
  "summary": {
    "total_files_processed": 10,
    "total_topics": 580,
    "task2_topics_count": 310,
    "task3_topics_count": 270,
    "files_processed": ["file1.json", "file2.json", ...]
  },
  "task2_topics": [
    {
      "content": "Topic content here...",
      "source_url": "https://...",
      "source_file": "aout-2025-expression-orale.json",
      "part": "partie_1",
      "part_number": 1
    },
    ...
  ],
  "task3_topics": [...]
}
```

## 🎯 Methods Reference

### Core Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load_all_topics()` | Load and organize all topics from JSON files | `(task2_topics, task3_topics)` |
| `get_task2_topics()` | Get all Task 2 topics | `List[TopicItem]` |
| `get_task3_topics()` | Get all Task 3 topics | `List[TopicItem]` |

### Filter Methods

| Method | Parameters | Description | Returns |
|--------|------------|-------------|---------|
| `get_topics_by_source()` | `source_file: str` | Get topics from specific file | `(task2_topics, task3_topics)` |
| `get_topics_by_part()` | `task: str, part_number: int` | Get topics from specific task/part | `List[TopicItem]` |

### Utility Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `export_organized_topics()` | `output_file: str` | Export organized data to JSON |
| `display_sample_topics()` | `sample_size: int` | Display sample topics for preview |

## 📈 Performance & Statistics

### Typical Processing Results
- **Files processed**: 10 JSON files
- **Total topics**: ~580 topics
- **Task 2 topics**: ~310 conversational scenarios
- **Task 3 topics**: ~270 opinion questions
- **Processing time**: < 1 second for typical dataset

### Content Filtering
The parser automatically filters out:
- Navigation menu items
- Very short content (< 20 characters)
- Duplicate topics within the same part
- Malformed or empty content

## 🔍 Chronological Sorting

Files are automatically sorted by date (newest to oldest):

```
1. aout-2025-expression-orale.json (Août 2025)
2. juillet-2025-expression-orale.json (Juillet 2025)
3. juin-2025-expression-orale.json (Juin 2025)
...
9. decembre-2024-expression-orale.json (Décembre 2024)
10. novembre-2024-expression-orale.json (Novembre 2024)
```

## 🐛 Error Handling

The parser includes comprehensive error handling:

- **File not found**: Gracefully skips missing files
- **JSON parsing errors**: Reports errors and continues with other files
- **Malformed data**: Uses fallback values and continues processing
- **Date parsing failures**: Assigns default dates for sorting

## 📝 Example Output

```
🚀 Starting TCF Topics Parser...
🔍 Scanning directory: output
📅 Files sorted by date (newest to oldest):
    1. aout-2025-expression-orale.json (Aout 2025)
    2. juillet-2025-expression-orale.json (Juillet 2025)
    ...
📁 Found 10 JSON files (sorted by date - newest to oldest)
📄 Processing: aout-2025-expression-orale.json
   ✅ Extracted 26 topics
...
============================================================
PARSING SUMMARY
============================================================
📁 Files processed: 10
📊 Total topics found: 580
🎯 Task 2 topics: 310
🎯 Task 3 topics: 270
```

## 🚀 Integration with Main Project

This parser is designed to work with the main TCF scraper:

1. **Scraper** (`app/main.py`) downloads topics from TCF websites
2. **Parser** (`parser/parser.py`) organizes the scraped data
3. **Output** can be used for learning applications, analysis, or further processing

## 📄 License

This parser is part of the French Learning Builder project.

## 🤝 Contributing

When contributing to this parser:

1. Maintain backward compatibility with existing JSON formats
2. Add comprehensive error handling for new features
3. Update this README for any new functionality
4. Test with various JSON file formats and edge cases

## 📞 Support

For questions or issues with the parser:
1. Check the error messages in the console output
2. Verify your JSON files match the expected format
3. Ensure file naming follows the pattern: `{month}-{year}-expression-orale.json`
