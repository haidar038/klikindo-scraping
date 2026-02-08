# KlikIndogrosir Product Scraper

A robust, Cloudflare-safe web scraper designed to extract product data (name and cheapest price) from KlikIndogrosir. This tool is built with **Playwright** and includes advanced anti-detection features to ensure reliability.

## 🚀 Features

- **Cloudflare Evasion**: Uses `playwright-stealth` and realistic browser behavior to bypass bot detection.
- **Proxy Rotation**: Automatically rotates proxies from `proxies.txt` upon detection or errors.
- **Session Persistence**: Maintains session cookies in `user_data_dir` to simulate a real user's long-term browsing.
- **Human-like Behavior**: Simulates random mouse movements, scrolling, and reading delays.
- **Robust Error Handling**: Includes retries and exponential backoff.
- **Batch Processing**: Reads URLs from `urls.txt` and saves results to `output.json`.

## 📋 Requirements

- **Python**: Version **3.8** up to **3.14** (tested on 3.10+).
- **OS**: Windows, macOS, or Linux.

## 📦 Installation

We provide automated scripts to set up the environment (Virtual Environment + Dependencies + Browser) for you.

### Windows

Double-click `install.bat` or run:

```cmd
install.bat
```

### Linux / macOS

Run the following commands:

```bash
chmod +x install.sh
./install.sh
```

---

_Manual Installation (if scripts fail):_

1. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Install Playwright browsers:
    ```bash
    playwright install
    ```

## ⚙️ Configuration

### 1. Target URLs (`urls.txt`)

Add the product URLs you want to scrape into `urls.txt`, one per line:

```text
https://www.klikindogrosir.com/product_details/0003041
https://www.klikindogrosir.com/product_details/0003701
```

### 2. Proxies (`proxies.txt`)

To enable proxy rotation, add your proxies to `proxies.txt`. Supports both authenticated and public proxies:

```text
# Format: protocol://user:pass@ip:port
http://user:pass@123.45.67.89:8080
socks5://123.45.67.89:1080
```

> **Note**: If `proxies.txt` is empty or missing, the scraper will use your direct internet connection.

## 🏃 Usage

Run the scraper using the Python in your virtual environment:

### Windows

```cmd
venv\Scripts\python scraper.py
```

### Linux / macOS

```bash
source venv/bin/activate
python scraper.py
```

### Output

- **Console**: Live progress and logging.
- **`scraper.log`**: Detailed execution logs for debugging.
- **`output.json`**: Structured data of scraped products.

```json
[
    {
        "url": "https://www.klikindogrosir.com/product_details/0003041",
        "product_name": "Product Name Example",
        "cheapest_price": 15000,
        "status": "success"
    }
]
```

## ⚠️ Disclaimer

This tool is for educational purposes only. Use it responsibly and respect the target website's Terms of Service and `robots.txt`. The author is not responsible for any misuse.
