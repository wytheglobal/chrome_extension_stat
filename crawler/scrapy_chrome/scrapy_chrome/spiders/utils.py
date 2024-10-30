import logging

def extract_image_url(link):
    if not link:
        return None
    return link.split('=')[0]

def extract_number_from_str(str, url):
    # input str like "169 ratings", "43.1K ratings"
    if not str:
        logging.warning("No user_count/rate_count found: %s", url)
        return None

    # Remove "ratings" or "users" and any whitespace
    num_str = str.split(' ')[0]

    # Handle K/M/B suffixes
    multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
    for suffix, multiplier in multipliers.items():
        if suffix in num_str:
            try:
                return int(float(num_str.replace(suffix, '')) * multiplier)
            except ValueError:
                logging.warning("Failed to parse number with suffix: %s", num_str)
                return None

    # Handle plain numbers with commas
    try:
        return int(num_str.replace(',', ''))
    except ValueError:
        logging.warning("Failed to parse number: %s", num_str)
        return None