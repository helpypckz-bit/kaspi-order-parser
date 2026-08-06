# Kaspi Merchant GraphQL Order Parser

Production-ready Python application for exporting Kaspi Merchant orders through the same internal GraphQL endpoint used by the Merchant SPA. Playwright is used only to authenticate and save browser cookies; order extraction is performed with JSON GraphQL requests, not HTML scraping.

## Features

- Manual one-time Playwright authentication with persisted `storage_state.json`.
- Threaded GraphQL order retrieval with up to five workers by default.
- Retry support with exponential backoff for transient HTTP/network failures.
- Typed dataclass models and isolated services for auth, GraphQL, parsing, Excel, and logging.
- Excel input (`orders.xlsx`) and Excel output (`result.xlsx`).
- Structured file and console logging.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Edit `.env` and set your merchant UID and file paths if needed.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `MERCHANT_UID` | `Applecity` | Kaspi merchant UID passed to GraphQL. |
| `INPUT_FILE` | `orders.xlsx` | Excel file with an `OrderCode` column. |
| `OUTPUT_FILE` | `result.xlsx` | Generated Excel export. |
| `HEADLESS` | `true` | Reserved for browser automation settings. Login is always visible. |
| `MAX_WORKERS` | `5` | Concurrent request workers. |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds. |
| `RETRY_COUNT` | `3` | Configured retry count. |
| `STORAGE_STATE_FILE` | `storage_state.json` | Playwright cookie/session state. |
| `GRAPHQL_QUERY_FILE` | `graphql/get_order_details.graphql` | GraphQL query file. |
| `LOG_FILE` | `logs/parser.log` | Application log file. |

## Authentication

```bash
python auth.py
```

A Chromium window opens at `https://kaspi.kz/mc`. Complete login manually, then return to the terminal and press Enter. The app saves cookies to `storage_state.json`. Passwords, cookies, logs, and generated results are ignored by Git.

## Input

Create `orders.xlsx` with a single required column:

| OrderCode |
| --- |
| 1022135385 |
| 1022135386 |

## Run Parser

```bash
python parser.py
```

The parser reads order codes, executes GraphQL requests concurrently, parses JSON, logs failures, continues processing remaining orders, and writes `result.xlsx`.

## Output Columns

`OrderCode`, `CreationTime`, `Status`, `State`, `CustomerFirstName`, `CustomerLastName`, `Phone`, `Comment`, `City`, `Warehouse`, `WarehouseCity`, `DeliveryMode`, `TotalPrice`, `ProductCount`, `Products`.

## Security Notes

Never commit `.env`, `storage_state.json`, logs, or generated output files. Authentication cookies are loaded from Playwright storage state and attached to `requests` sessions.

### Input troubleshooting

The recommended header is `OrderCode`, but the reader is intentionally tolerant: it also accepts common variants such as `Order Code`, `order_code`, `code`, and one-column workbooks without a header. If multiple columns are present, rename the order-code column to `OrderCode` to avoid ambiguity.

### SSL certificate troubleshooting on Windows

If requests fail with `CERTIFICATE_VERIFY_FAILED`, update dependencies first so `requests` uses the bundled `certifi` CA store. In corporate networks with TLS inspection, export your company/root CA as a PEM file and set `SSL_CA_BUNDLE=C:\path\to\corporate-ca.pem` in `.env`. Keep `VERIFY_SSL=true` for production; `VERIFY_SSL=false` exists only as a last-resort local diagnostic switch.

### HTTP 405 troubleshooting

The client sends POST requests and now tries both the captured `GRAPHQL_ENDPOINT` and `GRAPHQL_FALLBACK_ENDPOINT`. If Kaspi changes the internal route again and you still receive HTTP 405, open Kaspi Merchant DevTools, copy the current `getOrderDetails` GraphQL request URL, and set `GRAPHQL_ENDPOINT` in `.env` to that exact URL.

### Important: page URLs are not API URLs

Use `https://kaspi.kz/mc/#/` and links like `https://kaspi.kz/mc/#/orders/1023997750` only in the browser. Do not put those URLs into `GRAPHQL_ENDPOINT`: URL fragments after `#` are client-side routes and cannot receive POST requests. The parser automatically falls back to the API host `https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getOrderDetails` if a Kaspi page URL is accidentally configured as the GraphQL endpoint.

### GraphQL schema changes

Kaspi can change internal GraphQL field names. The bundled query uses `merchant(id: ...)` and avoids invalid `OrderPlace` subfields that caused validation errors such as `Missing field argument 'id'` and `Unknown field argument 'uid'`. If Kaspi changes the schema again, copy the exact current `getOrderDetails` query from browser DevTools into `graphql/get_order_details.graphql`.
