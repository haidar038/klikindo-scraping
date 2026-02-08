# KlikIndogrosir Product Scraper

A robust, Cloudflare-safe web scraper designed to extract product data from KlikIndogrosir. Features real-time data saving and automatic resume capabilities.

## 🚀 Features

- **Real-Time Saving**:
    - **CSV**: Data appended to `output.csv` immediately.
    - **JSONL**: Data appended to `output.jsonl` immediately (safe for interruptions).
- **Auto-Resume**: Automatically detects progress by counting lines in `output.csv`. No manual configuration needed.
- **Cloudflare Evasion**: Uses `playwright-stealth` and real browser behavior.
- **Stock Detection**: Identifies stock availability.
- **Flexible Proxy Support**: Supports both proxy rotation and **No-Proxy Safe Mode**.

## 📋 Requirements & Installation

See `install.bat` (Windows) or `install.sh` (Linux/macOS) for automated setup.
Or manually:

```bash
pip install -r requirements.txt
playwright install
```

## ⚙️ Configuration

1.  **Target URLs**: Edit `urls.txt`.
2.  **Proxies**: Edit `scraper.py` (set `PROXY_FILE` to `indo_proxies.txt` or `""` for direct).
3.  **Delays**: Edit `scraper.py` constants (`human_delay`, `BATCH_SIZE`).

## 🏃 Usage

```bash
python scraper.py
```

## 📊 Output

### 1. `output.csv` (Primary)

- Real-time data.
- Used for **Resume Logic** (script counts lines here to know where to start).
- **Delete this file to restart scraping from the beginning.**

### 2. `output.jsonl` (Real-Time JSON)

- Newline Delimited JSON. Each line is a JSON object.
- Best for programmatic processing of large datasets.

### 3. `output.json` (Final)

- Generated only when the script completes successfully.
- Contains the full array of data.

## ⚠️ Disclaimer

Educational purposes only. Respect `robots.txt`.
