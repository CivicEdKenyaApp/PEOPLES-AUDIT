import PyPDF2
import pdfplumber
import re
import json
from typing import Dict, List, Any, Optional
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

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
    institutional_references: List[str]  # Added missing field
    citations: List[str]                 # Added missing field
    scandals: List[Dict]
    keywords: List[str]
    page_stats: Dict[str, Any]

class PDFExtractor:
    """Extracts structured data from PDF documents"""
    
    def __init__(self, log_level=logging.INFO):
        self.setup_logging(log_level)
        
        # Regex patterns for extraction
        self.patterns = {
            'monetary': [
                r'KSh\s*([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion|B|M|T)?',
                r'\$([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion|B|M|T)?',
                r'([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion)\s*(?:shillings|KSh)'
            ],
            'article': r'Article\s*(\d+(?:[a-z])?(?:\(\d+[a-z]?\))?)',
            'year': r'\b(?:19|20)\d{2}\b',
            'percentage': r'(\d+(?:\.\d+)?)\s*%',
            'figure': r'Figure\s*(\d+(?:\.\d+)?)[:\s]+(.+?)(?=Figure\s*\d+|$)',
            'table': r'Table\s*(\d+(?:\.\d+)?)[:\s]+(.+?)(?=Table\s*\d+|$)'
        }
        
        # Institutional references patterns
        self.institutional_patterns = [
            r'\bEACC\b',
            r'\bODPP\b',
            r'\bDCI\b',
            r'\bOAG\b',
            r'\bCoB\b',
            r'\bKNBS\b',
            r'\bNational Treasury\b',
            r'\bCentral Bank\b',
            r'\bIMF\b',
            r'\bWorld Bank\b',
            r'\bParliament\b',
            r'\bSenate\b',
            r'\bCounty Government\b',
            r'\bPublic Service Commission\b'
        ]
    
    def setup_logging(self, log_level):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
    def extract_all(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all data from PDF document"""
        self.logger.info(f"Starting extraction of {pdf_path}")
        
        extraction_results = {
            'metadata': {},
            'text': {},
            'structure': {},
            'numerics': {},
            'references': {},
            'statistics': {}
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
                    'file_size': file.tell()
                })
                
                # Extract with pdfplumber for better accuracy
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num in range(num_pages):
                        try:
                            self.logger.info(f"Processing page {page_num + 1}/{num_pages}")
                            
                            # Get page from both libraries
                            pdf2_page = pdf_reader.pages[page_num]
                            pdfplumber_page = pdf.pages[page_num]
                            
                            # Extract text with fallback
                            text_pdf2 = self._safe_extract_text(pdf2_page)
                            text_pdfplumber = self._safe_extract_text(pdfplumber_page)
                            
                            # Use the better extraction
                            page_text = text_pdfplumber if len(text_pdfplumber) > len(text_pdf2) * 0.8 else text_pdf2
                            
                            # Process page
                            page_data = self._process_page(page_num + 1, page_text, pdfplumber_page)
                            
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
            
            # Post-processing
            extraction_results['structure']['chapters'] = self._extract_chapters(extraction_results['text'])
            extraction_results['statistics'] = self._generate_statistics(extraction_results)
            
            self.logger.info(f"PDF extraction completed: {num_pages} pages processed")
            
            return extraction_results
            
        except Exception as e:
            self.logger.error(f"Fatal error extracting PDF: {str(e)}")
            raise
    
    def _process_page(self, page_num: int, text: str, pdfplumber_page) -> PageData:
        """Process a single page and extract structured data"""
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Basic text processing
            paragraphs = self._split_paragraphs(cleaned_text)
            
            # Extract structured elements
            figures = self._extract_figures(text, page_num)
            tables = self._extract_tables(pdfplumber_page, page_num)
            monetary_values = self._extract_monetary_values(text, page_num)
            percentages = self._extract_percentages(text, page_num)
            years = self._extract_years(text)
            constitutional_articles = self._extract_constitutional_articles(text)
            legal_references = self._extract_legal_references(text)
            institutional_references = self._extract_institutional_references(text)  # Fixed
            citations = self._extract_citations(text)
            scandals = self._extract_scandals(text, page_num)
            keywords = self._extract_keywords(text)
            
            # Calculate page statistics
            page_stats = {
                'word_count': len(cleaned_text.split()),
                'paragraph_count': len(paragraphs),
                'sentence_count': len(re.findall(r'[.!?]+', cleaned_text)),
                'monetary_count': len(monetary_values),
                'article_count': len(constitutional_articles)
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
                page_stats=page_stats
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
                page_stats={}
            )
    
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
        # Pattern for citations like [1], [2], etc.
        citation_pattern = r'\[(\d+(?:,\s*\d+)*)\]'
        matches = re.findall(citation_pattern, text)
        citations = []
        for match in matches:
            if match not in citations:
                citations.append(f"[{match}]")
        return citations
    
    def _extract_monetary_values(self, text: str, page_num: int) -> List[Dict]:
        """Extract monetary values from text"""
        values = []
        
        for pattern in self.patterns['monetary']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    # Determine multiplier based on unit
                    unit_text = match.group(0).lower()
                    multiplier = 1
                    if 'trillion' in unit_text or 't' in unit_text:
                        multiplier = 1e12
                    elif 'billion' in unit_text or 'b' in unit_text:
                        multiplier = 1e9
                    elif 'million' in unit_text or 'm' in unit_text:
                        multiplier = 1e6
                    
                    final_amount = amount * multiplier
                    
                    # Get context (50 chars before and after)
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    
                    values.append({
                        'amount': final_amount,
                        'original_text': match.group(0),
                        'context': context,
                        'page': page_num,
                        'currency': 'KSh' if 'KSh' in match.group(0) else 'USD',
                        'unit': self._determine_unit(unit_text)
                    })
                    
                except (ValueError, AttributeError):
                    continue
        
        return values
    
    def _determine_unit(self, text: str) -> str:
        """Determine the unit of a monetary value"""
        text_lower = text.lower()
        if 'trillion' in text_lower or 't' in text_lower:
            return 'trillion'
        elif 'billion' in text_lower or 'b' in text_lower:
            return 'billion'
        elif 'million' in text_lower or 'm' in text_lower:
            return 'million'
        else:
            return 'units'
    
    def _extract_percentages(self, text: str, page_num: int) -> List[Dict]:
        """Extract percentage values from text"""
        percentages = []
        matches = re.finditer(self.patterns['percentage'], text)
        
        for match in matches:
            try:
                value = float(match.group(1))
                
                # Get context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                percentages.append({
                    'value': value,
                    'original_text': match.group(0),
                    'context': context,
                    'page': page_num
                })
            except ValueError:
                continue
        
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
        
        return list(set(years))
    
    def _extract_constitutional_articles(self, text: str) -> List[str]:
        """Extract constitutional article references"""
        articles = re.findall(self.patterns['article'], text)
        return list(set(articles))
    
    def _extract_legal_references(self, text: str) -> List[str]:
        """Extract legal references (Acts, Laws, Statutes)"""
        patterns = [
            r'\b[A-Z][a-zA-Z\s]+Act\s*(?:No\.)?\s*\d{4}\b',
            r'\b[A-Z][a-zA-Z\s]+Law\s*(?:No\.)?\s*\d{4}\b',
            r'\bConstitution\s*(?:of Kenya)?\s*2010\b',
            r'\bPublic Finance Management Act\b',
            r'\bAnti-Corruption and Economic Crimes Act\b',
            r'\bLeadership and Integrity Act\b'
        ]
        
        references = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        
        return list(set(references))
    
    def _extract_scandals(self, text: str, page_num: int) -> List[Dict]:
        """Extract corruption scandal references"""
        scandal_keywords = {
            'NYS': ['NYS scandal', 'National Youth Service scandal'],
            'KEMSA': ['KEMSA scandal', 'COVID scandal'],
            'Afya House': ['Afya House scandal', 'health scandal'],
            'Anglo Leasing': ['Anglo Leasing'],
            'Goldenberg': ['Goldenberg scandal'],
            'maize': ['maize scandal', 'fertilizer scandal'],
            'NYANDARUA': ['Nyandarua scandal'],
            'ARV': ['ARV scandal', 'HIV drugs scandal']
        }
        
        scandals = []
        text_lower = text.lower()
        
        for scandal_name, keywords in scandal_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Find amount if mentioned
                    amount_pattern = r'KSh\s*([\d,]+(?:\.\d+)?)\s*(?:billion|million)'
                    amount_match = re.search(amount_pattern, text, re.IGNORECASE)
                    
                    scandals.append({
                        'name': scandal_name,
                        'keyword': keyword,
                        'page': page_num,
                        'amount': amount_match.group(0) if amount_match else None,
                        'context': self._extract_context(text, keyword, 100)
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
            'oversight', 'compliance', 'violation'
        ]
        
        found_keywords = []
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_figures(self, text: str, page_num: int) -> List[Dict]:
        """Extract figure references"""
        figures = []
        matches = re.finditer(self.patterns['figure'], text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            figures.append({
                'number': match.group(1),
                'caption': match.group(2).strip()[:200],
                'page': page_num
            })
        
        return figures
    
    def _extract_tables(self, page, page_num: int) -> List[Dict]:
        """Extract table data"""
        tables = []
        
        try:
            # Try to extract tables using pdfplumber
            page_tables = page.extract_tables()
            
            for i, table in enumerate(page_tables):
                if table and len(table) > 0:
                    # Clean table data
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                        cleaned_table.append(cleaned_row)
                    
                    tables.append({
                        'table_number': i + 1,
                        'page': page_num,
                        'rows': len(cleaned_table),
                        'columns': len(cleaned_table[0]) if cleaned_table[0] else 0,
                        'sample_data': cleaned_table[:3] if len(cleaned_table) > 3 else cleaned_table
                    })
                    
        except Exception as e:
            self.logger.debug(f"Could not extract tables from page {page_num}: {str(e)}")
        
        return tables
    
    def _update_structure(self, structure: Dict, page_data: PageData, page_num: int):
        """Update document structure with page data"""
        if 'pages' not in structure:
            structure['pages'] = {}
        
        structure['pages'][page_num] = {
            'word_count': len(page_data.text.split()),
            'paragraph_count': len(page_data.paragraphs),
            'has_figures': len(page_data.figures) > 0,
            'has_tables': len(page_data.tables) > 0,
            'monetary_count': len(page_data.monetary_values),
            'article_count': len(page_data.constitutional_articles)
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
        
        # Institutional references (FIXED)
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
        
        for page_key, page_info in pages_data.items():
            page_num = int(page_key.split('_')[1])
            text = page_info['text']
            
            # Look for chapter headings
            chapter_patterns = [
                r'Chapter\s*(\d+)[:\s]+(.+)',
                r'CHAPTER\s*(\d+)[:\s]+(.+)',
                r'(\d+)\.\s*([A-Z][^a-z]{20,})'  # All caps heading
            ]
            
            for pattern in chapter_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    chapter_num = match.group(1).strip()
                    chapter_title = match.group(2).strip()
                    
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
            current_chapter['end_page'] = len(pages_data)
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
        
        for page_info in extraction_results['text'].values():
            total_words += len(page_info['text'].split())
            total_paragraphs += len(page_info['paragraphs'])
            
            # Sum monetary values
            for monetary in page_info['monetary_values']:
                total_monetary += monetary['amount']
            
            total_scandals += len(page_info['scandals'])
            total_articles += len(page_info['constitutional_articles'])
        
        return {
            'total_pages': total_pages,
            'total_words': total_words,
            'total_paragraphs': total_paragraphs,
            'total_monetary_values': total_monetary,
            'total_scandals': total_scandals,
            'total_constitutional_articles': total_articles,
            'chapters_count': len(extraction_results['structure'].get('chapters', [])),
            'figures_count': sum(len(p['figures']) for p in extraction_results['text'].values()),
            'tables_count': sum(len(p['tables']) for p in extraction_results['text'].values()),
            'extraction_timestamp': datetime.now().isoformat()
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR/PDF extraction issues
        replacements = {
            '�': '',
            '\x00': '',
            '\uf0b7': '•',
            '\uf0a7': '§',
            '\x0c': '\n',  # Form feed to newline
            'A rticle': 'Article',
            'C hapter': 'Chapter',
            'P art': 'Part',
            'F igure': 'Figure',
            'T able': 'Table'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Normalize article references
        text = re.sub(r'Article\s+(\d+)', r'Article \1', text, flags=re.IGNORECASE)
        
        # Remove page numbers in headers/footers
        text = re.sub(r'\n\d+\n', '\n', text)
        
        return text.strip()
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into meaningful paragraphs"""
        # Split by double newlines or large spaces
        raw_paragraphs = [p.strip() for p in re.split(r'\n\s*\n|\s{4,}', text) if p.strip()]
        
        # Filter and clean paragraphs
        paragraphs = []
        for para in raw_paragraphs:
            # Skip very short paragraphs (likely headers/footers)
            if len(para.split()) < 5 and len(para) < 50:
                continue
            
            # Skip page numbers
            if re.match(r'^\d+$', para.strip()):
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