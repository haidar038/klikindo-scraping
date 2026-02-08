import json
import time
import random
import logging
import re
import shutil
import csv
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
INPUT_FILE = "urls.txt"
OUTPUT_FILE = "output.json"
OUTPUT_JSONL = "output.jsonl"  # Real-time JSON Lines
PROXY_FILE = ""  # Disabled: Direct Connection
LOG_FILE = "scraper.log"
USER_DATA_DIR = "user_data_dir"  # Folder for persistent session/cookies
CHECKPOINT_FILE = "checkpoint.json"  # For resume capability

# Settings for Direct Connection (No Proxy)
# We need moderate delays to avoid immediate IP bans, but not as slow as 60s
BATCH_SIZE = 50  # Pause after this many URLs
BATCH_PAUSE_MIN = 60  # 1 minute
BATCH_PAUSE_MAX = 120  # 2 minutes
SESSION_ROTATE_EVERY = 200  # Rotate session less frequently

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import stealth, warn if not present
try:
    from playwright_stealth import Stealth
except ImportError:
    logger.warning("playwright-stealth not found! Running without stealth module.")
    Stealth = None

def load_proxies():
    """Load proxies from file."""
    if not PROXY_FILE or not Path(PROXY_FILE).exists():
        return []
    
    proxies = []
    with open(PROXY_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Basic format check/fix
                if "://" not in line:
                    # Assume http if no protocol specified
                    line = f"http://{line}" 
                proxies.append(line)
    return proxies

def human_delay(min_seconds=10, max_seconds=20):
    """Random delay to simulate human reading time. Moderate delay for Direct Connection."""
    sleep_time = random.uniform(min_seconds, max_seconds)
    logger.info(f"Waiting {sleep_time:.1f} seconds...")
    time.sleep(sleep_time)

def append_to_csv(data):
    """Appends a single data row to output.csv immediately."""
    csv_file = "output.csv"
    csv_columns = ["url", "product_name", "cheapest_price", "stock_available", "status", "timestamp"]
    
    # Add timestamp
    data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    file_exists = Path(csv_file).exists()
    
    try:
        with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
    except IOError as e:
        logger.error(f"I/O error appending to {csv_file}: {e}")

def append_to_jsonl(data):
    """Appends a single data row to output.jsonl immediately."""
    try:
        with open(OUTPUT_JSONL, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except IOError as e:
        logger.error(f"I/O error appending to {OUTPUT_JSONL}: {e}")

def get_processed_count():
    """Returns number of processed items based on output.csv line count (minus header)."""
    csv_file = "output.csv"
    if not Path(csv_file).exists():
        return 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Efficiently count lines
            return sum(1 for line in f) - 1 # Minus header
    except:
        return 0

def simulate_interaction(page):
    """Simulates mouse movements and scrolling to appear human-like."""
    try:
        # Random mouse movement
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 1000)
            y = random.randint(100, 800)
            try:
                page.mouse.move(x, y)
            except:
                pass
            time.sleep(random.uniform(0.1, 0.5))

        # Scroll down
        page.mouse.wheel(0, random.randint(200, 500))
        time.sleep(random.uniform(1, 2))
        
        # Scroll up slightly
        page.mouse.wheel(0, random.randint(-100, -50))
        time.sleep(random.uniform(0.5, 1))

    except Exception as e:
        logger.warning(f"Interaction simulation error: {e}")

def scrape_product(page, url):
    logger.info(f"Navigating to: {url}")
    
    # Retry logic for navigation
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Standard timeout for direct connection
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Failed to load {url} after {max_retries} attempts")
                # Don't raise on direct connection, just fail this URL
                # raise 
            time.sleep(random.uniform(5, 10))

    human_delay(2, 4) # Initial delay after load
    # simulate_interaction(page) # Optional: Enable if specific behavior checks needed
    # human_delay(1, 2)

    product_data = {
        "url": url,
        "product_name": None,
        "cheapest_price": None,
        "stock_available": None,
        "status": "failed"
    }

    # Extract Product Name
    try:
        # Strategy 1 (Preferred): Open Graph Title
        # <meta property="og:title" content="BIMOLI MINYAK GORENG  DRG 5000mL | Klik Indogrosir" />
        og_title_el = page.locator("meta[property='og:title']").first
        if og_title_el.count() > 0:
            raw_title = og_title_el.get_attribute("content")
            if raw_title:
                # Remove the site name suffix if present
                clean_title = raw_title.split("|")[0].strip()
                product_data["product_name"] = re.sub(r'\s+', ' ', clean_title)
        
        # Strategy 2: H4 (Fallback)
        if not product_data["product_name"]:
            product_name_locator = page.locator(".col-lg-8 h4").first
            if product_name_locator.count() > 0:
                clean_title = product_name_locator.text_content().strip()
                product_data["product_name"] = re.sub(r'\s+', ' ', clean_title)
            elif page.locator("h4").count() > 0:
                 # Filter out "Masuk ke Akun"
                 for i in range(page.locator("h4").count()):
                     text = page.locator("h4").nth(i).text_content().strip()
                     if "Masuk" not in text and "Login" not in text:
                         product_data["product_name"] = re.sub(r'\s+', ' ', text)
                         break
                         
        # Strategy 3: Meta Title (Fallback)
        if not product_data["product_name"]:
             title_el = page.locator("title")
             if title_el.count() > 0:
                 raw_title = title_el.first.text_content().strip()
                 clean_title = raw_title.split("|")[0].strip()
                 product_data["product_name"] = re.sub(r'\s+', ' ', clean_title)

    except Exception as e:
        logger.warning(f"Error extracting name for {url}: {e}")

    # Extract Price
    # Strategy 1 (Preferred): Open Graph Description
    # <meta property="og:description" content="Harga Termurah Rp99.475" />
    prices = []
    try:
        og_desc_el = page.locator("meta[property='og:description']").first
        if og_desc_el.count() > 0:
            og_desc = og_desc_el.get_attribute("content")
            if og_desc:
                # Extract number from "Harga Termurah Rp99.475"
                matches = re.findall(r'Rp\s?[\d,.]+', og_desc)
                for m in matches:
                    clean = re.sub(r'[^\d]', '', m)
                    if clean:
                        prices.append(int(clean))
                        logger.debug(f"Found price from og:description: {clean}")

        # Strategy 2: Radio Button 'harga' attribute
        if not prices:
            prdinfo_inputs = page.locator("input.prdinfo")
            if prdinfo_inputs.count() > 0:
                for i in range(prdinfo_inputs.count()):
                    harga_attr = prdinfo_inputs.nth(i).get_attribute("harga")
                    if harga_attr and harga_attr.isdigit():
                        prices.append(int(harga_attr))
        
        # Strategy 3: Fallback to text scan
        if not prices:
            body_text = page.locator("body").text_content()
            found_prices = re.findall(r'Rp\s?[\d.]+', body_text)
            for price_str in found_prices:
                clean_str = re.sub(r'[^\d]', '', price_str)
                if clean_str:
                    val = int(clean_str)
                    if val > 100 and val < 100000000: 
                        prices.append(val)
        
    except Exception as e:
        logger.warning(f"Error extracting prices for {url}: {e}")

    if prices:
        product_data["cheapest_price"] = min(prices)
        product_data["status"] = "success"
        logger.info(f"Found data: {product_data['product_name']} - Rp {product_data['cheapest_price']}")
    else:
        logger.warning(f"No valid price found for {url}")
        if product_data["product_name"]:
             product_data["status"] = "partial"

    # Extract Stock Availability
    # Button ".beli_button" contains a span with either "Stok Habis" or "+ Keranjang"
    try:
        # Check for "Stok Habis" span inside the button
        stok_habis_locator = page.locator(".beli_button span:has-text('Stok Habis')")
        if stok_habis_locator.count() > 0:
            product_data["stock_available"] = False
        else:
            # Check for "+ Keranjang" span to confirm in stock
            keranjang_locator = page.locator(".beli_button span:has-text('+ Keranjang')")
            if keranjang_locator.count() > 0:
                product_data["stock_available"] = True
            else:
                # If neither found, default to None (unknown)
                product_data["stock_available"] = None
    except Exception as e:
        logger.warning(f"Error extracting stock availability for {url}: {e}")
        product_data["stock_available"] = None

    return product_data

def run_scraper_batch(urls, proxy_server=None):
    """Runs a batch of URLs with a specific proxy configuration."""
    results = []
    
    logger.info(f"Starting batch with proxy: {proxy_server if proxy_server else 'Direct Connection'}")

    with sync_playwright() as p:
        user_data_path = Path(USER_DATA_DIR).absolute()
        
        # Args to help evade detection (minimal to avoid conflicts with stealth)
        args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--ignore-certificate-errors",
        ]
        
        proxy_config = {"server": proxy_server} if proxy_server else None

        try:
            # Launch persistent context
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_path,
                headless=False,
                args=args,
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                proxy=proxy_config
            )
        except Exception as e:
            logger.error(f"Failed to launch browser with proxy {proxy_server}: {e}")
            return [], False # Return empty results and failure flag

        # Apply stealth
        page = context.pages[0] if context.pages else context.new_page()
        if Stealth:
            Stealth().apply_stealth_sync(page)
            logger.info("Playwright Stealth applied.")

        success_count = 0
        total_processed_in_session = 0
        for i, url in enumerate(urls):
            logger.info(f"Processing {i+1}/{len(urls)}")
            
            try:
                data = scrape_product(page, url)
                if data:
                    results.append(data)
                    # Save to CSV and JSONL immediately
                    append_to_csv(data)
                    append_to_jsonl(data)
                    
                    if data["status"] == "success":
                        success_count += 1
                total_processed_in_session += 1
            except Exception as e:
                logger.error(f"Fatal error during scraping {url}: {e}")
                # If we hit a fatal error (like network timeout repeated), we might want to rotate proxy
                context.close()
                return results, False # Signal to rotate proxy for remaining URLs

            # Check for blocking (simple heuristic: repeated failures)
            if i > 2 and success_count == 0:
                 logger.warning("High failure rate detected. Possible block.")
                 context.close()
                 return results, False

            # Extended delay for no-proxy safe mode
            human_delay()
            
            # Batch pause: rest every BATCH_SIZE URLs
            if (i + 1) % BATCH_SIZE == 0 and (i + 1) < len(urls):
                pause_time = random.uniform(BATCH_PAUSE_MIN, BATCH_PAUSE_MAX)
                logger.info(f"Batch pause: resting for {pause_time/60:.1f} minutes...")
                time.sleep(pause_time)

        context.close()
        return results, True # Success

def main():
    # Ensure URL file exists
    if not Path(INPUT_FILE).exists():
        logger.error(f"Input file {INPUT_FILE} not found!")
        return

    # Load URL list
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    # Load proxies
    proxies = load_proxies()
    logger.info(f"Loaded {len(proxies)} proxies.")
    
    # Resume logic based on output.csv line count
    start_index = get_processed_count()
    if start_index > 0:
        logger.info(f"Resuming from index {start_index} (based on output.csv count).")
        if start_index >= len(urls):
             logger.info("All URLs already processed according to output.csv. Stopping.")
             return
        urls_to_process = urls[start_index:]
    else:
        urls_to_process = urls


    final_results = []
    
    # Add None to represent "Direct Connection" (use as last resort or first attempt)
    # Strategy: If we have proxies, use them randomly. If none, use direct.
    proxy_pool = proxies if proxies else [None]
    
    # NOTE: urls_to_process is already set by resume logic above!
    
    current_proxy_index = 0
    max_global_retries = 5 # Avoid infinite loops
    retry_count = 0

    while urls_to_process and retry_count < max_global_retries:
        current_proxy = proxy_pool[current_proxy_index % len(proxy_pool)]
        
        # We need to process "urls_to_process"
        # Since run_scraper_batch might fail halfway, we need it to return what it finished
        # Detailed logic:
        # run_scraper_batch should take "urls", verify duplication? No, just run.
        # But we need to know WHICH ones failed.
        # Simplified: If batch fails, we rotate proxy and RETRY THE WHOLE REMAINING BATCH?
        # Yes, potentially. Or we append what succeeded to results.
        
        # Let's modify run_scraper_batch to return (results, completed_flag)
        # But wait, run_scraper_batch iterates internally.
        # If it returns "False", it means it crashed/stopped early.
        # We should probably pass ALL remaining urls to it.
        # And it returns the data it got. We filter out the processed URLs from `urls_to_process`
        
        batch_results, completed_cleanly = run_scraper_batch(urls_to_process, current_proxy)
        
        final_results.extend(batch_results)
        
        # Determine which URLs are done
        processed_urls = {res["url"] for res in batch_results}
        # In this new logic, urls_to_process is just a slice of the main list.
        # But run_scraper_batch returns what it processed.
        # We need to advance our index or slice.
        # Since run_scraper_batch might return partial results if it failed...
        # Wait, run_scraper_batch loops through its input list.
        # If it returns, we assume it finished (or failed and returned distinct results).
        
        # Actually, simpler: just remove processed form urls_to_process
        urls_to_process = [u for u in urls_to_process if u not in processed_urls]
        
        if not urls_to_process:
            break
            
        if not completed_cleanly:
            logger.warning("Batch incomplete or blocked. Rotating proxy...")
            retry_count += 1
            current_proxy_index += 1
            if current_proxy_index >= len(proxy_pool) and len(proxy_pool) > 1:
                logger.info("Cycled through all proxies. Sleeping longer before retry.")
                time.sleep(30)
            
            # Rotate user_data_dir to ensure fresh session for new proxy?
            # Yes, if we suspect block, we should probably clear session or use a new folder.
            # For this implementation, let's clear it.
            try:
                shutil.rmtree(USER_DATA_DIR, ignore_errors=True)
                logger.info("Cleared user_data_dir for new session.")
            except:
                pass
        else:
             # Completed cleanly but maybe some failed individually?
             # For now, assume if completed_cleanly=True, we processed the list.
             # If urls_to_process is empty, we are done.
             pass

    # Delete checkpoint file on successful completion
    if Path(CHECKPOINT_FILE).exists():
        try:
            Path(CHECKPOINT_FILE).unlink()
            logger.info("Checkpoint file removed (scraping complete).")
        except:
            pass

    # Save final output (JSON only, CSV is real-time)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)
    
    logger.info("Scraping completed. Check output.json and output.csv.")

if __name__ == "__main__":
    main()
