# Extractor

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Purpose](https://img.shields.io/badge/type-contact_extractor-yellow.svg)

`Extractor` is a command-line tool that scans HTML or text content to extract useful information such as phone numbers, emails, and URLs. It's designed for use in web scraping, OSINT, or data cleaning tasks.

---

## ⚙️ Features

- Extracts:
  - Phone numbers (Iran format supported)
  - Email addresses
  - URLs (absolute and relative)
- Accepts raw HTML/text input
- Outputs to console or optionally to file
- Easy to extend with new regex patterns

---

## 📁 Files

- `extractor.py`: Main script for extraction
- (Optional input files or URL sources)

---

## 📦 Requirements

- Python 3.8+
- `re` (built-in)
- `argparse` (built-in)

---

## 🚀 Usage

```bash
python extractor.py -i input.txt -o output.txt
```

### Options

| Flag | Description |
|------|-------------|
| `-i`, `--input` | Path to input file containing HTML/text |
| `-o`, `--output` | Path to save extracted results (optional) |

---

## 🧪 Example

```bash
python extractor.py -i sample.html
```

Output:

```
[+] Phone: 09121234567
[+] Email: example@email.com
[+] URL: https://example.com/page
```

---

## 🛠 How it Works

1. Reads content from an input file
2. Uses regex patterns to find phones, emails, and URLs
3. Prints results or saves to file if specified

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author

Developed by [Your Name]. Contributions and suggestions are welcome!
