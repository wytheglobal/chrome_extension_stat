import os
import json
from datetime import datetime


def formatTime(date, format_string):
    return date.strftime(format_string)

def load_chrome_extension_list():
    base_dir = os.path.join(os.path.dirname(__file__), '../../../extension_list/data/extension_list/2024-10-17')
    urls = []
    
    for filename in os.listdir(base_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(base_dir, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                for item in data.get('items', []):
                    if 'href' in item:
                        url = f"https://chromewebstore.google.com{item['href']}"
                        urls.append(url)

    return urls

def save_chrome_extension_list(urls):
    output_dir = os.path.join(os.path.dirname(__file__), 'var')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = formatTime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    output_file = os.path.join(output_dir, f'extension_urls_{timestamp}.json')
    
    with open(output_file, 'w') as f:
        json.dump({'urls': urls}, f, indent=2)
    print(f"URLs saved to: {output_file}")