---
name: office-doc-engine
description: >-
  Use this skill to create, edit, parse, or convert Microsoft Word (.docx), Excel (.xlsx),
  PowerPoint (.pptx), and PDF documents programmatically without requiring desktop office applications.
  Applies corporate styling, formula calculations, tables, charts, and slide layouts.
---

# Office Document Engine

Enables agents to produce, inspect, and update production-grade business documents, spreadsheets, presentations, and PDF briefs directly from code.

## When to Use This Skill
- When asked to generate reports, executive summaries, or memos as `.docx` or `.pdf`.
- When manipulating datasets into styled spreadsheets (`.xlsx`) with formulas, conditional formatting, and charts.
- When assembling pitch decks, architecture presentations, or training slides as `.pptx`.
- When extracting text, tables, or metadata from locked PDF files.

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

## Anti-Patterns & Traps to Avoid
- **Unstyled Raw Tables & Default Borders**: Generating spreadsheets or tables with raw unformatted gridlines, unstyled headers, and default column widths that clip text values.
- **Hardcoding Calculated Totals in Spreadsheets**: Writing raw sum or average numbers into cells instead of dynamic Excel formulas (`=SUM(C2:C100)`), breaking re-calculation when data is edited.
- **In-Memory Buffer Exhaustion with Giant Datasets**: Using standard openpyxl DOM parsing on multi-hundred-megabyte spreadsheets instead of `write_only=True` streaming mode, causing fatal OOM errors.
- **Hardcoded Operating System Specific Paths**: Using hardcoded Windows backslashes (`C:\temp\`) or Unix `/tmp` instead of `pathlib.Path` or `tempfile.NamedTemporaryFile`, breaking document generation across environments.

## Quality Checklist
- [ ] Tables feature styled header rows with high-contrast fill colors and bold typography.
- [ ] Column widths are auto-calculated with padding to prevent cell truncation or `###` overflow.
- [ ] Computed values utilize native spreadsheet formulas (`SUM`, `AVERAGE`, `VLOOKUP`) rather than static numbers.
- [ ] Presentation slides conform to 16:9 widescreen layout with consistent typography and color palettes.
- [ ] Large workbook exports utilize streaming / write-only modes when data exceeds 10,000 rows.
- [ ] Document generation scripts execute cleanly without deprecation warnings or dangling file descriptors.
