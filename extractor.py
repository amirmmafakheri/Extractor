import argparse
import requests
import re
import threading
import time

extensions = ['.3g2', '.3gp', '.7z', '.ai', '.aif', '.apk', '.arj', '.asp', '.aspx', '.avi', '.bak', '.bat', '.bin', '.bmp',
        '.cab', '.cda', '.cer', '.cfg', '.cfm', '.cgi', '.class', '.cpl', '.cpp', '.css', '.csv', '.cur', '.dat',
        '.db', '.dbf', '.deb', '.dll', '.dmg', '.dmp', '.doc', '.docx', '.drv', '.email', '.eml', '.emlx', '.exe', '.flv',
        '.fnt', '.fon', '.gadget', '.gif', '.git', '.h264', '.hta', '.htm', '.html', '.icns', '.ico', '.inc', '.ini',
        '.iso', '.jar', '.java', '.jhtml', '.jpeg', '.jpg', '.js', '.jsa', '.jsp', '.key', '.lnk', '.log', '.m4v', '.mdb',
        '.mid', '.mkv', '.mov', '.mp3', '.mp4', '.mpa', '.mpeg', '.mpg', '.msg', '.msi', '.nsf', '.odp', '.ods', '.odt',
        '.oft', '.ogg', '.ost', '.otf', '.part', '.pcap', '.pdb', '.pdf', '.phar', '.php', '.php2', '.php3', '.php4', '.php5',
        '.php6', '.php7', '.phps', '.pht', '.phtml', '.pkg', '.pl', '.png', '.pps', '.ppt', '.pptx', '.ps', '.psd', '.pst',
        '.py', '.rar', '.reg', '.rm', '.rpm', '.rss', '.rtf', '.sav', '.sh', '.shtml', '.sql', '.svg', '.swf', '.swift',
        '.sys', '.tar', '.tar.gz', '.tex', '.tif', '.tiff', '.tmp', '.toast', '.ttf', '.txt', '.vb', '.vcd', '.vcf', '.vob',
        '.wav', '.wma', '.wmv', '.wpd', '.wpl', '.wsf', '.xhtml', '.xls', '.xlsm', '.xlsx', '.xml', '.z', '.zip','.json'
        ]

def fetch_words_from_url(url, custom_headers=None, delay=0):
    try:
        # Introduce a delay if specified
        time.sleep(delay)

        # Send an HTTP GET request to the URL with custom headers if provided
        response = requests.get(url, headers=custom_headers)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # Extract text content from the response
        page_content = response.text

        # Use regular expressions to find words (letters, digits, hyphens, and the specified extensions)
        words = re.findall(r'\w+(?:-\w+)*(?:' + '|'.join(re.escape(ext) for ext in extensions) + ')?', page_content)

        return words
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

def fetch_words_from_url_thread(url, custom_headers, delay, results):
    words = fetch_words_from_url(url, custom_headers, delay)
    results[url] = words

def fetch_words_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            urls = file.read().splitlines()
            words = set()  # Use a set to store unique words
            for url in urls:
                words.update(fetch_words_from_url(url))
            return words
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return set()

def fetch_words_from_file_parallel(listfile, custom_headers=None, delay=0):
    try:
        with open(listfile, 'r') as file:
            urls = file.read().splitlines()
        
        threads = []
        results = {}
        
        for url in urls:
            thread = threading.Thread(target=fetch_words_from_url_thread, args=(url, custom_headers, delay, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Aggregate words from all threads into a set
        words = set()
        for url_words in results.values():
            words.update(url_words)

        return words
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return set()

def fetch_words_from_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            # Read the content of the text file and split it into words
            text_content = file.read()
            words = set(re.findall(r'\w+(?:-\w+)*(?:' + '|'.join(re.escape(ext) for ext in extensions) + ')?', text_content))
            return words
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return set()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch words from web pages using URLs or a text file.")
    parser.add_argument("-l", "--listfile", help="File containing a list of URLs")
    parser.add_argument("-u", "--url", help="URL of the web page")
    parser.add_argument("-f", "--file", help="Text file containing content to parse")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads for parallel processing")
    parser.add_argument("-H", "--headers", action="append", help="Custom HTTP headers (in the format 'header:value')")
    parser.add_argument("-d", "--delay", type=float, default=0, help="Delay in seconds between HTTP requests")

    args = parser.parse_args()
    listfile = args.listfile
    url = args.url
    file = args.file
    num_threads = args.threads
    custom_headers = {}
    delay = args.delay

    if num_threads < 1:
        print("Number of threads must be greater than or equal to 1.")
        exit(1)

    # Parse custom headers from command-line arguments
    if args.headers:
        for header in args.headers:
            header_parts = header.split(':')
            if len(header_parts) == 2:
                custom_headers[header_parts[0].strip()] = header_parts[1].strip()
            else:
                print(f"Invalid header format: {header}. Use the format 'header:value'.")

    if listfile:
        words = fetch_words_from_file_parallel(listfile, custom_headers, delay)
    elif url:
        words = fetch_words_from_url(url, custom_headers, delay)
    elif file:
        words = fetch_words_from_text_file(file)
    else:
        print("You must provide either a URL, a list file, or a text file.")
        words = set()

    if words:
        print("Unique words found:")
        for word in words:
            print(word)
    else:
        print("No words found.")
