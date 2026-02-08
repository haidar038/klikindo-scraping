# KlikIndogrosir Product Scraper

A robust, Cloudflare-safe web scraper designed to extract product data (name, cheapest price, and stock availability) from KlikIndogrosir. This tool is built with **Playwright** and includes advanced anti-detection features and resilience mechanisms for large-scale scraping.

## 🚀 Features

- **Cloudflare Evasion**: Uses `playwright-stealth` and real browser behavior to bypass bot detection.
- **Stock Availability Detection**: Accurately identifies if a product is in stock or out of stock.
- **Real-Time CSV Saving**: Data is appended to `output.csv` immediately after scraping each item, preventing data loss.
- **Checkpoint & Resume**: Automatically saves progress to `checkpoint.json`. If interrupted, simply run the script again to resume from where it left off.
- **Flexible Proxy Support**: Supports both proxy rotation and **No-Proxy Safe Mode** (Direct Connection with moderate delays).
- **Session Persistence**: Maintains session cookies in `user_data_dir` to simulate a real user's long-term browsing.
- **Batch Processing Settings**: Configurable batch pauses (e.g., pause every 50 URLs) to reduce ban risk.

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

### 2. Proxies (`http_proxies.txt` or `indo_proxies.txt`)

To enable proxy rotation, update `PROXY_FILE` in `scraper.py` to point to your proxy list file.
To run **without proxies** (uses your own IP), set `PROXY_FILE` to an empty string `""` in `scraper.py`.

### 3. Delays & Safety

Open `scraper.py` to adjust:

- `human_delay`: Time between requests.
- `BATCH_SIZE`: Number of URLs before taking a long break.
- `BATCH_PAUSE_MIN` / `BATCH_PAUSE_MAX`: Duration of the batch break.

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

## 📊 Output

### 1. `output.csv` (Real-Time)

Data is saved here **immediately** as it is scraped. Open this file to monitor progress.
Columns: `url`, `product_name`, `cheapest_price`, `stock_available`, `status`, `timestamp`

### 2. `output.json` (Final Summary)

Generated at the very end of the process, containing the full list of results.

### 3. `checkpoint.json`

A temporary file used to store progress. **Delete this file if you want to restart scraping from the beginning.**

## ⚠️ Disclaimer

This tool is for educational purposes only. Use it responsibly and respect the target website's Terms of Service and `robots.txt`. The author is not responsible for any misuse.
