---
name: office-doc-engine
description: Use this skill when programmatically creating, editing, parsing, or converting
  Word (.docx), Excel (.xlsx), PowerPoint (.pptx), and PDF documents.
---

# Office Document Engine

## Overview

Programmatically creates, edits, parses, and converts Microsoft Word (.docx), Excel (.xlsx), PowerPoint (.pptx), and PDF documents using Python libraries (python-docx, openpyxl, python-pptx, PyPDF2) without requiring desktop Office installations.

## When to Use

- When asked to generate reports, executive summaries, or memos as `.docx` or `.pdf`.
- When manipulating datasets into styled spreadsheets (`.xlsx`) with formulas, conditional formatting, and charts.
- When assembling pitch decks, architecture presentations, or training slides as `.pptx`.
- When extracting text, tables, or metadata from locked PDF files.
- **When NOT to use**: Authoring markdown documentation for code repositories (use `technical-writer-scribe` or `workspace-researcher`).

## Core Process & Document Generation Workflows

## Core Tooling & Libraries

| Format | Recommended Engine | Common Packages |
|---|---|---|
| **Word (.docx)** | Python / Node.js | `python-docx` (Python), `docx` (Node.js) |
| **Excel (.xlsx)** | Python | `openpyxl`, `pandas`, `xlsxwriter` |
| **PowerPoint (.pptx)** | Python | `python-pptx` |
| **PDF (.pdf)** | Python / CLI | `pypdf`, `pdfplumber` (text/tables), `weasyprint` (HTML to PDF) |

## Step-by-Step Execution Workflow

### 1. Document Planning & Layout Design
- **Word / PDF**: Define typographic hierarchy (H1, H2, H3), margins (1 inch standard), palette (neutral dark text, corporate accent), and header/footer metadata.
- **Excel**: Define sheet structure, column headers, number formatting (currency `$#,##0.00`, percentages `0.0%`), and freeze panes on row 1.
- **PowerPoint**: Select 16:9 widescreen layout, slide title anchor, 2-column or card-based layout, and high-contrast color scheme.

### 2. Implementation via Scripting

#### Python Script Pattern (Word .docx):
```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor

doc = Document()
# Set standard margins
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

title = doc.add_heading("Executive Project Summary", level=0)
p = doc.add_paragraph("Generated automatically via Agent Office Engine.")
doc.save("output/Executive_Summary.docx")
```

#### Python Script Pattern (Excel .xlsx with Formulas):
```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Financial Summary"

# Headers & Styling
headers = ["Quarter", "Revenue", "Expenses", "Net Margin"]
ws.append(headers)

header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

# Data
rows = [["Q1", 120000, 85000], ["Q2", 145000, 92000], ["Q3", 160000, 99000]]
for row in rows:
    ws.append(row)

# Add formula for Margin
for r in range(2, 5):
    ws[f"D{r}"] = f"=B{r}-C{r}"

wb.save("output/Financial_Model.xlsx")
```

### 3. Execution & Verification
1. Run the generation script using `run_command` in a designated scratch or output directory.
2. Verify output existence, file size (> 0 bytes), and validate using inspection tools (e.g. read back generated rows or verify PDF text extraction).

## Quality & Formatting Rules
- **Never output raw unstyled tables**: Always style headers with distinct background fills and bold white or dark contrast text.
- **Never hardcode calculated totals in Excel**: Always inject formulas (`SUM`, `AVERAGE`, `VLOOKUP`) so workbooks remain dynamic.
- **Always adhere to 16:9 aspect ratio** for modern presentations.
- **PDF Generation**: Prefer rendering cleanly styled HTML/CSS to PDF via headless browser or `weasyprint` for pixel-perfect typography.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"We can use hardcoded cell coordinates instead of dynamic formula ranges."* | Hardcoded cell ranges break when new rows or categories are inserted; named ranges or dynamic formula offsets are essential. |
| *"CSV is fine; the user can format it into Excel themselves."* | Users expect styled workbooks with freeze panes, currency formatting, auto-filtered headers, and pre-calculated formulas. |
| *"PowerPoint text boxes don't need explicit coordinate bounding boxes."* | Unconstrained shapes overlap across slides and render illegibly on different screen aspect ratios. |
| *"Extracting PDF text with simple regex is always reliable."* | PDFs have complex multi-column layouts, font encodings, and table boundaries that require layout-aware parsers. |

## Red Flags

- Generating spreadsheets with raw numbers where dynamic formulas (`SUM`, `AVERAGE`, `VLOOKUP`) should be used.
- Unstyled raw white Word documents lacking standardized corporate typography, headers, and margins.
- Hardcoding Windows drive paths (`C:\temp\`) instead of cross-platform temporary directories.
- Failing to close file handles before attempting file move or conversion operations.

## Verification

After completing the workflow, confirm:
- [ ] Generated spreadsheets include styled headers, formatted numbers (currency, percentages), and verified formulas.
- [ ] Word documents use semantic paragraph styles (Heading 1, Heading 2, Body) and proper page breaks.
- [ ] Presentations conform to 16:9 widescreen dimensions with non-overlapping visual hierarchy.
- [ ] Document generation runs headless in Linux/Windows CI/CD pipelines without MS Office dependencies.
