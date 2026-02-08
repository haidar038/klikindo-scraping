# ✅ PRD Revisi (Enhanced Cloudflare-Safe Handling)

## Product Requirements Document (PRD)

### Project Name

KlikIndogrosir Product Data Scraper

---

## 1. Background

KlikIndogrosir adalah platform retail grosir online yang dilindungi sistem anti-bot (Cloudflare). User membutuhkan sistem scraping untuk mengambil data produk dari daftar URL tertentu untuk keperluan internal seperti monitoring harga dan katalog produk.

---

## 2. Objectives

Membangun sistem scraping otomatis yang dapat:

- Mengambil nama produk
- Mengambil harga termurah dari varian produk
- Memproses batch URL dari file input
- Menghasilkan output terstruktur (JSON/CSV)
- Meminimalkan deteksi bot dan challenge Cloudflare secara aman

---

## 3. Scope

### In Scope

- Scraping halaman `product_details`
- Extract:
    - Product Name
    - Cheapest Variant Price

- Batch processing URL dari file `.txt`
- Output ke JSON/CSV
- Penanganan anti-bot berbasis stealth + behavioral simulation

### Out of Scope

- Crawling seluruh katalog tanpa URL input
- Bypass captcha secara ilegal atau brute-force
- Exploit Cloudflare challenge secara otomatis penuh

---

## 4. User Stories

### US-1

Sebagai user, saya ingin memasukkan daftar URL produk agar scraper memproses otomatis.

### US-2

Sebagai user, saya ingin mendapatkan nama produk dan harga termurah dari setiap produk.

### US-3

Sebagai user, saya ingin output data dalam JSON/CSV agar mudah digunakan ulang.

### US-4

Sebagai user, saya ingin scraper berjalan stabil tanpa memicu Cloudflare block/challenge terlalu cepat.

---

## 5. Functional Requirements

| Feature                            | Priority |
| ---------------------------------- | -------- |
| Load URL dari file txt             | High     |
| Scrape nama produk                 | High     |
| Scrape harga termurah              | High     |
| Export JSON/CSV                    | High     |
| Error logging per URL              | Medium   |
| Retry jika gagal                   | Medium   |
| Cloudflare-safe session reuse      | High     |
| Stealth mode fingerprint reduction | High     |
| Human-like browsing simulation     | High     |
| Captcha fallback manual pause      | Medium   |

---

## 6. Non-Functional Requirements

- Scraper stabil untuk ≥1000 URL dengan pacing aman
- Tidak overload server target
- Modular dan mudah di-maintain
- Tidak melakukan bypass ilegal terhadap sistem keamanan

---

# 7. Anti-Bot Handling Strategy (Revised)

Karena target menggunakan **Cloudflare Turnstile / Bot Protection**, scraper harus memakai kombinasi strategi defensif berikut:

---

## Level A: Stealth Fingerprint Reduction (Opsi 2)

Scraper harus mengurangi bot fingerprint dengan:

- Menggunakan Playwright Stealth Plugin
- Menghindari headless mode
- Menyamarkan browser environment agar menyerupai user asli

### Requirements

- Implementasi `playwright-stealth`
- Disable automation flags
- Realistic browser headers

---

## Level B: Human-like Browsing Behavior (Opsi 3)

Cloudflare sangat sensitif terhadap pola mesin. Maka scraper wajib mensimulasikan perilaku manusia:

- Random delay lebih panjang (8–15 detik)
- Scroll ringan sebelum extract data
- Tidak membuka URL terlalu cepat berurutan

### Requirements

- Delay randomized per request
- Scroll simulation per page load
- Rate limiting internal

---

## Level C: Session Reuse + Single Tab Navigation (Opsi 4)

Cloudflare lebih mudah memblokir jika session terlihat seperti bot yang “teleporting”.

Maka scraper harus:

- Reuse browser context yang sama
- Menggunakan tab/page yang sama untuk semua URL
- Menyimpan cookies agar session terlihat konsisten

### Requirements

- Persistent context directory (`user_data_dir`)
- Tidak membuat browser baru per URL
- Semua scraping dilakukan dalam satu session

---

## Combined Expected Outcome

Dengan kombinasi ini, scraper akan:

✅ Lebih tahan terhadap Cloudflare challenge
✅ Tidak memicu captcha setelah URL pertama
✅ Lebih stabil untuk scraping batch kecil–menengah
❌ Tetap tidak menjamin bebas captcha untuk scraping agresif skala besar

---

# 8. Complete Roadmap (100%)

## Phase 1 — MVP

- URL input
- Extract nama + harga termurah
- Output JSON

## Phase 2 — Reliable Cloudflare-Safe Scraper

- Stealth plugin integration
- Human delay + scrolling behavior
- Session reuse + persistent cookies
- Retry + backoff

## Phase 3 — Scalable System

- Queue system
- Proxy rotation (opsional)
- Database storage (SQLite)

## Phase 4 — Production Deployment

- Scheduler automation (cron/Celery)
- Docker packaging
- Monitoring dashboard + logs

---

## 9. Tech Stack Recommendation

| Component          | Tech                 |
| ------------------ | -------------------- |
| Scraper Engine     | Playwright + Stealth |
| Language           | Python               |
| Output             | JSON / CSV           |
| Storage (Phase 3+) | SQLite               |
