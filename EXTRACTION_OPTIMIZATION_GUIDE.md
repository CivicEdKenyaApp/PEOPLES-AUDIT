# PDF Extraction Optimization Guide

## Overview
This guide explains how to maximize accuracy and detail from the PDF extraction process for the People's Audit pipeline.

## Enhanced Features

### 1. Multiple Extraction Methods
The enhanced extractor uses multiple libraries to get the best results:
- **PyPDF2**: Basic text extraction
- **pdfplumber**: Best for text-based PDFs (primary method)
- **PyMuPDF (pymupdf)**: Excellent for complex layouts and images
- **OCR (pytesseract)**: Fallback for scanned PDFs or poor quality pages

### 2. Enhanced Table Extraction
Tables are extracted using three methods:
- **pdfplumber**: Primary method, good for most tables
- **Camelot**: Excellent for structured tables with clear borders
- **Tabula**: Good for simple tables

The extractor automatically selects the best result.

### 3. Quality Metrics
Each page gets a quality score (0-1) based on:
- Text length and word count
- Paragraph structure
- Presence of tables and figures
- Overall extraction completeness

## Installation Requirements

### Basic Installation
```bash
pip install -r requirements.txt
```

### Enhanced Features (Optional but Recommended)

#### For OCR Support:
```bash
# Windows
# Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# Then:
pip install pytesseract Pillow

# Linux
sudo apt-get install tesseract-ocr
pip install pytesseract Pillow

# macOS
brew install tesseract
pip install pytesseract Pillow
```

#### For Advanced Table Extraction:
```bash
# Camelot requires additional dependencies
# Windows: Install Ghostscript from https://www.ghostscript.com/download/gsdnld.html
# Linux: sudo apt-get install ghostscript python3-tk
# macOS: brew install ghostscript

pip install camelot-py[cv]
pip install tabula-py
```

## Usage

### Basic Usage (Current)
```python
from extractors.pdf_extractor import PDFExtractor

extractor = PDFExtractor()
results = extractor.extract_all("input/THE-PEOPLES-AUDIT_compressed.pdf")
```

### Enhanced Usage with OCR
```python
from extractors.pdf_extractor import PDFExtractor

# Enable OCR for pages with low text quality
extractor = PDFExtractor(use_ocr=True, ocr_threshold=100)
results = extractor.extract_all("input/THE-PEOPLES-AUDIT_compressed.pdf")
```

### Check Extraction Quality
```python
# After extraction, check quality metrics
quality = results['quality_metrics']
print(f"Overall Quality Score: {quality['overall_score']:.2%}")
print(f"Average Words per Page: {quality['average_words_per_page']:.0f}")
print(f"Table Coverage: {quality['table_coverage']:.2%}")
```

## Optimization Tips

### 1. For Maximum Text Accuracy
- Ensure `pdfplumber` is installed (already in requirements)
- Install `pymupdf` for better complex layout handling
- Use OCR if the PDF appears to be scanned or has poor text quality

### 2. For Maximum Table Accuracy
- Install both `camelot-py` and `tabula-py`
- The extractor will automatically try all methods and select the best
- Check the `method` field in table data to see which method worked best

### 3. For Maximum Detail Extraction
The enhanced extractor now extracts:
- **Monetary values**: With better pattern matching (KSh, USD, billion, million, trillion)
- **Constitutional articles**: Enhanced patterns (Article, Art., Art)
- **Institutional references**: Expanded list of institutions
- **Citations**: Better pattern matching
- **Images**: Extracted metadata from PDF pages
- **Quality metrics**: Per-page and overall quality scores

### 4. Pre-processing PDF (Optional)
If your PDF has issues:
1. **Repair PDF**: Use tools like `qpdf` or Adobe Acrobat to repair corrupted PDFs
2. **Optimize PDF**: Reduce file size while maintaining quality
3. **Convert to text-based PDF**: If scanned, use OCR tools to create text-based version

```bash
# Using qpdf to repair
qpdf --check input/THE-PEOPLES-AUDIT_compressed.pdf

# Using pdftk to repair (if available)
pdftk input/THE-PEOPLES-AUDIT_compressed.pdf output repaired.pdf
```

## Configuration Options

### PDFExtractor Parameters

```python
PDFExtractor(
    log_level=logging.INFO,      # Logging level (DEBUG, INFO, WARNING, ERROR)
    use_ocr=False,               # Enable OCR fallback
    ocr_threshold=100            # Minimum word count to trigger OCR
)
```

### When to Enable OCR
- PDF appears to be scanned
- Text extraction yields very few words per page (< 100)
- Quality score is consistently low (< 0.3)
- Tables are not being extracted properly

### OCR Configuration
If using OCR, you may need to configure Tesseract path:

```python
import pytesseract

# Windows example
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Or set environment variable
# TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

## Quality Checks

### After Extraction, Verify:

1. **Text Quality**
   ```python
   for page_key, page_data in results['text'].items():
       quality = page_data['extraction_quality']
       if quality['quality_score'] < 0.3:
           print(f"Low quality page: {page_key}")
   ```

2. **Table Extraction**
   ```python
   total_tables = sum(len(p.get('tables', [])) for p in results['text'].values())
   print(f"Total tables extracted: {total_tables}")
   ```

3. **Monetary Values**
   ```python
   total_monetary = sum(len(p.get('monetary_values', [])) for p in results['text'].values())
   print(f"Total monetary values found: {total_monetary}")
   ```

## Troubleshooting

### Issue: Low Text Extraction
**Solutions:**
1. Enable OCR: `extractor = PDFExtractor(use_ocr=True)`
2. Check if PDF is text-based or scanned
3. Try repairing the PDF
4. Check if PDF is password-protected

### Issue: Tables Not Extracted
**Solutions:**
1. Install camelot-py: `pip install camelot-py[cv]`
2. Install tabula-py: `pip install tabula-py`
3. Check table quality in PDF (may need manual extraction for complex tables)
4. Review table extraction logs for errors

### Issue: Missing Monetary Values
**Solutions:**
1. Check if values use different formats (e.g., "12.05 trillion" vs "12.05T")
2. Review extraction patterns in `pdf_extractor.py`
3. Check context around values in extracted text
4. Manually verify a few pages

### Issue: Poor Quality Scores
**Solutions:**
1. Enable OCR if pages have low word counts
2. Check PDF quality (may be corrupted or scanned)
3. Verify extraction methods are working (check logs)
4. Consider pre-processing the PDF

## Best Practices

1. **Always check quality metrics** after extraction
2. **Review sample pages** to verify accuracy
3. **Enable OCR** if working with scanned documents
4. **Install all optional dependencies** for maximum accuracy
5. **Check logs** for warnings or errors
6. **Validate extracted data** against source PDF manually for critical pages

## Performance Considerations

- **OCR is slow**: Only enable if necessary
- **Multiple extraction methods**: Adds processing time but improves accuracy
- **Table extraction**: Camelot and Tabula can be slow for large PDFs
- **Memory usage**: Large PDFs may require more memory

## Example: Full Optimization Setup

```python
import logging
from extractors.pdf_extractor import PDFExtractor

# Configure logging for detailed output
logging.basicConfig(level=logging.INFO)

# Create extractor with all optimizations
extractor = PDFExtractor(
    log_level=logging.INFO,
    use_ocr=True,           # Enable OCR for poor quality pages
    ocr_threshold=50        # Lower threshold for OCR
)

# Extract with full detail
results = extractor.extract_all("input/THE-PEOPLES-AUDIT_compressed.pdf")

# Check quality
quality = results['quality_metrics']
print(f"\nExtraction Quality Report:")
print(f"  Overall Score: {quality['overall_score']:.2%}")
print(f"  Average Words/Page: {quality['average_words_per_page']:.0f}")
print(f"  Pages with Tables: {quality['pages_with_tables']}")
print(f"  Table Coverage: {quality['table_coverage']:.2%}")

# Review low-quality pages
low_quality_pages = [
    (k, v['extraction_quality']['quality_score'])
    for k, v in results['text'].items()
    if v['extraction_quality']['quality_score'] < 0.5
]

if low_quality_pages:
    print(f"\n⚠️  {len(low_quality_pages)} pages with quality < 50%:")
    for page, score in low_quality_pages[:5]:  # Show first 5
        print(f"  {page}: {score:.2%}")
```

## Next Steps

After extraction, the pipeline continues with:
1. **Semantic Tagging** (Stage 2)
2. **Data Consolidation** (Stage 3)
3. **Constitutional Validation** (Stage 4)
4. **Text Generation** (Stage 5)
5. **Visualization** (Stage 6)

Each stage benefits from high-quality extraction, so investing in extraction quality pays off throughout the pipeline.

