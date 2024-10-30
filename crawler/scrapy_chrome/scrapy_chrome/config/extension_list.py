import os
import json
from datetime import datetime


def formatTime(date, format_string):
    return date.strftime(format_string)

def load_chrome_extension_list():
    intput_dir = os.path.join(os.path.dirname(__file__), 'var')
    os.makedirs(intput_dir, exist_ok=True)
    
    # Find latest extension_urls file
    latest_file = None
    latest_time = None
    
    for filename in os.listdir(intput_dir):
        if filename.startswith('extension_urls_') and filename.endswith('.json'):
            file_path = os.path.join(intput_dir, filename)
            file_time = os.path.getmtime(file_path)
            
            if latest_time is None or file_time > latest_time:
                latest_time = file_time
                latest_file = file_path
    
    if latest_file:
        with open(latest_file, 'r') as f:
            return json.load(f)
            
    return {}


def generate_extension_list():
    base_dir = os.path.join(os.path.dirname(__file__), '../../../extension_list/data/extension_list/2024-10-29')
    # urls = []
    urls = {}
    
    for filename in os.listdir(base_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(base_dir, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                # category
                category = data.get('category', '')
                if '-' in category:
                    category = category.split('-')[1]
                # url items
                for item in data.get('items', []):
                    if 'href' in item:
                        url = f"https://chromewebstore.google.com{item['href']}"
                        if item['id'] in urls:
                            print(f"Warning: Duplicate extension ID found: {item['id']}")
                        urls[item['id']] = {
                            'url': url,
                            'category': category
                        }
                        # urls.append({
                        #     'url': url,
                        #     'category': data.get('category', '')
                        # })

    return urls

def save_chrome_extension_list(data):
    output_dir = os.path.join(os.path.dirname(__file__), 'var')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = formatTime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    output_file = os.path.join(output_dir, f'extension_urls_{timestamp}.json')
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"URLs saved to: {output_file}")

def check_duplicate_urls(urls):
    unique_urls = set(urls)
    print(f"Total URLs: {len(urls)}")
    print(f"Unique URLs: {len(unique_urls)}")
    print(f"Duplicate URLs: {len(urls) - len(unique_urls)}")
    if len(urls) != len(unique_urls):
        print("Duplicates found!")
        for url in unique_urls:
            if urls.count(url) > 1:
                print(f"Duplicate URL: {url}")
    else:
        print("No duplicates found.")


if __name__ == "__main__":
    import sys

    # Get command line arguments
    args = sys.argv[1:]

    # Default mode
    mode = 'all'
    if len(args) > 0:
        mode = args[0]

    if mode == 'generate':
        # Only check for duplicates
        urls = generate_extension_list()
        save_chrome_extension_list(urls)
    elif mode == 'load':
        # Only save URLs
        urls = load_chrome_extension_list() 
        print(urls)
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: generate, load")
        sys.exit(1)