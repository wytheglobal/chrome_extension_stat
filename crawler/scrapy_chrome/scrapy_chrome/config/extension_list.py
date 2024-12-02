import os
import json
from datetime import datetime


def formatTime(date, format_string):
    return date.strftime(format_string)

def find_nth_newest_file(directory, n=0, prefix='', suffix=''):
    """
    Load the nth newest file from a directory that matches prefix and suffix.
    Args:
        directory (str): Directory path to search in
        n (int): Which file to get - 0 is newest, 1 is second newest, etc.
        prefix (str): Required prefix of filename
        suffix (str): Required suffix of filename
    Returns:
        str: Path to the nth newest file, or None if not found
    """
    matching_files = []
    
    # Get all matching files with their timestamps
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and filename.endswith(suffix):
            file_path = os.path.join(directory, filename)
            matching_files.append((file_path, os.path.getmtime(file_path)))
            
    if not matching_files:
        return None
        
    # Sort by timestamp descending
    matching_files.sort(key=lambda x: x[1], reverse=True)
    
    # Return nth file if it exists
    if n < len(matching_files):
        return matching_files[n][0]
        
    return None


def load_chrome_extension_list():
    intput_dir = os.path.join(os.path.dirname(__file__), 'var')
    os.makedirs(intput_dir, exist_ok=True)

    # Find latest extension_urls file
    latest_file = find_nth_newest_file(intput_dir, n=0, prefix='extension_urls_', suffix='.json')
    previous_file = find_nth_newest_file(intput_dir, n=1, prefix='extension_urls_', suffix='.json')

    
    if latest_file:
        print(f"Loading extension list from: {latest_file}")
        with open(latest_file, 'r') as f:
            latest_data = json.load(f)
    if previous_file:
        print(f"Loading extension list from: {previous_file}")
        with open(previous_file, 'r') as f:
            previous_data = json.load(f)

    return (latest_data | previous_data)

def find_new_extensions():
    intput_dir = os.path.join(os.path.dirname(__file__), 'var')

    latest_file = find_nth_newest_file(intput_dir, n=0, prefix='extension_urls_', suffix='.json')
    previous_file = find_nth_newest_file(intput_dir, n=1, prefix='extension_urls_', suffix='.json')

    with open(latest_file, 'r') as f:
        latest_data = json.load(f)
    with open(previous_file, 'r') as f:
        previous_data = json.load(f)

    print("latest_file: ", latest_file, "len: ", len(latest_data))
    print("previous_file: ", previous_file, "len: ", len(previous_data))
    print("increase: ", len(latest_data.keys() - previous_data.keys()))
    print("decrease: ", len(previous_data.keys() - latest_data.keys()))

    return len(latest_data.keys() - previous_data.keys())


def generate_extension_list():
    base_dir = os.path.join(os.path.dirname(__file__), '../../../extension_list/data/extension_list/2024-11-26')
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
        print(len(urls))
    elif mode == 'find_new':
        new_extensions = find_new_extensions()
        print(new_extensions)
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: generate, load")
        sys.exit(1)