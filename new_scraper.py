#!/usr/bin/env python3
import requests
from lxml import html
from urllib.parse import urljoin, urlparse
import concurrent.futures
import threading

# --- Configuration ---
MAX_DEPTH = 30
MAX_THREADS = 10     # How many IPs to scan simultaneously
TIMEOUT = 5
TARGET_STYLE = 'opacity: .0'

# A lock to stop text from getting jumbled in the console
print_lock = threading.Lock()

def safe_print(message):
    """Helper to print safely from multiple threads."""
    with print_lock:
        print(message)

def crawl_recursive(url, current_depth, visited):
    """
    The recursive logic.
    Note: 'visited' is passed in so it is local to this specific target's thread.
    """
    if current_depth > MAX_DEPTH or url in visited:
        return

    visited.add(url)
    
    # Only print "Scanning" for the top level to reduce noise, 
    
    if current_depth == 1:
        safe_print(f"[*] Starting scan on: {url}")

    try:
        response = requests.get(url, timeout=TIMEOUT)
        
        # Skip non-HTML content
        if "text/html" not in response.headers.get('Content-Type', ''):
            return

        tree = html.fromstring(response.content)

        # 1. Search for the hidden style
        xpath_query = f'//*[contains(@style, "{TARGET_STYLE}")]'
        hidden_elements = tree.xpath(xpath_query)

        if hidden_elements:
            with print_lock:
                print(f"\n[!!!] HIT FOUND on: {url}")
                print(f"      Count: {len(hidden_elements)}")
                for elem in hidden_elements:
                     print(f"      Tag: <{elem.tag}>")
                     print(f"      Text: <{elem.text}>")
                print("-" * 40)

        # 2. Go Deeper
        if current_depth < MAX_DEPTH:
            links = tree.xpath('//a/@href')
            for link in links:
                absolute_link = urljoin(url, link)
                
                # Stay on the same domain/IP
                if urlparse(url).netloc == urlparse(absolute_link).netloc:
                    crawl_recursive(absolute_link, current_depth + 1, visited)

    except requests.exceptions.RequestException:
        pass
    except Exception as e:
        safe_print(f"[!] Error on {url}: {e}")

def worker_entry(ip):
    """
    This is the function that the ThreadPool calls.
    It prepares the URL and the visited set for the crawler.
    """
    start_url = f"http://{ip}"
    # Create a fresh visited set for this specific target
    local_visited = set()
    crawl_recursive(start_url, 1, local_visited)

# --- Main Execution ---
if __name__ == "__main__":
    # Example List of Targets
    targets = [
            "192.168.28.100:80", 
            "192.168.28.111:80",
            "192.168.28.111:8080"
            ]

    print(f"--- Starting Multi-Threaded Scan ---")
    print(f"--- Threads: {MAX_THREADS} | Max Depth: {MAX_DEPTH} ---")

    # The ThreadPoolExecutor manages the heavy lifting
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # map() runs 'worker_entry' on every item in 'targets'
        executor.map(worker_entry, targets)
        
    print("--- Scan Complete ---")
