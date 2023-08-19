import re
import argparse
import requests
import threading
import time
from queue import Queue

extensions_to_combine = [
    '.3g2', '.3gp', '.7z', '.ai', '.aif', '.apk', '.arj', '.asp', '.aspx', '.avi', '.bak', '.bat', '.bin', '.bmp',
    '.c', '.cab', '.cda', '.cer', '.cfg', '.cfm', '.cgi', '.class', '.cpl', '.cpp', '.cs', '.css', '.csv', '.cur', '.dat',
    '.db', '.dbf', '.deb', '.dll', '.dmg', '.dmp', '.doc', '.docx', '.drv', '.email', '.eml', '.emlx', '.exe', '.flv',
    '.fnt', '.fon', '.gadget', '.gif', '.git', '.h', '.h264', '.hta', '.htm', '.html', '.icns', '.ico', '.inc', '.ini',
    '.iso', '.jar', '.java', '.jhtml', '.jpeg', '.jpg', '.js', '.jsa', '.jsp', '.key', '.lnk', '.log', '.m4v', '.mdb',
    '.mid', '.mkv', '.mov', '.mp3', '.mp4', '.mpa', '.mpeg', '.mpg', '.msg', '.msi', '.nsf', '.odp', '.ods', '.odt',
    '.oft', '.ogg', '.ost', '.otf', '.part', '.pcap', '.pdb', '.pdf', '.phar', '.php', '.php2', '.php3', '.php4', '.php5',
    '.php6', '.php7', '.phps', '.pht', '.phtml', '.pkg', '.pl', '.png', '.pps', '.ppt', '.pptx', '.ps', '.psd', '.pst',
    '.py', '.rar', '.reg', '.rm', '.rpm', '.rss', '.rtf', '.sav', '.sh', '.shtml', '.sql', '.svg', '.swf', '.swift',
    '.sys', '.tar', '.tar.gz', '.tex', '.tif', '.tiff', '.tmp', '.toast', '.ttf', '.txt', '.vb', '.vcd', '.vcf', '.vob',
    '.wav', '.wma', '.wmv', '.wpd', '.wpl', '.wsf', '.xhtml', '.xls', '.xlsm', '.xlsx', '.xml', '.z', '.zip'
    ]

# Worker function for fetching URLs and processing content
def worker(url_queue, js_content_list, delay, headers):
    while not url_queue.empty():
        url = url_queue.get()
        response = requests.get(url, headers=headers)
        js_content_list.append(response.text)
        url_queue.task_done()
        time.sleep(delay)

# Create an argument parser
parser = argparse.ArgumentParser(description='Extract all words from JavaScript files.')
parser.add_argument('-f', '--file', type=str, help='Path to the local JavaScript file')
parser.add_argument('-u', '--url', type=str, help='URL to a single JavaScript file')
parser.add_argument('-l', '--url_list', type=str, help='Path to a text file containing a list of URLs')
parser.add_argument('-fe', '--filter_extensions', nargs='+', type=str, help='List of extensions to filter')
parser.add_argument('-ne', '--not_to_exclude', nargs='+', type=str, help='List of extensions not to exclude')
parser.add_argument('-o', '--output', type=str, help='Path to the output file')
parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads for parallel processing')
parser.add_argument('-d', '--delay', type=float, default=0, help='Delay in seconds between fetching URLs')
parser.add_argument('-H', '--headers', nargs='+', type=str, help='Custom headers in format "HeaderName: HeaderValue"')
parser.add_argument('-all', action='store_true', help='Extract all words from the page')

# Parse the command line arguments
args = parser.parse_args()

# Parse custom headers if provided
headers = {}
if args.headers:
    for header in args.headers:
        header_name, header_value = map(str.strip, header.split(':', 1))
        headers[header_name] = header_value

# Read the JavaScript content
if args.file:
    with open(args.file, 'r') as file:
        js_content = file.read()
elif args.url:
    response = requests.get(args.url, headers=headers)
    js_content = response.text
elif args.url_list:
    with open(args.url_list, 'r') as url_file:
        urls = url_file.read().splitlines()

        # Use threading to fetch URLs in parallel
        url_queue = Queue()
        for url in urls:
            url_queue.put(url)
        
        js_content_list = []
        threads = []
        for _ in range(args.threads):
            thread = threading.Thread(target=worker, args=(url_queue, js_content_list, args.delay, headers))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        js_content = ''.join(js_content_list)
else:
    print("Please provide either -f, -u, or -l option.")
    exit()

# Check if the -all switch is provided
if args.all:
    # Extract all words from the content (you can define your own regex pattern here)
    all_words = re.findall(r'\b[\w-]+\b', js_content)

    unique_words = set(all_words)  # Convert the list to a set to get unique words
    
    print("Unique All Words:")
    for word in unique_words:
        print(word)

    all_words2 = re.findall(r'\b(\w+)\.(\w+)\b', js_content)

    unique_words2 = set()  # Create a set for unique word.ext combinations

    for word, ext in all_words2:
        if f'.{ext}' in extensions_to_combine:  # Check if the extension is in the list
            word_ext = f"{word}.{ext}"
            print(word_ext)
            unique_words2.add(word_ext)


else:
    # Define extensions to be treated as a single unit

    # Filter extensions if provided
    if args.filter_extensions:
        extensions_to_combine = [ext for ext in extensions_to_combine if ext in args.filter_extensions]

    # Exclude extensions specified in not_to_exclude
    if args.not_to_exclude:
        extensions_to_combine = [ext for ext in extensions_to_combine if ext not in args.not_to_exclude]

    # Construct a regular expression pattern for combined extensions
    combined_extensions_pattern = '|'.join(re.escape(ext) for ext in extensions_to_combine)

    # Construct the full regular expression pattern
    full_pattern = r'(\b[\w-]+)(' + combined_extensions_pattern + r')\b'

    # Extract all words using regular expression
    matched_words = re.findall(full_pattern, js_content)

    # Store unique words in a set
    unique_words = set()
    for word, ext in matched_words:
        unique_words.add(f"{word}{ext}")

    # Save the output to the specified file or print to console
    if args.output:
        with open(args.output, 'w') as output_file:
            for unique_word in unique_words:
                output_file.write(f"{unique_word}\n")
    else:
        for unique_word in unique_words:
            print(unique_word)
