import PyPDF2
import pdfplumber
import re
import json
from typing import Dict, List, Any, Optional
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import os

# Optional imports for enhanced extraction
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

try:
    import pytesseract
    from PIL import Image
    import io
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    camelot = None

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    tabula = None

@dataclass
class PageData:
    """Data structure for extracted PDF page content"""
    page_number: int
    text: str
    paragraphs: List[str]
    figures: List[Dict]
    tables: List[Dict]
    monetary_values: List[Dict]
    percentages: List[Dict]
    years: List[int]
    constitutional_articles: List[str]
    legal_references: List[str]
    institutional_references: List[str]
    citations: List[str]
    scandals: List[Dict]
    keywords: List[str]
    page_stats: Dict[str, Any]
    extraction_quality: Dict[str, Any]  # Quality metrics
    images: List[Dict]  # Extracted images/figures

class PDFExtractor:
    """Enhanced PDF extractor with multiple extraction methods and OCR fallback"""
    
    def __init__(self, log_level=logging.INFO, use_ocr=False, ocr_threshold=100):
        """
        Initialize enhanced PDF extractor
        
        Args:
            log_level: Logging level
            use_ocr: Enable OCR for pages with low text quality
            ocr_threshold: Minimum word count to trigger OCR (default: 100)
        """
        self.setup_logging(log_level)
        self.use_ocr = use_ocr and OCR_AVAILABLE
        self.ocr_threshold = ocr_threshold
        
        # Enhanced regex patterns for extraction
        self.patterns = {
            'monetary': [
                # KSh patterns
                r'KSh\s*([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion|B|M|T|bn|mn|tn)?',
                r'([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion|B|M|T|bn|mn|tn)\s*(?:shillings|KSh|KES)',
                r'KES\s*([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion|B|M|T)?',
                # USD patterns
                r'\$([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion|B|M|T)?',
                r'USD\s*([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion|B|M|T)?',
                # Generic large numbers that might be monetary
                r'([\d,]{7,})\s*(?:shillings|KSh|KES)',
            ],
            'article': [
                r'Article\s*(\d+(?:[a-z])?(?:\(\d+[a-z]?\))?)',
                r'Art\.\s*(\d+(?:[a-z])?)',
                r'Art\s+(\d+(?:[a-z])?)',
            ],
            'year': r'\b(?:19|20)\d{2}\b',
            'percentage': r'(\d+(?:\.\d+)?)\s*%',
            'figure': [
                r'Figure\s*(\d+(?:\.\d+)?)[:\s]+(.+?)(?=Figure\s*\d+|$)',
                r'Fig\.\s*(\d+(?:\.\d+)?)[:\s]+(.+?)',
                r'FIG\.\s*(\d+(?:\.\d+)?)[:\s]+(.+?)',
            ],
            'table': [
                r'Table\s*(\d+(?:\.\d+)?)[:\s]+(.+?)(?=Table\s*\d+|$)',
                r'Tbl\.\s*(\d+(?:\.\d+)?)[:\s]+(.+?)',
            ],
            'date': [
                r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            ]
        }
        
        # Enhanced institutional references patterns
        self.institutional_patterns = [
            r'\bEACC\b',
            r'\bODPP\b',
            r'\bDPP\b',
            r'\bDCI\b',
            r'\bOAG\b',
            r'\bCoB\b',
            r'\bKNBS\b',
            r'\bNational Treasury\b',
            r'\bTreasury\b',
            r'\bCentral Bank\b',
            r'\bCBK\b',
            r'\bIMF\b',
            r'\bWorld Bank\b',
            r'\bWB\b',
            r'\bParliament\b',
            r'\bSenate\b',
            r'\bCounty Government\b',
            r'\bPublic Service Commission\b',
            r'\bPSC\b',
            r'\bIEBC\b',
            r'\bJSC\b',
            r'\bEACC\b',
            r'\bFRA\b',
            r'\bPPRA\b',
            r'\bNHIF\b',
            r'\bKIPPRA\b',
        ]
    
    def setup_logging(self, log_level):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
    
    def extract_all(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all data from PDF document with enhanced methods"""
        self.logger.info(f"Starting enhanced extraction of {pdf_path}")
        
        extraction_results = {
            'metadata': {},
            'text': {},
            'structure': {},
            'numerics': {},
            'references': {},
            'statistics': {},
            'quality_metrics': {}
        }
        
        try:
            # Calculate file hash for versioning
            file_hash = self._calculate_file_hash(pdf_path)
            
            # Extract with PyPDF2 for basic metadata
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                extraction_results['metadata'].update({
                    'source_file': pdf_path,
                    'total_pages': num_pages,
                    'extraction_date': datetime.now().isoformat(),
                    'file_hash': file_hash,
                    'file_size': os.path.getsize(pdf_path),
                    'extraction_methods': {
                        'pypdf2': True,
                        'pdfplumber': True,
                        'pymupdf': PYMUPDF_AVAILABLE,
                        'ocr': self.use_ocr,
                        'camelot': CAMELOT_AVAILABLE,
                        'tabula': TABULA_AVAILABLE
                    }
                })
                
                # Extract with multiple methods
                with pdfplumber.open(pdf_path) as pdf:
                    # Also try PyMuPDF if available
                    pymupdf_doc = None
                    if PYMUPDF_AVAILABLE:
                        try:
                            pymupdf_doc = fitz.open(pdf_path)
                        except Exception as e:
                            self.logger.warning(f"PyMuPDF not available: {e}")
                    
                    for page_num in range(num_pages):
                        try:
                            self.logger.info(f"Processing page {page_num + 1}/{num_pages}")
                            
                            # Get page from multiple libraries
                            pdf2_page = pdf_reader.pages[page_num]
                            pdfplumber_page = pdf.pages[page_num]
                            pymupdf_page = pymupdf_doc[page_num] if pymupdf_doc else None
                            
                            # Extract text with multiple methods and select best
                            page_text, extraction_method = self._extract_text_multiple_methods(
                                pdf2_page, pdfplumber_page, pymupdf_page, page_num + 1
                            )
                            
                            # Process page with enhanced extraction
                            page_data = self._process_page(
                                page_num + 1, page_text, pdfplumber_page, pymupdf_page, pdf_path
                            )
                            
                            # Store extraction method used
                            page_data.extraction_quality['method_used'] = extraction_method
                            
                            # Store results
                            page_key = f"page_{page_num + 1:03d}"
                            extraction_results['text'][page_key] = asdict(page_data)
                            
                            # Update aggregated data
                            self._update_structure(extraction_results['structure'], page_data, page_num + 1)
                            self._update_numerics(extraction_results['numerics'], page_data)
                            self._update_references(extraction_results['references'], page_data)
                            
                        except Exception as e:
                            self.logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                            continue
                    
                    if pymupdf_doc:
                        pymupdf_doc.close()
            
            # Post-processing
            extraction_results['structure']['chapters'] = self._extract_chapters(extraction_results['text'])
            extraction_results['statistics'] = self._generate_statistics(extraction_results)
            extraction_results['quality_metrics'] = self._calculate_quality_metrics(extraction_results)
            
            self.logger.info(f"Enhanced PDF extraction completed: {num_pages} pages processed")
            self.logger.info(f"Quality score: {extraction_results['quality_metrics'].get('overall_score', 'N/A')}")
            
            return extraction_results
            
        except Exception as e:
            self.logger.error(f"Fatal error extracting PDF: {str(e)}")
            raise
    
    def _extract_text_multiple_methods(self, pdf2_page, pdfplumber_page, pymupdf_page, page_num) -> tuple:
        """Extract text using multiple methods and return the best result"""
        texts = {}
        methods = {}
        
        # Method 1: PyPDF2
        try:
            text_pdf2 = self._safe_extract_text(pdf2_page)
            if text_pdf2:
                texts['pypdf2'] = text_pdf2
                methods['pypdf2'] = len(text_pdf2.split())
        except Exception as e:
            self.logger.debug(f"PyPDF2 extraction failed for page {page_num}: {e}")
        
        # Method 2: pdfplumber (usually best for text-based PDFs)
        try:
            text_pdfplumber = pdfplumber_page.extract_text()
            if text_pdfplumber:
                texts['pdfplumber'] = text_pdfplumber
                methods['pdfplumber'] = len(text_pdfplumber.split())
        except Exception as e:
            self.logger.debug(f"pdfplumber extraction failed for page {page_num}: {e}")
        
        # Method 3: PyMuPDF (often best for complex layouts)
        if pymupdf_page:
            try:
                text_pymupdf = pymupdf_page.get_text()
                if text_pymupdf:
                    texts['pymupdf'] = text_pymupdf
                    methods['pymupdf'] = len(text_pymupdf.split())
            except Exception as e:
                self.logger.debug(f"PyMuPDF extraction failed for page {page_num}: {e}")
        
        # Select best method (longest text, but prefer pdfplumber for quality)
        if not texts:
            # If no text extracted, try OCR if enabled
            if self.use_ocr:
                self.logger.warning(f"No text extracted from page {page_num}, attempting OCR...")
                ocr_text = self._extract_with_ocr(pymupdf_page if pymupdf_page else pdfplumber_page, page_num)
                if ocr_text:
                    return ocr_text, 'ocr'
            return "", "none"
        
        # Prefer pdfplumber if it has reasonable content (>80% of longest)
        if 'pdfplumber' in texts:
            max_words = max(methods.values()) if methods else 0
            if methods.get('pdfplumber', 0) >= max_words * 0.8:
                return texts['pdfplumber'], 'pdfplumber'
        
        # Otherwise use the longest extraction
        best_method = max(methods.items(), key=lambda x: x[1])[0] if methods else 'pypdf2'
        return texts.get(best_method, ""), best_method
    
    def _extract_with_ocr(self, page, page_num: int) -> str:
        """Extract text using OCR as fallback"""
        if not OCR_AVAILABLE:
            return ""
        
        try:
            # Convert page to image
            if hasattr(page, 'get_pixmap'):  # PyMuPDF
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
            elif hasattr(page, 'to_image'):  # pdfplumber
                img = page.to_image(resolution=300)
                img_data = img.original
            else:
                return ""
            
            # Perform OCR
            image = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(image, lang='eng')
            
            self.logger.info(f"OCR extracted {len(text.split())} words from page {page_num}")
            return text
            
        except Exception as e:
            self.logger.warning(f"OCR failed for page {page_num}: {e}")
            return ""
    
    def _process_page(self, page_num: int, text: str, pdfplumber_page, pymupdf_page, pdf_path: str) -> PageData:
        """Process a single page and extract structured data with enhanced methods"""
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Check if we need OCR (low quality text)
            if self.use_ocr and len(cleaned_text.split()) < self.ocr_threshold:
                self.logger.info(f"Low text quality on page {page_num}, attempting OCR...")
                ocr_text = self._extract_with_ocr(pymupdf_page if pymupdf_page else pdfplumber_page, page_num)
                if ocr_text and len(ocr_text.split()) > len(cleaned_text.split()):
                    cleaned_text = self._clean_text(ocr_text)
                    text = ocr_text
            
            # Basic text processing
            paragraphs = self._split_paragraphs(cleaned_text)
            
            # Extract structured elements
            figures = self._extract_figures(cleaned_text, page_num)
            tables = self._extract_tables_enhanced(pdfplumber_page, pymupdf_page, pdf_path, page_num)
            monetary_values = self._extract_monetary_values(cleaned_text, page_num)
            percentages = self._extract_percentages(cleaned_text, page_num)
            years = self._extract_years(cleaned_text)
            constitutional_articles = self._extract_constitutional_articles(cleaned_text)
            legal_references = self._extract_legal_references(cleaned_text)
            institutional_references = self._extract_institutional_references(cleaned_text)
            citations = self._extract_citations(cleaned_text)
            scandals = self._extract_scandals(cleaned_text, page_num)
            keywords = self._extract_keywords(cleaned_text)
            images = self._extract_images(pymupdf_page, page_num)
            
            # Calculate page statistics
            word_count = len(cleaned_text.split())
            page_stats = {
                'word_count': word_count,
                'paragraph_count': len(paragraphs),
                'sentence_count': len(re.findall(r'[.!?]+', cleaned_text)),
                'monetary_count': len(monetary_values),
                'article_count': len(constitutional_articles),
                'table_count': len(tables),
                'figure_count': len(figures),
                'image_count': len(images)
            }
            
            # Calculate extraction quality metrics
            extraction_quality = {
                'text_length': len(cleaned_text),
                'word_count': word_count,
                'has_tables': len(tables) > 0,
                'has_figures': len(figures) > 0,
                'has_images': len(images) > 0,
                'quality_score': self._calculate_page_quality_score(
                    word_count, len(paragraphs), len(tables), len(figures)
                )
            }
            
            return PageData(
                page_number=page_num,
                text=cleaned_text,
                paragraphs=paragraphs,
                figures=figures,
                tables=tables,
                monetary_values=monetary_values,
                percentages=percentages,
                years=years,
                constitutional_articles=constitutional_articles,
                legal_references=legal_references,
                institutional_references=institutional_references,
                citations=citations,
                scandals=scandals,
                keywords=keywords,
                page_stats=page_stats,
                extraction_quality=extraction_quality,
                images=images
            )
            
        except Exception as e:
            self.logger.error(f"Error in page processing: {str(e)}")
            # Return minimal PageData object
            return PageData(
                page_number=page_num,
                text=text[:1000] if text else "",
                paragraphs=[],
                figures=[],
                tables=[],
                monetary_values=[],
                percentages=[],
                years=[],
                constitutional_articles=[],
                legal_references=[],
                institutional_references=[],
                citations=[],
                scandals=[],
                keywords=[],
                page_stats={},
                extraction_quality={'quality_score': 0.0},
                images=[]
            )
    
    def _extract_tables_enhanced(self, pdfplumber_page, pymupdf_page, pdf_path: str, page_num: int) -> List[Dict]:
        """Extract tables using multiple methods for maximum accuracy"""
        tables = []
        all_tables = []
        
        # Method 1: pdfplumber (best for most cases)
        try:
            page_tables = pdfplumber_page.extract_tables()
            for i, table in enumerate(page_tables):
                if table and len(table) > 0:
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                        cleaned_table.append(cleaned_row)
                    
                    all_tables.append({
                        'method': 'pdfplumber',
                        'table_number': i + 1,
                        'page': page_num,
                        'rows': len(cleaned_table),
                        'columns': len(cleaned_table[0]) if cleaned_table[0] else 0,
                        'data': cleaned_table,
                        'sample_data': cleaned_table[:3] if len(cleaned_table) > 3 else cleaned_table
                    })
        except Exception as e:
            self.logger.debug(f"pdfplumber table extraction failed for page {page_num}: {e}")
        
        # Method 2: Camelot (excellent for structured tables)
        if CAMELOT_AVAILABLE:
            try:
                camelot_tables = camelot.read_pdf(str(pdf_path), pages=str(page_num), flavor='lattice')
                for i, table in enumerate(camelot_tables):
                    if table.df is not None and not table.df.empty:
                        table_data = table.df.values.tolist()
                        all_tables.append({
                            'method': 'camelot',
                            'table_number': i + 1,
                            'page': page_num,
                            'rows': len(table_data),
                            'columns': len(table_data[0]) if table_data else 0,
                            'data': [[str(cell) for cell in row] for row in table_data],
                            'sample_data': table_data[:3] if len(table_data) > 3 else table_data,
                            'accuracy': table.accuracy
                        })
            except Exception as e:
                self.logger.debug(f"Camelot table extraction failed for page {page_num}: {e}")
        
        # Method 3: Tabula (good for simple tables)
        if TABULA_AVAILABLE:
            try:
                tabula_tables = tabula.read_pdf(pdf_path, pages=page_num, multiple_tables=True)
                for i, table in enumerate(tabula_tables):
                    if table is not None and not table.empty:
                        table_data = table.values.tolist()
                        all_tables.append({
                            'method': 'tabula',
                            'table_number': i + 1,
                            'page': page_num,
                            'rows': len(table_data),
                            'columns': len(table_data[0]) if table_data else 0,
                            'data': [[str(cell) for cell in row] for row in table_data],
                            'sample_data': table_data[:3] if len(table_data) > 3 else table_data
                        })
            except Exception as e:
                self.logger.debug(f"Tabula table extraction failed for page {page_num}: {e}")
        
        # Deduplicate and select best tables
        # Prefer tables with more rows and columns
        if all_tables:
            # Group by approximate similarity (same number of rows/columns)
            unique_tables = {}
            for table in all_tables:
                key = (table['rows'], table['columns'])
                if key not in unique_tables or table['rows'] * table['columns'] > unique_tables[key]['rows'] * unique_tables[key]['columns']:
                    unique_tables[key] = table
            
            tables = list(unique_tables.values())
            # Sort by size (largest first)
            tables.sort(key=lambda x: x['rows'] * x['columns'], reverse=True)
        
        return tables
    
    def _extract_images(self, pymupdf_page, page_num: int) -> List[Dict]:
        """Extract images from page"""
        images = []
        
        if not pymupdf_page:
            return images
        
        try:
            image_list = pymupdf_page.get_images()
            for img_index, img in enumerate(image_list):
                images.append({
                    'image_number': img_index + 1,
                    'page': page_num,
                    'xref': img[0],
                    'width': img[2] if len(img) > 2 else None,
                    'height': img[3] if len(img) > 3 else None,
                    'colorspace': img[1] if len(img) > 1 else None
                })
        except Exception as e:
            self.logger.debug(f"Image extraction failed for page {page_num}: {e}")
        
        return images
    
    def _calculate_page_quality_score(self, word_count: int, para_count: int, table_count: int, figure_count: int) -> float:
        """Calculate quality score for page extraction (0-1)"""
        score = 0.0
        
        # Text quality (0-0.5)
        if word_count > 500:
            score += 0.5
        elif word_count > 200:
            score += 0.3
        elif word_count > 50:
            score += 0.1
        
        # Structure quality (0-0.3)
        if para_count > 10:
            score += 0.3
        elif para_count > 5:
            score += 0.2
        elif para_count > 0:
            score += 0.1
        
        # Table quality (0-0.1)
        if table_count > 0:
            score += 0.1
        
        # Figure quality (0-0.1)
        if figure_count > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_quality_metrics(self, extraction_results: Dict) -> Dict:
        """Calculate overall quality metrics for the extraction"""
        pages = extraction_results['text']
        total_pages = len(pages)
        
        if total_pages == 0:
            return {'overall_score': 0.0}
        
        quality_scores = []
        total_words = 0
        pages_with_tables = 0
        pages_with_figures = 0
        
        for page_data in pages.values():
            quality = page_data.get('extraction_quality', {})
            quality_scores.append(quality.get('quality_score', 0.0))
            total_words += quality.get('word_count', 0)
            if quality.get('has_tables', False):
                pages_with_tables += 1
            if quality.get('has_figures', False):
                pages_with_figures += 1
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return {
            'overall_score': avg_quality,
            'average_words_per_page': total_words / total_pages if total_pages > 0 else 0,
            'pages_with_tables': pages_with_tables,
            'pages_with_figures': pages_with_figures,
            'table_coverage': pages_with_tables / total_pages if total_pages > 0 else 0.0,
            'figure_coverage': pages_with_figures / total_pages if total_pages > 0 else 0.0
        }
    
    def _extract_institutional_references(self, text: str) -> List[str]:
        """Extract institutional references from text"""
        references = []
        for pattern in self.institutional_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref_text = match.group(0)
                if ref_text not in references:
                    references.append(ref_text)
        return references
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract citation references from text"""
        # Pattern for citations like [1], [2], [1,2,3], etc.
        citation_pattern = r'\[(\d+(?:,\s*\d+)*)\]'
        matches = re.findall(citation_pattern, text)
        citations = []
        for match in matches:
            citation = f"[{match}]"
            if citation not in citations:
                citations.append(citation)
        return citations
    
    def _extract_monetary_values(self, text: str, page_num: int) -> List[Dict]:
        """Extract monetary values from text with enhanced patterns"""
        values = []
        seen = set()  # To avoid duplicates
        
        for pattern in self.patterns['monetary']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    # Determine multiplier based on unit
                    unit_text = match.group(0).lower()
                    multiplier = 1
                    if 'trillion' in unit_text or 'tn' in unit_text or 't' in unit_text:
                        multiplier = 1e12
                    elif 'billion' in unit_text or 'bn' in unit_text or 'b' in unit_text:
                        multiplier = 1e9
                    elif 'million' in unit_text or 'mn' in unit_text or 'm' in unit_text:
                        multiplier = 1e6
                    
                    final_amount = amount * multiplier
                    
                    # Get context (100 chars before and after for better context)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()
                    
                    # Create unique key to avoid duplicates
                    unique_key = (final_amount, match.start())
                    if unique_key not in seen:
                        seen.add(unique_key)
                        values.append({
                            'amount': final_amount,
                            'original_text': match.group(0),
                            'context': context,
                            'page': page_num,
                            'currency': 'KSh' if any(c in match.group(0) for c in ['KSh', 'KES', 'shillings']) else 'USD',
                            'unit': self._determine_unit(unit_text),
                            'position': match.start()
                        })
                    
                except (ValueError, AttributeError) as e:
                    continue
        
        # Sort by position in document
        values.sort(key=lambda x: x['position'])
        return values
    
    def _determine_unit(self, text: str) -> str:
        """Determine the unit of a monetary value"""
        text_lower = text.lower()
        if 'trillion' in text_lower or 'tn' in text_lower or 't' in text_lower:
            return 'trillion'
        elif 'billion' in text_lower or 'bn' in text_lower or 'b' in text_lower:
            return 'billion'
        elif 'million' in text_lower or 'mn' in text_lower or 'm' in text_lower:
            return 'million'
        else:
            return 'units'
    
    def _extract_percentages(self, text: str, page_num: int) -> List[Dict]:
        """Extract percentage values from text"""
        percentages = []
        seen = set()
        
        matches = re.finditer(self.patterns['percentage'], text)
        for match in matches:
            try:
                value = float(match.group(1))
                
                # Get context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                # Avoid duplicates
                unique_key = (value, match.start())
                if unique_key not in seen:
                    seen.add(unique_key)
                    percentages.append({
                        'value': value,
                        'original_text': match.group(0),
                        'context': context,
                        'page': page_num,
                        'position': match.start()
                    })
            except ValueError:
                continue
        
        # Sort by position
        percentages.sort(key=lambda x: x['position'])
        return percentages
    
    def _extract_years(self, text: str) -> List[int]:
        """Extract year references from text"""
        years = []
        matches = re.findall(self.patterns['year'], text)
        
        for match in matches:
            try:
                year = int(match)
                if 1900 <= year <= datetime.now().year + 10:  # Allow future projections
                    years.append(year)
            except ValueError:
                continue
        
        return sorted(list(set(years)))
    
    def _extract_constitutional_articles(self, text: str) -> List[str]:
        """Extract constitutional article references with enhanced patterns"""
        articles = []
        for pattern in self.patterns['article']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            articles.extend(matches)
        return sorted(list(set(articles)), key=lambda x: (len(x), x))
    
    def _extract_legal_references(self, text: str) -> List[str]:
        """Extract legal references (Acts, Laws, Statutes)"""
        patterns = [
            r'\b[A-Z][a-zA-Z\s]+Act\s*(?:No\.)?\s*\d{4}\b',
            r'\b[A-Z][a-zA-Z\s]+Law\s*(?:No\.)?\s*\d{4}\b',
            r'\bConstitution\s*(?:of Kenya)?\s*2010\b',
            r'\bPublic Finance Management Act\b',
            r'\bPublic Finance Management Act\s*\d{4}\b',
            r'\bAnti-Corruption and Economic Crimes Act\b',
            r'\bLeadership and Integrity Act\b',
            r'\bAccess to Information Act\b',
            r'\bElection Campaign Financing Act\b',
            r'\bProceeds of Crime and Anti-Money Laundering Act\b',
        ]
        
        references = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        
        return sorted(list(set(references)))
    
    def _extract_scandals(self, text: str, page_num: int) -> List[Dict]:
        """Extract corruption scandal references"""
        scandal_keywords = {
            'NYS': ['NYS scandal', 'National Youth Service scandal', 'NYS'],
            'KEMSA': ['KEMSA scandal', 'COVID scandal', 'KEMSA'],
            'Afya House': ['Afya House scandal', 'health scandal', 'Afya House'],
            'Anglo Leasing': ['Anglo Leasing', 'Anglo Leasing scandal'],
            'Goldenberg': ['Goldenberg scandal', 'Goldenberg'],
            'maize': ['maize scandal', 'fertilizer scandal', 'maize'],
            'NYANDARUA': ['Nyandarua scandal', 'Nyandarua'],
            'ARV': ['ARV scandal', 'HIV drugs scandal', 'ARV'],
            'Eurobond': ['Eurobond scandal', 'Eurobond'],
            'SGR': ['SGR scandal', 'Standard Gauge Railway'],
        }
        
        scandals = []
        text_lower = text.lower()
        seen = set()
        
        for scandal_name, keywords in scandal_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Find amount if mentioned nearby
                    amount_pattern = r'KSh\s*([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion)'
                    amount_match = re.search(amount_pattern, text, re.IGNORECASE)
                    
                    unique_key = (scandal_name, page_num)
                    if unique_key not in seen:
                        seen.add(unique_key)
                        scandals.append({
                            'name': scandal_name,
                            'keyword': keyword,
                            'page': page_num,
                            'amount': amount_match.group(0) if amount_match else None,
                            'context': self._extract_context(text, keyword, 150)
                        })
                    break  # Found one keyword per scandal
        
        return scandals
    
    def _extract_context(self, text: str, keyword: str, context_chars: int = 100) -> str:
        """Extract context around a keyword"""
        index = text.lower().find(keyword.lower())
        if index == -1:
            return ""
        
        start = max(0, index - context_chars)
        end = min(len(text), index + len(keyword) + context_chars)
        return text[start:end].strip()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        keywords = [
            'debt', 'corruption', 'audit', 'governance',
            'transparency', 'accountability', 'public funds',
            'misappropriation', 'embezzlement', 'fraud',
            'oversight', 'compliance', 'violation',
            'procurement', 'tender', 'contract',
            'budget', 'expenditure', 'revenue',
            'constitutional', 'rights', 'violation'
        ]
        
        found_keywords = []
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                found_keywords.append(keyword)
        
        return sorted(list(set(found_keywords)))
    
    def _extract_figures(self, text: str, page_num: int) -> List[Dict]:
        """Extract figure references with enhanced patterns"""
        figures = []
        seen = set()
        
        for pattern in self.patterns['figure']:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                fig_num = match.group(1)
                caption = match.group(2).strip()[:300] if len(match.groups()) > 1 else ""
                
                unique_key = (fig_num, page_num)
                if unique_key not in seen:
                    seen.add(unique_key)
                    figures.append({
                        'number': fig_num,
                        'caption': caption,
                        'page': page_num,
                        'full_match': match.group(0)[:200]
                    })
        
        return figures
    
    def _update_structure(self, structure: Dict, page_data: PageData, page_num: int):
        """Update document structure with page data"""
        if 'pages' not in structure:
            structure['pages'] = {}
        
        structure['pages'][page_num] = {
            'word_count': len(page_data.text.split()),
            'paragraph_count': len(page_data.paragraphs),
            'has_figures': len(page_data.figures) > 0,
            'has_tables': len(page_data.tables) > 0,
            'has_images': len(page_data.images) > 0,
            'monetary_count': len(page_data.monetary_values),
            'article_count': len(page_data.constitutional_articles),
            'quality_score': page_data.extraction_quality.get('quality_score', 0.0)
        }
    
    def _update_numerics(self, numerics: Dict, page_data: PageData):
        """Aggregate numeric data"""
        if 'monetary_values' not in numerics:
            numerics['monetary_values'] = []
        numerics['monetary_values'].extend(page_data.monetary_values)
        
        if 'percentages' not in numerics:
            numerics['percentages'] = []
        numerics['percentages'].extend(page_data.percentages)
        
        if 'years' not in numerics:
            numerics['years'] = []
        numerics['years'].extend(page_data.years)
    
    def _update_references(self, references: Dict, page_data: PageData):
        """Aggregate reference data"""
        # Legal references
        if 'legal' not in references:
            references['legal'] = []
        references['legal'].extend(page_data.legal_references)
        
        # Institutional references
        if 'institutional' not in references:
            references['institutional'] = []
        references['institutional'].extend(page_data.institutional_references)
        
        # Citations
        if 'citations' not in references:
            references['citations'] = []
        references['citations'].extend(page_data.citations)
        
        # Constitutional articles
        if 'constitutional' not in references:
            references['constitutional'] = []
        references['constitutional'].extend(page_data.constitutional_articles)
        
        # Scandals
        if 'scandals' not in references:
            references['scandals'] = []
        references['scandals'].extend(page_data.scandals)
    
    def _extract_chapters(self, pages_data: Dict) -> List[Dict]:
        """Extract chapter structure from pages"""
        chapters = []
        current_chapter = None
        
        for page_key, page_info in sorted(pages_data.items()):
            page_num = int(page_key.split('_')[1])
            text = page_info.get('text', '')
            
            # Look for chapter headings with enhanced patterns
            chapter_patterns = [
                r'Chapter\s*(\d+)[:\s]+(.+?)(?=\n|$)',
                r'CHAPTER\s*(\d+)[:\s]+(.+?)(?=\n|$)',
                r'(\d+)\.\s*([A-Z][A-Z\s]{10,})',  # All caps heading
                r'PART\s*(\d+)[:\s]+(.+?)(?=\n|$)',
            ]
            
            for pattern in chapter_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    chapter_num = match.group(1).strip()
                    chapter_title = match.group(2).strip()[:200]
                    
                    # Close previous chapter
                    if current_chapter:
                        current_chapter['end_page'] = page_num - 1
                        chapters.append(current_chapter)
                    
                    # Start new chapter
                    current_chapter = {
                        'number': chapter_num,
                        'title': chapter_title,
                        'start_page': page_num,
                        'end_page': None
                    }
                    break
        
        # Close last chapter
        if current_chapter:
            if pages_data:
                last_page = max(int(k.split('_')[1]) for k in pages_data.keys())
                current_chapter['end_page'] = last_page
            chapters.append(current_chapter)
        
        return chapters
    
    def _generate_statistics(self, extraction_results: Dict) -> Dict:
        """Generate extraction statistics"""
        total_pages = len(extraction_results['text'])
        total_words = 0
        total_paragraphs = 0
        total_monetary = 0
        total_scandals = 0
        total_articles = 0
        total_tables = 0
        total_figures = 0
        
        for page_info in extraction_results['text'].values():
            total_words += len(page_info.get('text', '').split())
            total_paragraphs += len(page_info.get('paragraphs', []))
            total_tables += len(page_info.get('tables', []))
            total_figures += len(page_info.get('figures', []))
            
            # Sum monetary values
            for monetary in page_info.get('monetary_values', []):
                total_monetary += monetary.get('amount', 0)
            
            total_scandals += len(page_info.get('scandals', []))
            total_articles += len(page_info.get('constitutional_articles', []))
        
        return {
            'total_pages': total_pages,
            'total_words': total_words,
            'total_paragraphs': total_paragraphs,
            'total_monetary_values': total_monetary,
            'total_scandals': total_scandals,
            'total_constitutional_articles': total_articles,
            'chapters_count': len(extraction_results['structure'].get('chapters', [])),
            'figures_count': total_figures,
            'tables_count': total_tables,
            'extraction_timestamp': datetime.now().isoformat()
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text with enhanced cleaning"""
        if not text:
            return ""
        
        # Remove excessive whitespace but preserve paragraph breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double
        
        # Fix common OCR/PDF extraction issues
        replacements = {
            '': '',
            '\x00': '',
            '\uf0b7': '•',
            '\uf0a7': '§',
            '\x0c': '\n',  # Form feed to newline
            'A rticle': 'Article',
            'C hapter': 'Chapter',
            'P art': 'Part',
            'F igure': 'Figure',
            'T able': 'Table',
            'K S h': 'KSh',
            'K E S': 'KES',
            'U S D': 'USD',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Normalize article references
        text = re.sub(r'Article\s+(\d+)', r'Article \1', text, flags=re.IGNORECASE)
        text = re.sub(r'Art\.\s*(\d+)', r'Article \1', text, flags=re.IGNORECASE)
        
        # Remove page numbers in headers/footers (standalone numbers)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Fix broken words (common in PDF extraction)
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Fix hyphenated words split across lines
        
        return text.strip()
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into meaningful paragraphs with enhanced logic"""
        # Split by double newlines or large spaces
        raw_paragraphs = [p.strip() for p in re.split(r'\n\s*\n|\s{4,}', text) if p.strip()]
        
        # Filter and clean paragraphs
        paragraphs = []
        for para in raw_paragraphs:
            # Skip very short paragraphs (likely headers/footers)
            if len(para.split()) < 3 and len(para) < 30:
                continue
            
            # Skip page numbers
            if re.match(r'^\d+$', para.strip()):
                continue
            
            # Skip common header/footer patterns
            if re.match(r'^(Page|Página|Página)\s+\d+', para, re.IGNORECASE):
                continue
            
            paragraphs.append(para)
        
        return paragraphs
    
    def _safe_extract_text(self, page) -> str:
        """Safely extract text from a page object"""
        try:
            if hasattr(page, 'extract_text'):
                return page.extract_text() or ""
            elif hasattr(page, 'get_text'):
                return page.get_text() or ""
            else:
                return str(page) or ""
        except Exception:
            return ""
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return "unknown_hash"
