import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple

def scrape_expression_ecrite_topics_from_url(url: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Scrape TCF Canada Expression Écrite topics from a specific URL
    Returns a structured dictionary with Tâche 1, Tâche 2, and Tâche 3 topics
    """
    
    try:
        # Send GET request to the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize the topics structure
        topics = {
            "tache_1": [],
            "tache_2": [],
            "tache_3": []
        }
        
        # Find all combinations (Combinaison sections)
        combinations = soup.find_all(text=re.compile(r'Combinaison \d+'))
        
        for combination_text in combinations:
            # Find the parent element containing this combination
            combination_element = combination_text.parent
            if not combination_element:
                continue
                
            # Find the next siblings that contain the tasks
            current = combination_element
            current_task = None
            
            # Look for task content in the following elements
            for sibling in combination_element.find_all_next():
                text = sibling.get_text(strip=True)
                
                # Stop if we reach the next combination
                if 'Combinaison' in text and text != combination_text:
                    break
                
                # Identify task sections
                if 'Tâche 1' in text:
                    current_task = "tache_1"
                elif 'Tâche 2' in text:
                    current_task = "tache_2"
                elif 'Tâche 3' in text:
                    current_task = "tache_3"
                
                # Extract task content
                if current_task and text and len(text) > 30:
                    # Skip headers and word count instructions
                    if ('Tâche' not in text and 
                        'mots minimum' not in text and 
                        'mots maximum' not in text and 
                        'Document' not in text and
                        not text.startswith('Combinaison')):
                        
                        # Clean the text
                        clean_text = text.strip()
                        
                        # Check if this looks like a task instruction
                        if (any(keyword in clean_text.lower() for keyword in [
                            'rédigez', 'écrivez', 'vous', 'invitez', 'message', 
                            'courriel', 'article', 'blog', 'annonce', 'partagez'
                        ]) and len(clean_text) > 20):
                            
                            # Add to appropriate task if not already present
                            task_entry = {
                                "content": clean_text,
                                "source_url": url,
                                "combination": combination_text.strip()
                            }
                            
                            # Check for duplicates
                            if not any(existing['content'] == clean_text for existing in topics[current_task]):
                                topics[current_task].append(task_entry)
        
        return topics
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage {url}: {e}")
        return get_fallback_ee_topics()
    except Exception as e:
        print(f"Error parsing the webpage {url}: {e}")
        return get_fallback_ee_topics()

def get_fallback_ee_topics() -> Dict[str, List[Dict[str, str]]]:
    """
    Fallback topics for Expression Écrite based on the sample content
    """
    return {
        "tache_1": [
            {
                "content": "Répondez au courriel de votre ami Lucas en lui fournissant des détails sur les nouveaux locaux de votre entreprise : emplacement, aménagement des pièces, équipements disponibles, etc.",
                "source_url": "fallback",
                "combination": "Sample",
                "word_count": "60-120 mots"
            },
            {
                "content": "Vous êtes locataire d'un appartement qui vous semble trop grand. Rédigez une annonce dans un journal pour trouver un colocataire, en indiquant la superficie, le profil recherché et le montant du loyer, entre autres détails.",
                "source_url": "fallback", 
                "combination": "Sample",
                "word_count": "60-120 mots"
            },
            {
                "content": "Rédigez un message à un ami pour l'informer de votre déménagement et lui demander son aide, en précisant la date, le lieu et le déroulement du programme.",
                "source_url": "fallback",
                "combination": "Sample", 
                "word_count": "60-120 mots"
            }
        ],
        "tache_2": [
            {
                "content": "Partagez votre expérience lors de l'événement « Une semaine sans voiture », incluant les dates, le lieu et les activités proposées, tout en donnant votre avis sur cette initiative.",
                "source_url": "fallback",
                "combination": "Sample",
                "word_count": "120-150 mots"
            },
            {
                "content": "Vous avez récemment débuté une nouvelle activité de loisir, comme un sport ou la danse. Rédigez un article sur votre blog pour partager votre expérience.",
                "source_url": "fallback",
                "combination": "Sample",
                "word_count": "120-150 mots"
            },
            {
                "content": "Rédigez un article de blog sur votre artiste préféré dans le cadre d'un concours dont le thème est « Mon artiste préféré », permettant de gagner un séjour de deux semaines dans votre ville favorite.",
                "source_url": "fallback",
                "combination": "Sample",
                "word_count": "120-150 mots"
            }
        ],
        "tache_3": [
            {
                "content": "Impact des vêtements de marque sur les enfants",
                "source_url": "fallback",
                "combination": "Sample",
                "documents": [
                    "Les vêtements de marque jouent un rôle essentiel pour les enfants et les adolescents en leur permettant de s'exprimer et de se sentir intégrés dans un groupe social. Cette attraction pour les marques est particulièrement forte chez les adolescents qui cherchent à affirmer leur personnalité.",
                    "Les enfants grandissent rapidement, ce qui rend leurs vêtements trop petits après peu de temps. De plus, jouer à l'extérieur avec leurs amis dans l'herbe ou sur les aires de jeux fait que leurs vêtements s'usent vite et se salissent rapidement, souvent avec des trous."
                ]
            },
            {
                "content": "L'accès gratuit aux musées : avantage ou inconvénient ?",
                "source_url": "fallback",
                "combination": "Sample",
                "documents": [
                    "L'accès gratuit aux musées peut engendrer une affluence excessive, altérant ainsi la qualité de la visite. De plus, cela risque de diminuer leurs revenus, compromettant l'entretien des lieux et la conservation des œuvres.",
                    "Rendre les musées gratuits est une excellente initiative, car cela permet à tous d'accéder à la culture, quel que soit leur revenu. À mon avis, la gratuité des musées joue un rôle clé dans l'éducation du public."
                ]
            }
        ]
    }

def extract_task3_documents(soup, task3_element) -> List[str]:
    """
    Extract Document 1 and Document 2 for Tâche 3
    """
    documents = []
    
    # Look for document patterns
    for element in task3_element.find_all_next():
        text = element.get_text(strip=True)
        
        if 'Document 1' in text or 'Document 2' in text:
            # Find the next paragraph or content
            next_elem = element.find_next()
            if next_elem:
                doc_text = next_elem.get_text(strip=True)
                if len(doc_text) > 50:  # Reasonable document length
                    documents.append(doc_text)
    
    return documents

def calculate_ee_summary(topics: Dict[str, List[Dict[str, str]]]) -> Dict[str, int]:
    """
    Calculate summary statistics for Expression Écrite topics
    """
    summary = {}
    total_topics = 0
    
    for task_name, task_topics in topics.items():
        summary[task_name] = len(task_topics)
        total_topics += len(task_topics)
    
    summary["total_topics"] = total_topics
    return summary

def display_ee_topics(topics: Dict[str, List[Dict[str, str]]]):
    """
    Display the Expression Écrite topics in a formatted way
    """
    print("=" * 60)
    print("TCF CANADA - EXPRESSION ÉCRITE TOPICS")
    print("=" * 60)
    
    task_names = {
        "tache_1": "TÂCHE 1 (Message personnel - 60-120 mots)",
        "tache_2": "TÂCHE 2 (Article/Blog - 120-150 mots)", 
        "tache_3": "TÂCHE 3 (Texte argumentatif - Documents à analyser)"
    }
    
    for task, task_topics in topics.items():
        task_name = task_names.get(task, task.upper())
        print(f"\n🎯 {task_name}")
        print("-" * 50)
        
        for i, topic in enumerate(task_topics, 1):
            print(f"\n{i}. {topic['content']}")
            
            if 'word_count' in topic:
                print(f"   📏 Nombre de mots: {topic['word_count']}")
            
            if 'documents' in topic and topic['documents']:
                print(f"   📄 Documents à analyser:")
                for j, doc in enumerate(topic['documents'], 1):
                    print(f"      Document {j}: {doc[:100]}...")
            
            if 'combination' in topic:
                print(f"   📋 Source: {topic['combination']}")
        
        print("\n" + "=" * 50)

def generate_filename_from_ee_url(url: str) -> str:
    """
    Generate a safe filename from an Expression Écrite URL
    """
    # Parse the URL
    parsed = urlparse(url)
    
    # Get the path and remove leading/trailing slashes
    path = parsed.path.strip('/')
    
    # Replace 'expression-orale' with 'expression-ecrite' if needed
    path = path.replace('expression-orale', 'expression-ecrite')
    
    # Replace slashes and other unsafe characters with underscores
    safe_name = re.sub(r'[^\w\-.]', '_', path)
    
    # Remove multiple consecutive underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Remove leading/trailing underscores
    safe_name = safe_name.strip('_')
    
    # If empty, use the domain
    if not safe_name:
        safe_name = parsed.netloc.replace('.', '_')
    
    return f"{safe_name}.json"

def save_ee_topics_to_json(topics: Dict[str, List[Dict[str, str]]], filename: str = "tcf_ee_topics.json"):
    """
    Save Expression Écrite topics to a JSON file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
        print(f"✅ Expression Écrite topics saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving to file {filename}: {e}")

def process_single_ee_url(url: str, output_dir: str = "output") -> Optional[str]:
    """
    Process a single Expression Écrite URL and save its topics to a JSON file
    Returns the filename if successful, None otherwise
    """
    print(f"\n🔍 Processing Expression Écrite URL: {url}")
    
    # Scrape topics from the URL
    topics = scrape_expression_ecrite_topics_from_url(url)
    
    # Generate filename
    filename = generate_filename_from_ee_url(url)
    filepath = os.path.join(output_dir, filename)
    
    # Calculate summary
    summary = calculate_ee_summary(topics)
    
    # Add metadata to the topics
    topics_with_metadata = {
        "source_url": url,
        "type": "expression_ecrite",
        "topics": topics,
        "summary": summary
    }
    
    # Save to file
    save_ee_topics_to_json(topics_with_metadata, filepath)
    
    # Display summary for this URL
    print(f"📊 Summary for {url}:")
    for task_name, task_topics in topics.items():
        task_display = task_name.replace('_', ' ').title()
        print(f"   - {task_display}: {len(task_topics)} topics")
    print(f"   - Total: {summary['total_topics']} topics")
    
    return filepath if topics_with_metadata['summary']['total_topics'] > 0 else None

def process_multiple_ee_urls(urls: List[str], output_dir: str = "output") -> List[str]:
    """
    Process multiple Expression Écrite URLs and create separate files for each
    Returns list of successfully created filenames
    """
    print(f"🚀 Starting batch processing of {len(urls)} Expression Écrite URLs...")
    print(f"📁 Output directory: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    successful_files = []
    failed_urls = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(urls)}: {url}")
        print(f"{'='*60}")
        
        try:
            filepath = process_single_ee_url(url, output_dir)
            if filepath:
                successful_files.append(filepath)
            else:
                failed_urls.append(url)
        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")
            failed_urls.append(url)
    
    # Final summary
    print(f"\n{'='*60}")
    print("EXPRESSION ÉCRITE BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successfully processed: {len(successful_files)} URLs")
    print(f"❌ Failed to process: {len(failed_urls)} URLs")
    
    if successful_files:
        print(f"\n📁 Created files:")
        for filepath in successful_files:
            print(f"   - {filepath}")
    
    if failed_urls:
        print(f"\n❌ Failed URLs:")
        for url in failed_urls:
            print(f"   - {url}")
    
    return successful_files

def create_organized_ee_topics(input_files: List[str], output_file: str = "organized_ee_topics.json") -> bool:
    """
    Combine multiple Expression Écrite topic files into one organized structure
    """
    print(f"\n📋 Organizing Expression Écrite topics from {len(input_files)} files...")
    
    organized_topics = {
        "task1_topics": [],
        "task2_topics": [], 
        "task3_topics": [],
        "metadata": {
            "total_files_processed": len(input_files),
            "source_urls": []
        }
    }
    
    for filepath in input_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            source_url = data.get('source_url', 'unknown')
            organized_topics["metadata"]["source_urls"].append(source_url)
            
            topics = data.get('topics', {})
            
            # Add topics with metadata
            for task1_topic in topics.get('tache_1', []):
                topic_entry = {
                    "content": task1_topic['content'],
                    "source_url": source_url,
                    "source_file": os.path.basename(filepath),
                    "task": "tache_1",
                    "word_count": "60-120",
                    "type": "message_personnel"
                }
                organized_topics["task1_topics"].append(topic_entry)
            
            for task2_topic in topics.get('tache_2', []):
                topic_entry = {
                    "content": task2_topic['content'],
                    "source_url": source_url,
                    "source_file": os.path.basename(filepath),
                    "task": "tache_2", 
                    "word_count": "120-150",
                    "type": "article_blog"
                }
                organized_topics["task2_topics"].append(topic_entry)
            
            for task3_topic in topics.get('tache_3', []):
                topic_entry = {
                    "content": task3_topic['content'],
                    "source_url": source_url,
                    "source_file": os.path.basename(filepath),
                    "task": "tache_3",
                    "type": "texte_argumentatif",
                    "documents": task3_topic.get('documents', [])
                }
                organized_topics["task3_topics"].append(topic_entry)
                
        except Exception as e:
            print(f"⚠️ Error processing file {filepath}: {e}")
            continue
    
    # Save organized topics
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(organized_topics, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Organized topics saved to {output_file}")
        print(f"📊 Summary:")
        print(f"   - Tâche 1: {len(organized_topics['task1_topics'])} topics")
        print(f"   - Tâche 2: {len(organized_topics['task2_topics'])} topics") 
        print(f"   - Tâche 3: {len(organized_topics['task3_topics'])} topics")
        print(f"   - Total: {len(organized_topics['task1_topics']) + len(organized_topics['task2_topics']) + len(organized_topics['task3_topics'])} topics")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving organized topics: {e}")
        return False

def main():
    """
    Main function to run the TCF Expression Écrite topic scraper
    """
    # Expression Écrite URLs - modify these to match actual URLs
    urls = [
        "https://reussir-tcfcanada.com/aout-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/juillet-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/juin-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/mai-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/avril-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/mars-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/fevrier-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/janvier-2025-expression-ecrite/",
        "https://reussir-tcfcanada.com/decembre-2024-expression-ecrite/",
        "https://reussir-tcfcanada.com/novembre-2024-expression-ecrite/",
    ]
    
    print("🚀 Starting TCF Canada Expression Écrite topic scraper...")
    print(f"📋 Processing {len(urls)} URL(s)")
    
    if len(urls) == 1:
        # Single URL processing with display
        url = urls[0]
        print(f"🔍 Processing single Expression Écrite URL: {url}")
        
        topics = scrape_expression_ecrite_topics_from_url(url)
        display_ee_topics(topics)
        
        # Calculate summary
        summary = calculate_ee_summary(topics)
        
        # Save with metadata
        topics_with_metadata = {
            "source_url": url,
            "type": "expression_ecrite",
            "topics": topics,
            "summary": summary
        }
        
        filename = generate_filename_from_ee_url(url)
        save_ee_topics_to_json(topics_with_metadata, filename)
        
        print(f"\n📊 Summary:")
        for task_name, task_topics in topics.items():
            task_display = task_name.replace('_', ' ').title()
            print(f"   - {task_display}: {len(task_topics)} topics")
        print(f"   - Total: {summary['total_topics']} topics")
        
    else:
        # Multiple URLs processing
        successful_files = process_multiple_ee_urls(urls, output_dir="output")
        
        if successful_files:
            print(f"\n🎉 Successfully created {len(successful_files)} files!")
            
            # Create organized topics file
            print(f"\n📋 Creating organized topics file...")
            success = create_organized_ee_topics(successful_files, "organized_ee_topics.json")
            
            if success:
                print(f"✅ Organized Expression Écrite topics file created successfully!")
            else:
                print(f"⚠️ Failed to create organized topics file")
        else:
            print(f"\n😞 No files were created successfully.")

def main_with_custom_ee_urls(urls: List[str], output_dir: str = "output"):
    """
    Alternative main function that accepts a custom list of Expression Écrite URLs
    """
    print("🚀 Starting TCF Canada Expression Écrite topic scraper with custom URLs...")
    print(f"📋 Processing {len(urls)} URL(s)")
    print(f"📁 Output directory: {output_dir}")
    
    if not urls:
        print("❌ No URLs provided!")
        return
    
    # Process all URLs
    successful_files = process_multiple_ee_urls(urls, output_dir)
    
    if successful_files:
        print(f"\n🎉 Successfully created {len(successful_files)} files!")
        
        # Create organized topics file
        organized_file = os.path.join(output_dir, "organized_ee_topics.json")
        success = create_organized_ee_topics(successful_files, organized_file)
        
        if success:
            print(f"✅ Organized Expression Écrite topics file created successfully!")
            return successful_files + [organized_file]
        else:
            print(f"⚠️ Failed to create organized topics file")
            return successful_files
    else:
        print(f"\n😞 No files were created successfully.")
        return []

if __name__ == "__main__":
    # Example of how to use with custom URLs:
    # custom_urls = [
    #     "https://reussir-tcfcanada.com/aout-2025-expression-ecrite/",
    #     "https://reussir-tcfcanada.com/juillet-2025-expression-ecrite/",
    # ]
    # main_with_custom_ee_urls(custom_urls, "ee_output_folder")
    
    main()
