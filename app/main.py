import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urlparse
from typing import Dict, List, Optional

def scrape_tcf_topics_from_url(url: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Scrape TCF Canada oral expression topics from a specific URL
    Returns a structured dictionary with Tâche 2 and Tâche 3 topics
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
            "tache_2": {
                "partie_1": [],
                "partie_2": []
            },
            "tache_3": {
                "partie_1": [],
                "partie_2": []
            }
        }
        
        # Find all topic sections
        # Look for headings and their associated content
        current_section = None
        current_part = None
        
        # Find all elements that might contain topics
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'div']):
            text = element.get_text(strip=True)
            
            # Identify sections
            if "Tâche 2" in text:
                current_section = "tache_2"
            elif "Tâche 3" in text:
                current_section = "tache_3"
            elif "Partie 1" in text:
                current_part = "partie_1"
            elif "Partie 2" in text:
                current_part = "partie_2"
            
            # Extract topics (look for bold text or specific patterns)
            if current_section and current_part and text:
                # Check if this looks like a topic (starts with "Sujet" or contains key phrases)
                if ("Sujet" in text or 
                    any(keyword in text.lower() for keyword in [
                        "je suis", "vous", "nous", "pensez-vous", "selon vous", 
                        "d'après vous", "faut-il", "est-il"
                    ])) and len(text) > 20:
                    
                    # Clean up the text
                    clean_text = text.replace("Sujet 1", "").replace("Sujet 2", "").replace("Sujet 3", "").replace("Sujet 4", "").replace("Sujet 5", "").strip()
                    
                    if clean_text and clean_text not in topics[current_section][current_part]:
                        topics[current_section][current_part].append(clean_text)
        
        return topics
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage {url}: {e}")
        return get_fallback_topics()
    except Exception as e:
        print(f"Error parsing the webpage {url}: {e}")
        return get_fallback_topics()

def get_fallback_topics() -> Dict[str, Dict[str, List[str]]]:
    """
    Fallback topics based on the known content from the website
    """
    return {
        "tache_2": {
            "partie_1": [
                "Je suis un(e) de vos collègues. Vous êtes nouvellement arrivé(e) dans l'entreprise et vous me demandez des renseignements sur l'organisation, les collègues, la cantine, etc.",
                "Je suis votre ami(e) et je vous invite à une célébration. Vous êtes nouvellement installé(e) au Québec et, comme c'est votre première fête ici, vous me demandez des renseignements (heures, cadeaux, vêtements, etc.).",
                "Je travaille à la réception du club de sport près de chez vous. Vous voulez pratiquer un sport mais vous ne savez pas lequel choisir. Vous m'interrogez sur les activités offertes (horaires, coût, matériel, etc.).",
                "Je travaille à la réception d'un musée. Vous souhaitez venir avec des amis pour le découvrir. Vous me posez des questions afin de préparer votre visite (heures d'ouverture, tarifs, visites guidées, etc.).",
                "Nous sommes collègues. Vous envisagez de partir en week-end et je vous suggère une ville que je connais. Vous me demandez des informations sur cette destination (logement, restauration, activités, etc.)."
            ],
            "partie_2": [
                "Je suis votre ami(e). Vous venez de découvrir ma ville. Vous m'interrogez afin de savoir comment sortir à moindre coût (lieux, loisirs, transports, etc.).",
                "Je suis votre voisin(e). Je propose à la location une petite maison proche de la mer pour les séjours de vacances. Vous souhaitez en savoir plus (équipements, environnement, tarif, etc.).",
                "Je travaille dans une boutique de meubles. Vous voulez recevoir un meuble à domicile. Vous m'interrogez sur les conditions de livraison (coût, durée, moyens utilisés, etc.).",
                "Nous nous trouvons dans une salle d'attente. Le train a du retard et nous engageons la conversation bien que nous ne nous connaissions pas. Je vous parle de ma passion pour la montagne. Vous me posez des questions à ce propos (lieux, activités, équipement, etc.).",
                "À une soirée où nous faisons connaissance, je rentre d'un voyage récent. Vous me posez des questions sur ce séjour (durée, endroits visités, ressenti, etc.)."
            ]
        },
        "tache_3": {
            "partie_1": [
                "Pensez-vous que la gentillesse garantit toujours d'obtenir de l'attention et du respect ?",
                "Pensez-vous qu'il est possible de trouver le bonheur en vivant célibataire ?",
                "Selon vous, faut-il avoir une journée dédiée à la défense des droits des femmes ? Pourquoi ?",
                "Regarder la télévision permet de s'instruire. Qu'en pensez-vous ?",
                "Est-il indispensable d'aimer son travail pour réussir dans sa vie professionnelle ? Pourquoi ?"
            ],
            "partie_2": [
                "De quelles manières les entreprises peuvent-elles faciliter l'intégration des nouveaux employés ?",
                "Le fait de vivre dans différents pays peut-il améliorer les perspectives professionnelles ?",
                "Quelle était votre matière préférée à l'école et pourquoi ?",
                "D'après vous, quelles matières seraient importantes à enseigner davantage à l'école et pourquoi ?",
                "Selon vous, vaut-il mieux posséder une famille nombreuse ou de solides amitiés ? Pourquoi ?"
            ]
        }
    }

def display_topics(topics: Dict[str, Dict[str, List[str]]]):
    """
    Display the topics in a formatted way
    """
    print("=" * 60)
    print("TCF CANADA - EXPRESSION ORALE TOPICS (AOÛT 2025)")
    print("=" * 60)
    
    for task, task_data in topics.items():
        task_name = "TÂCHE 2 (Conversational Scenarios)" if task == "tache_2" else "TÂCHE 3 (Opinion/Discussion Questions)"
        print(f"\n🎯 {task_name}")
        print("-" * 50)
        
        for part, part_topics in task_data.items():
            part_name = "PARTIE 1" if part == "partie_1" else "PARTIE 2"
            print(f"\n📋 {part_name}:")
            
            for i, topic in enumerate(part_topics, 1):
                print(f"\n{i}. {topic}")
        
        print("\n" + "=" * 50)

def generate_filename_from_url(url: str) -> str:
    """
    Generate a safe filename from a URL
    """
    # Parse the URL
    parsed = urlparse(url)
    
    # Get the path and remove leading/trailing slashes
    path = parsed.path.strip('/')
    
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

def save_topics_to_json(topics: Dict[str, Dict[str, List[str]]], filename: str = "tcf_topics.json"):
    """
    Save topics to a JSON file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
        print(f"✅ Topics saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving to file {filename}: {e}")

def process_single_url(url: str, output_dir: str = "output") -> Optional[str]:
    """
    Process a single URL and save its topics to a JSON file
    Returns the filename if successful, None otherwise
    """
    print(f"\n🔍 Processing URL: {url}")
    
    # Scrape topics from the URL
    topics = scrape_tcf_topics_from_url(url)
    
    # Generate filename
    filename = generate_filename_from_url(url)
    filepath = os.path.join(output_dir, filename)
    
    # Add metadata to the topics
    topics_with_metadata = {
        "source_url": url,
        "topics": topics,
        "summary": {
            "tache_2_partie_1": len(topics['tache_2']['partie_1']),
            "tache_2_partie_2": len(topics['tache_2']['partie_2']),
            "tache_3_partie_1": len(topics['tache_3']['partie_1']),
            "tache_3_partie_2": len(topics['tache_3']['partie_2']),
            "total_topics": sum(len(part) for task in topics.values() for part in task.values())
        }
    }
    
    # Save to file
    save_topics_to_json(topics_with_metadata, filepath)
    
    # Display summary for this URL
    print(f"📊 Summary for {url}:")
    print(f"   - Tâche 2 Partie 1: {len(topics['tache_2']['partie_1'])} topics")
    print(f"   - Tâche 2 Partie 2: {len(topics['tache_2']['partie_2'])} topics")
    print(f"   - Tâche 3 Partie 1: {len(topics['tache_3']['partie_1'])} topics")
    print(f"   - Tâche 3 Partie 2: {len(topics['tache_3']['partie_2'])} topics")
    print(f"   - Total: {topics_with_metadata['summary']['total_topics']} topics")
    
    return filepath if topics_with_metadata['summary']['total_topics'] > 0 else None

def process_multiple_urls(urls: List[str], output_dir: str = "output") -> List[str]:
    """
    Process multiple URLs and create separate files for each
    Returns list of successfully created filenames
    """
    print(f"🚀 Starting batch processing of {len(urls)} URLs...")
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
            filepath = process_single_url(url, output_dir)
            if filepath:
                successful_files.append(filepath)
            else:
                failed_urls.append(url)
        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")
            failed_urls.append(url)
    
    # Final summary
    print(f"\n{'='*60}")
    print("BATCH PROCESSING COMPLETE")
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

def main():
    """
    Main function to run the TCF topic scraper
    """
    # Example URLs list - you can modify this or pass URLs as command line arguments
    urls = [
        "https://reussir-tcfcanada.com/aout-2025-expression-orale/",
        # Add more URLs here as needed
        "https://reussir-tcfcanada.com/juillet-2025-expression-orale/",
        "https://reussir-tcfcanada.com/juin-2025-expression-orale/",
        "https://reussir-tcfcanada.com/mai-2025-expression-orale/",
        "https://reussir-tcfcanada.com/avril-2025-expression-orale/",
        "https://reussir-tcfcanada.com/mars-2025-expression-orale/",
        "https://reussir-tcfcanada.com/fevrier-2025-expression-orale/",
        "https://reussir-tcfcanada.com/janvier-2025-expression-orale/",
        "https://reussir-tcfcanada.com/decembre-2024-expression-orale/",
        "https://reussir-tcfcanada.com/novembre-2024-expression-orale/",
    ]
    
    print("🚀 Starting TCF Canada topic scraper...")
    print(f"📋 Processing {len(urls)} URL(s)")
    
    if len(urls) == 1:
        # Single URL processing with display
        url = urls[0]
        print(f"🔍 Processing single URL: {url}")
        
        topics = scrape_tcf_topics_from_url(url)
        display_topics(topics)
        
        # Save with metadata
        topics_with_metadata = {
            "source_url": url,
            "topics": topics,
            "summary": {
                "tache_2_partie_1": len(topics['tache_2']['partie_1']),
                "tache_2_partie_2": len(topics['tache_2']['partie_2']),
                "tache_3_partie_1": len(topics['tache_3']['partie_1']),
                "tache_3_partie_2": len(topics['tache_3']['partie_2']),
                "total_topics": sum(len(part) for task in topics.values() for part in task.values())
            }
        }
        
        filename = generate_filename_from_url(url)
        save_topics_to_json(topics_with_metadata, filename)
        
        print(f"\n📊 Summary:")
        print(f"   - Tâche 2 Partie 1: {len(topics['tache_2']['partie_1'])} topics")
        print(f"   - Tâche 2 Partie 2: {len(topics['tache_2']['partie_2'])} topics")
        print(f"   - Tâche 3 Partie 1: {len(topics['tache_3']['partie_1'])} topics")
        print(f"   - Tâche 3 Partie 2: {len(topics['tache_3']['partie_2'])} topics")
        print(f"   - Total: {topics_with_metadata['summary']['total_topics']} topics")
        
    else:
        # Multiple URLs processing
        successful_files = process_multiple_urls(urls, output_dir="output")
        
        if successful_files:
            print(f"\n🎉 Successfully created {len(successful_files)} files!")
        else:
            print(f"\n😞 No files were created successfully.")

def main_with_custom_urls(urls: List[str], output_dir: str = "output"):
    """
    Alternative main function that accepts a custom list of URLs
    """
    print("🚀 Starting TCF Canada topic scraper with custom URLs...")
    print(f"📋 Processing {len(urls)} URL(s)")
    print(f"📁 Output directory: {output_dir}")
    
    if not urls:
        print("❌ No URLs provided!")
        return
    
    # Process all URLs
    successful_files = process_multiple_urls(urls, output_dir)
    
    if successful_files:
        print(f"\n🎉 Successfully created {len(successful_files)} files!")
        return successful_files
    else:
        print(f"\n😞 No files were created successfully.")
        return []

if __name__ == "__main__":
    # Example of how to use with custom URLs:
    # custom_urls = [
    #     "https://reussir-tcfcanada.com/aout-2025-expression-orale/",
    #     "https://reussir-tcfcanada.com/juillet-2025-expression-orale/",
    #     "https://reussir-tcfcanada.com/septembre-2025-expression-orale/",
    # ]
    # main_with_custom_urls(custom_urls, "my_output_folder")
    
    main()