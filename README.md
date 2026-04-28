# HomeLogic — The Independent Owner's Renovation Framework

> *"The homeowner who knows the right questions is more powerful than the contractor who knows all the answers."*

---

## Philosophy: The Independent Owner

Most homeowners walk into a renovation blind. They rely entirely on contractors and salespeople who have conflicting incentives. **HomeLogic** changes that dynamic.

This project is built on a single principle: **information is leverage**. By capturing product data systematically, asking the right questions before signing anything, and logging every contractor conversation, you transform yourself from a passive client into an informed decision-maker.

HomeLogic is a **local-first, GitHub-compatible** toolkit. Your data stays on your machine. Your decisions stay in your repo. Nothing is uploaded to a third-party service unless you choose to.

---

## What's Inside

```
HomeLogicAI/
├── capture.py               # CLI scraper: capture product data from any URL
├── compare/
│   └── compare.py           # Generate comparison tables from vault subfolders
├── decisions/               # "What You Don't Know" decision templates
│   ├── ceiling_fans.md
│   ├── kitchen_hardware.md
│   ├── cabinet_storage.md
│   └── lighting.md
├── vault/                   # Scraped product data, organized by category
│   ├── fans/
│   ├── lighting/
│   ├── hardware/
│   ├── flooring/
│   └── cabinet_storage/
├── logs/
│   └── contractor_conversations.md   # Timestamped accountability ledger
├── standards.json           # Defines "good" benchmarks per category
├── config.yaml              # Customize your renovation zones
└── requirements.txt
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Capture a product

```bash
python capture.py --url "https://www.example.com/product-page" --category fans
```

This will:
- Scrape the page for Title, Price, Dimensions, Material, and Key Attributes
- Save the result as a JSON file in `vault/fans/`
- Download a product image alongside the JSON

### 3. Compare products in a category

```bash
python compare/compare.py --folder vault/fans
```

Generates a Markdown comparison table (and optional CSV) from all JSON files in the folder.

### 4. Review a decision template

Open any file in `decisions/` before you speak to a supplier or contractor. These templates tell you:
- **What to Ask** — questions most homeowners never think to raise
- **Critical Attributes** — the specs that actually matter
- **Hidden Costs / Technical Blind Spots** — the surprises that blow budgets

### 5. Log a contractor conversation

Open `logs/contractor_conversations.md` and add a dated entry any time a contractor makes a claim, promise, or excuse. This creates a paper trail.

---

## CLI Reference

| Command | Description |
|---|---|
| `python capture.py --url URL --category CATEGORY` | Scrape a product URL and save to vault |
| `python capture.py --url URL --category CATEGORY --name "My Item"` | Override the auto-detected product name |
| `python compare/compare.py --folder vault/CATEGORY` | Generate comparison table for a category |
| `python compare/compare.py --folder vault/CATEGORY --format csv` | Output as CSV instead of Markdown |

### Supported categories

`fans` · `lighting` · `hardware` · `flooring` · `cabinet_storage`

You can add custom categories by editing `config.yaml`.

---

## Configuration (`config.yaml`)

Edit `config.yaml` to reflect your actual renovation zones and preferences:

```yaml
renovation_zones:
  - Kitchen
  - Master Bath
  - Guest Room
```

---

## The "Experience Log" (Contractor Conversations)

Every time a contractor says something important — a promise, a limitation, a price — log it in `logs/contractor_conversations.md`. The format is simple:

```markdown
## 2024-03-15 — John (ABC Electrical)
- Said panel upgrade is NOT needed for ceiling fan circuit
- Quoted $350 for fan installation (2 fans)
- Warned: permit required if we add a new circuit
```

This single habit has saved homeowners thousands of dollars by creating an accountable record.

---

## Standards (`standards.json`)

The `standards.json` file defines what "good" looks like for each category. Use it as a reference when evaluating products:

- **Fans**: DC motor preferred, CFM ≥ 5000 for rooms > 200 sq ft, blade pitch 12–15°, noise < 40 dB
- **Lighting**: CRI ≥ 90 for kitchens/bathrooms, color temp 2700–3000K for living spaces
- **Hardware**: Solid brass or stainless steel for high-use areas, lifetime finish warranty preferred

---

## Extending the Project

HomeLogic is designed for developers to extend:

- **New scraper targets**: Add a new parser function in `capture.py`
- **New decision templates**: Copy any file in `decisions/` and adapt
- **New vault categories**: Create a new subfolder in `vault/` and add to `config.yaml`
- **New comparison columns**: Edit the `COLUMNS` list in `compare/compare.py`

---

## License

MIT — use it, fork it, make it yours.
