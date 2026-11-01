# Railway Imprest Automator — Multi-Station Edition

A Streamlit app that generates the two monthly Word documents for a railway station imprest account:

- **Annexure-I** — the master imprest bill (balance summary, allocation details, voucher table, ledger, certification).
- **Annexure-II** — the labour annexure (daily attendance calendar, wage total and payment certificate for each cleaning worker).

You enter the month's bills, worker attendance and station details once. The app fills two generic `.docx` templates and gives you both files to download. Because the station's name, officer and workers are filled in at generate time, **the same two templates work for every station**.

---

## Quick start (Windows)

1. Install **Python 3.10 or later** from python.org. Tick **"Add python.exe to PATH"** during installation.
2. Keep the whole `railway_imprest` folder together.
3. Double-click **`App.bat`**.
   - It checks the folder structure and both templates.
   - It installs missing packages from `requirements.txt`.
   - It starts the app in your browser.

### Manual start (any OS)

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

**Requirements:** `streamlit>=1.32`, `python-docx>=1.1.0`

---

## Folder structure

```
railway_imprest/
├── App.bat                  # Windows launcher with pre-flight checks
├── app.py                   # Entry point: page config, sidebar, tabs, footer
├── config.py                # Months list, template paths, blank-station defaults
├── requirements.txt
├── templates/
│   ├── ANNEXURE_TEMPLATE.docx   # Annexure-I master bill template
│   ├── LABOUR_TEMPLATE.docx     # Annexure-II labour template
│   └── README.txt               # Template rules (anchor text, worker slots)
├── core/
│   ├── dates.py             # Days in month
│   ├── num_to_words.py      # Number → Indian-English words (lakh/thousand)
│   ├── sanitize.py          # HTML-escape helper for user-entered text
│   ├── state.py             # Session-state helpers
│   ├── validation.py        # Template anchor checks and worker-slot counting
│   └── balance_store.py     # settings.ini / balances.ini persistence, month keys
├── docx_engine/
│   ├── xml_helpers.py       # Low-level Word (OOXML) formatting helpers
│   ├── annexure1.py         # generate_annexure_1()
│   └── labour.py            # generate_labour_annexure()
└── ui/
    ├── styles.py            # All CSS, plus small JS fallbacks for dropdowns
    ├── sidebar.py           # Billing period selector and active-period card
    ├── tab_expenses.py      # Tab 1: Consumables
    ├── tab_labour.py        # Tab 2: Labour
    ├── tab_generate.py      # Tab 3: Generate & Download
    └── tab_station.py       # Tab 4: Station Details
```

Two files are created at runtime next to `app.py`:

| File | Purpose |
|---|---|
| `settings.ini` | The active station's details (name, division, officer, ATM no., phone, mobile, sanctioned amount, daily wage, workers) |
| `balances.ini` | Each station's closing balance per month, used to pre-fill next month's opening balance |

---

## How to use

### 1. Station Details tab (first-time setup)

Fill in and save:

- Station name, division / station code (e.g. `SMR/SET`), station manager name, ATM card number, auto phone, mobile.
- Sanctioned amount and daily wage per worker.
- Number of labourers (2–4). For each one, enter the **Name (UPPERCASE)** and the **Full Name with Title** (e.g. `Smt. THAYAMMA`).

Whatever you type here is printed in the documents exactly as entered. Check spelling and spacing, for example `S N VENUPRASAD` and `SMR/SET`.

### 2. Sidebar

Pick the **billing month and year**. The active-period card shows the From/To dates, number of days and the sanctioned amount.

### 3. Consumables tab

- Choose **3 vouchers** (1 consumable bill) or **4 vouchers** (2 bills). For 4 vouchers, Bill 2 can be Consumable or Stationery.
- Enter the amount, date and number of items for each bill.

### 4. Labour tab

- Enter the days worked for each worker. Wages are days × daily wage.
- **Leave days** are assigned automatically from the end of the month, and no two workers share a leave day.
- To match real attendance, tick the **customize** option and pick each worker's exact leave days. The app checks that:
  - the number of days picked matches the leave count implied by days worked, and
  - no two workers share a leave day.

  Generation is blocked until both checks pass. The days you pick are the days printed in the document.

### 5. Generate & Download tab

- **Opening balance** is pre-filled from the previous month's closing balance, if one was stored. You can edit it.
- The page shows the financial summary and the expenditure breakdown.
- Click **Generate All Documents**, then download Annexure-I and the Labour Annexure.
- Generating also stores this month's closing balance, which pre-fills next month's opening balance.

Generation is **blocked** if any of these is true:

- The closing balance is negative (overspent).
- A template file is missing the anchor text it needs (usually a wrong or swapped file).
- The station has more workers than the Labour template has slots for.
- The leave-day selection is invalid.

---

## Templates — read before editing

The app fills templates by **searching for specific text**, not by named placeholders. Keep this text intact if you edit a template.

| Template | Must contain |
|---|---|
| `ANNEXURE_TEMPLATE.docx` | `No. Station Imprest`, `Sub: Recoupment`, `BALANCE AMOUNT ON HAND`, `Certified that the amount paid` |
| `LABOUR_TEMPLATE.docx` | `LABOUR NAME:`, `Payment to Smt`, `Total amount paid` |

- **Keep the file names exactly as shown.** The two files were once supplied with their names swapped, which makes the app generate documents with nothing filled in. The Generate tab now detects this and tells you.
- **The Labour template has 2 worker slots.** Stations with 3 or 4 workers are blocked from generating until the template gets more slots. To add one, duplicate a complete worker block (LABOUR NAME line, calendar table, signature lines, payment certificate) inside the `.docx`.
- **Workers fill the slots by position**, not by name. The first `LABOUR NAME:` block gets the first worker, the second block gets the second worker, and so on.
- The voucher table adapts to 3 or 4 vouchers automatically (the row count is adjusted and the new row is renumbered).

---

## Known limitations

- **One active station at a time.** `settings.ini` holds a single station profile. To switch stations, edit and save Station Details. Closing balances are stored per station, so each station keeps its own history.
- **Labour Annexure supports 2 workers** until the template is extended (see above).
- **Labour Annexure signature-block alignment (open issue).** On the officer name and division lines, the template's original leading-space padding is not yet preserved when text is replaced in `docx_engine/labour.py`, so those lines can sit further left than in the reference document. The fix is to read each paragraph's original leading-space count before overwriting it and re-apply it.
- **Annexure-I disclaimer font size is unconfirmed.** The "Enclosed: 1) To be sent in duplicate…" line is 9 pt in both the template and the reference. Change it only if you confirm you want a different size.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Generated document has none of the station's details | The template files are swapped or missing anchor text. Check the error shown on the Generate tab, and `templates/README.txt`. |
| Officer name or division prints differently from your reference (e.g. `SET` instead of `SMR/SET`) | Station Details contains that text. Correct it there and save. |
| Garbled characters in the `App.bat` window | Fixed in the current `App.bat` (pure ASCII plus `chcp 65001`). If you edit the file, avoid non-ASCII characters. |
| Sidebar looks like plain text | `ui/sidebar.py` and `ui/styles.py` have drifted apart. Every CSS class used in markup must be defined in `styles.py`. |
| Dropdown or multiselect shows a dark or white-on-white box | Check the matching rule in `ui/styles.py`. Each widget type needs its own CSS: `.stSelectbox`, `.stMultiSelect`, `.stTextInput`, and so on. |
| Input box looks cut off at the bottom | The wrapper height rule in `ui/styles.py` (`min-height: 46px; overflow: visible`) is missing. |
| Text cursor not visible in a text box | The `caret-color` rule is missing for that input type in `ui/styles.py`. |
| Tab-indented lines collapse to the left in Word | `make_run()` in `docx_engine/xml_helpers.py` must emit real `<w:tab/>` elements for tab characters. |
| Amounts don't carry into the next month | `balances.ini` is missing or was moved. Closing balances are saved when you generate. |

---

## Where to change what

| To change… | Edit |
|---|---|
| Station form fields | `ui/tab_station.py` |
| Bill / voucher entry | `ui/tab_expenses.py` |
| Attendance and leave-day logic (screen) | `ui/tab_labour.py` |
| Leave-day logic (document) | `docx_engine/labour.py` — keep the two in sync |
| Totals, summary cards, Generate and download buttons | `ui/tab_generate.py` |
| What goes where in Annexure-I | `docx_engine/annexure1.py` |
| What goes where in the Labour Annexure | `docx_engine/labour.py` |
| Fonts, bold and alignment helpers for Word | `docx_engine/xml_helpers.py` |
| Colours, fonts, layout, widget styling | `ui/styles.py` |
| Sidebar | `ui/sidebar.py` |
| Required template text | `core/validation.py` |
| Opening-balance carry-forward and settings storage | `core/balance_store.py` |
| Page title, tab order, header and footer | `app.py` |
| Defaults and template paths | `config.py` |

---

## Developer notes

- **Match the reference documents.** When output differs from a reference `.docx`, compare run-level font size, bold and alignment, not only the text. Most mismatches came from cells that start empty in the template, which have no formatting to inherit, so size, bold and alignment must be set explicitly.
- **Don't assign `paragraph.text` where formatting matters.** It collapses the paragraph into one plain run and loses bold and size. Rebuild the runs with `clear_para_runs()` and `append_run()` instead.
- **Keep the on-screen preview and the document in sync.** The Labour tab shows the leave days, and the document must print exactly those days.
- **Escape user text in HTML.** Anything typed by the user and placed in an `unsafe_allow_html` block goes through `core/sanitize.esc()`. Values passed to the Word engine stay raw.
- **Don't hide the sidebar toggle.** The app uses Streamlit's built-in collapse arrow only. Custom JS that forced inline styles on the sidebar once left it stuck closed.
