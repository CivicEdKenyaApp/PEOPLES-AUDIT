#!/usr/bin/env python3
"""
Optimized PDF Extraction Script
===============================
Demonstrates how to use the enhanced PDF extractor for maximum accuracy
"""

import sys
import json
import logging
from pathlib import Path
from extractors.pdf_extractor import PDFExtractor

def main():
    """Run optimized extraction"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get PDF path
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "input/THE-PEOPLES-AUDIT_compressed.pdf"
    
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        print("Usage: python extract_optimized.py [path_to_pdf]")
        sys.exit(1)
    
    print("=" * 80)
    print("ENHANCED PDF EXTRACTION")
    print("=" * 80)
    print(f"Source: {pdf_path}")
    print()
    
    # Check for optional dependencies
    print("Checking dependencies...")
    deps_status = {
        'pymupdf': False,
        'ocr': False,
        'camelot': False,
        'tabula': False
    }
    
    try:
        import fitz
        deps_status['pymupdf'] = True
        print("  ✓ PyMuPDF available")
    except ImportError:
        print("  ✗ PyMuPDF not available (install: pip install pymupdf)")
    
    try:
        import pytesseract
        from PIL import Image
        deps_status['ocr'] = True
        print("  ✓ OCR available")
    except ImportError:
        print("  ✗ OCR not available (install: pip install pytesseract Pillow)")
    
    try:
        import camelot
        deps_status['camelot'] = True
        print("  ✓ Camelot available")
    except ImportError:
        print("  ✗ Camelot not available (install: pip install camelot-py[cv])")
    
    try:
        import tabula
        deps_status['tabula'] = True
        print("  ✓ Tabula available")
    except ImportError:
        print("  ✗ Tabula not available (install: pip install tabula-py)")
    
    print()
    
    # Determine if OCR should be enabled
    use_ocr = deps_status['ocr']
    if not use_ocr:
        print("⚠️  OCR not available. Install pytesseract for scanned PDF support.")
        print()
    
    # Create extractor with optimizations
    print("Initializing enhanced extractor...")
    extractor = PDFExtractor(
        log_level=logging.INFO,
        use_ocr=use_ocr,
        ocr_threshold=100  # Trigger OCR if page has < 100 words
    )
    
    print("Starting extraction...")
    print()
    
    try:
        # Extract
        results = extractor.extract_all(str(pdf_path))
        
        # Display results
        print("=" * 80)
        print("EXTRACTION COMPLETE")
        print("=" * 80)
        print()
        
        # Statistics
        stats = results['statistics']
        print("Statistics:")
        print(f"  Total Pages: {stats['total_pages']}")
        print(f"  Total Words: {stats['total_words']:,}")
        print(f"  Total Paragraphs: {stats['total_paragraphs']:,}")
        print(f"  Tables Found: {stats['tables_count']}")
        print(f"  Figures Found: {stats['figures_count']}")
        print(f"  Monetary Values: {len(results['numerics']['monetary_values'])}")
        print(f"  Constitutional Articles: {stats['total_constitutional_articles']}")
        print(f"  Scandals Referenced: {stats['total_scandals']}")
        print()
        
        # Quality metrics
        quality = results['quality_metrics']
        print("Quality Metrics:")
        print(f"  Overall Score: {quality['overall_score']:.2%}")
        print(f"  Average Words/Page: {quality['average_words_per_page']:.0f}")
        print(f"  Pages with Tables: {quality['pages_with_tables']}")
        print(f"  Table Coverage: {quality['table_coverage']:.2%}")
        print(f"  Figure Coverage: {quality['figure_coverage']:.2%}")
        print()
        
        # Check for low-quality pages
        low_quality = [
            (k, v['extraction_quality']['quality_score'])
            for k, v in results['text'].items()
            if v['extraction_quality'].get('quality_score', 1.0) < 0.5
        ]
        
        if low_quality:
            print(f"⚠️  Warning: {len(low_quality)} pages with quality < 50%")
            print("   Consider enabling OCR or checking PDF quality")
            print()
        
        # Save results
        output_dir = Path("stage_1_extract")
        output_dir.mkdir(exist_ok=True)
        
        print("Saving results...")
        
        # Save all extraction results
        with open(output_dir / 'raw_text.json', 'w', encoding='utf-8') as f:
            json.dump(results['text'], f, indent=2, ensure_ascii=False)
        
        with open(output_dir / 'document_structure.json', 'w', encoding='utf-8') as f:
            json.dump(results['structure'], f, indent=2, ensure_ascii=False)
        
        with open(output_dir / 'numeric_facts.json', 'w', encoding='utf-8') as f:
            json.dump(results['numerics'], f, indent=2, ensure_ascii=False)
        
        with open(output_dir / 'references.json', 'w', encoding='utf-8') as f:
            json.dump(results['references'], f, indent=2, ensure_ascii=False)
        
        with open(output_dir / 'extraction_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(results['metadata'], f, indent=2, ensure_ascii=False)
        
        with open(output_dir / 'extraction_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(results['statistics'], f, indent=2, ensure_ascii=False)
        
        with open(output_dir / 'quality_metrics.json', 'w', encoding='utf-8') as f:
            json.dump(results['quality_metrics'], f, indent=2, ensure_ascii=False)
        
        print(f"✓ Results saved to {output_dir}/")
        print()
        
        # Sample monetary values
        if results['numerics']['monetary_values']:
            print("Sample Monetary Values (first 5):")
            for val in results['numerics']['monetary_values'][:5]:
                amount = val['amount']
                if amount >= 1e12:
                    display = f"{amount/1e12:.2f} trillion"
                elif amount >= 1e9:
                    display = f"{amount/1e9:.2f} billion"
                elif amount >= 1e6:
                    display = f"{amount/1e6:.2f} million"
                else:
                    display = f"{amount:,.0f}"
                print(f"  {val['currency']} {display} (Page {val['page']})")
            print()
        
        print("=" * 80)
        print("Extraction complete! Check stage_1_extract/ for all results.")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

