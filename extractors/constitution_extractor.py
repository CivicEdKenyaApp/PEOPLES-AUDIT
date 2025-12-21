# extractors/constitution_extractor.py
import PyPDF2
import pdfplumber
import re
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

@dataclass
class ConstitutionalArticle:
    article_number: str
    full_text: str
    title: str
    chapter: str
    part: str
    page_number: int
    section: Optional[str]
    subsection: Optional[str]
    simplified_summary: str
    rights_guaranteed: List[str]
    obligations: List[str]
    prohibitions: List[str]

@dataclass
class ConstitutionStructure:
    preamble: str
    chapters: Dict[str, List[ConstitutionalArticle]]
    parts: Dict[str, List[str]]
    total_articles: int
    total_pages: int
    amendment_history: List[Dict]

class ConstitutionExtractor:
    """Extracts and structures the Constitution of Kenya 2010"""
    
    def __init__(self, log_level=logging.INFO):
        self.setup_logging(log_level)
        
        # Regex patterns for constitutional extraction
        self.patterns = {
            'article': r'Article\s*(\d+(?:[a-z])?)\s*(.+?)(?=Article\s*\d+|$)',
            'chapter': r'CHAPTER\s*(\d+)[:\s]*([A-Z\s]+)',
            'part': r'PART\s*([IVXLCDM]+)[:\s]*([A-Z\s]+)',
            'section': r'\((\d+)\)\s*(.+?)(?=\(\d+\)|$)',
            'subsection': r'\(([a-z])\)\s*(.+?)(?=\([a-z]\)|$)',
            'rights': r'right to\s+(.+?)(?:\.|;)',
            'obligations': r'(?:shall|must)\s+(.+?)(?:\.|;)',
            'prohibitions': r'(?:shall not|must not|no)\s+(.+?)(?:\.|;)',
            'preamble': r'WE, THE PEOPLE OF KENYA(.+?)CHAPTER',
            'amendment': r'Amendment\s*(?:No\.)?\s*(\d+).*?(\d{4})'
        }
        
        # Article summaries for simplified explanations
        self.article_summaries = {
            '1': {
                'simple': "All power belongs to the people of Kenya. The government gets its authority from you.",
                'detailed': "Sovereignty of the people and how it can be exercised."
            },
            '10': {
                'simple': "Lists the values that should guide all government actions: honesty, fairness, participation, and justice.",
                'detailed': "National values and principles of governance that bind all state organs."
            },
            '19': {
                'simple': "The Bill of Rights is for everyone and must be respected by all.",
                'detailed': "Application of Bill of Rights to all persons and interpretation."
            },
            '20': {
                'simple': "The government must apply the Bill of Rights to everyone.",
                'detailed': "Application of Bill of Rights."
            },
            '21': {
                'simple': "The government must make laws to protect your rights.",
                'detailed': "Implementation of rights and fundamental freedoms."
            },
            '22': {
                'simple': "You can go to court if your rights are violated.",
                'detailed': "Enforcement of Bill of Rights through courts."
            },
            '23': {
                'simple': "Courts can give you justice when your rights are violated.",
                'detailed': "Authority of courts to uphold and enforce the Bill of Rights."
            },
            '24': {
                'simple': "Some rights can be limited, but only if necessary and fair.",
                'detailed': "Limitation of rights and fundamental freedoms."
            },
            '25': {
                'simple': "Some rights can never be taken away, even in emergencies.",
                'detailed': "Fundamental rights that may not be limited."
            },
            '26': {
                'simple': "Every person has the right to life.",
                'detailed': "Right to life and protection."
            },
            '27': {
                'simple': "Everyone is equal before the law and must be treated fairly.",
                'detailed': "Equality and freedom from discrimination."
            },
            '28': {
                'simple': "Every person has dignity and must be respected.",
                'detailed': "Human dignity."
            },
            '29': {
                'simple': "You have the right to freedom and security.",
                'detailed': "Freedom and security of the person."
            },
            '30': {
                'simple': "You cannot be made a slave or forced to work.",
                'detailed': "Freedom from slavery, servitude and forced labour."
            },
            '31': {
                'simple': "You have the right to privacy in your home and communications.",
                'detailed': "Privacy."
            },
            '32': {
                'simple': "You have freedom of religion and belief.",
                'detailed': "Freedom of conscience, religion, belief and opinion."
            },
            '33': {
                'simple': "You have freedom to express yourself and access information.",
                'detailed': "Freedom of expression."
            },
            '34': {
                'simple': "The media is free and independent.",
                'detailed': "Freedom of the media."
            },
            '35': {
                'simple': "You have the right to get information from the government.",
                'detailed': "Access to information."
            },
            '36': {
                'simple': "You can form or join any association or group.",
                'detailed': "Freedom of association."
            },
            '37': {
                'simple': "You can peacefully protest, demonstrate, and picket.",
                'detailed': "Assembly, demonstration, picketing and petition."
            },
            '38': {
                'simple': "You have political rights including voting and running for office.",
                'detailed': "Political rights."
            },
            '39': {
                'simple': "You have the right to move and live anywhere in Kenya.",
                'detailed': "Freedom of movement and residence."
            },
            '40': {
                'simple': "You have the right to own property.",
                'detailed': "Protection of right to property."
            },
            '41': {
                'simple': "Workers have rights including fair pay and safe conditions.",
                'detailed': "Labour relations."
            },
            '42': {
                'simple': "You have the right to a clean and healthy environment.",
                'detailed': "Right to a clean and healthy environment."
            },
            '43': {
                'simple': "You have rights to healthcare, food, water, housing, education, and social security.",
                'detailed': "Economic and social rights."
            },
            '44': {
                'simple': "Your language and culture must be respected.",
                'detailed': "Language and culture."
            },
            '45': {
                'simple': "Families are protected by the state.",
                'detailed': "Family."
            },
            '46': {
                'simple': "Consumers have rights to quality goods and services.",
                'detailed': "Consumer rights."
            },
            '47': {
                'simple': "You have the right to fair administrative action.",
                'detailed': "Fair administrative action."
            },
            '48': {
                'simple': "You have the right to access justice.",
                'detailed': "Access to justice."
            },
            '49': {
                'simple': "You have rights when arrested or detained.",
                'detailed': "Rights of arrested persons."
            },
            '50': {
                'simple': "You have the right to a fair trial.",
                'detailed': "Fair hearing."
            },
            '51': {
                'simple': "You have rights if you are held in custody.",
                'detailed': "Rights of persons detained, held in custody or imprisoned."
            },
            '52': {
                'simple': "This part explains how the Bill of Rights works.",
                'detailed': "Interpretation of this Part."
            },
            '53': {
                'simple': "Children have special rights and protections.",
                'detailed': "Rights of the child."
            },
            '54': {
                'simple': "Persons with disabilities have equal rights.",
                'detailed': "Rights of persons with disabilities."
            },
            '55': {
                'simple': "Youth have rights including access to relevant education.",
                'detailed': "Rights of the youth."
            },
            '56': {
                'simple': "Minorities and marginalized groups have special protections.",
                'detailed': "Rights of minorities and marginalized groups."
            },
            '57': {
                'simple': "Older members of society have the right to care and assistance.",
                'detailed': "Rights of older members of society."
            },
            '58': {
                'simple': "Emergency powers are limited and must respect rights.",
                'detailed': "Derogation from rights and fundamental freedoms during emergency."
            },
            '73': {
                'simple': "Leaders must act with integrity and use authority for public good.",
                'detailed': "Responsibilities of leadership."
            },
            '74': {
                'simple': "Leaders must follow a code of conduct.",
                'detailed': "Oath of office of State officers."
            },
            '75': {
                'simple': "Leaders must avoid conflicts of interest.",
                'detailed': "Conduct of State officers."
            },
            '76': {
                'simple': "Financial integrity requirements for leaders.",
                'detailed': "Financial probity of State officers."
            },
            '77': {
                'simple': "Restrictions on public officers engaging in other gainful employment.",
                'detailed': "Restriction on activities of State officers."
            },
            '78': {
                'simple': "Citizenship and leadership qualifications.",
                'detailed': "Citizenship and leadership."
            },
            '79': {
                'simple': "Legislation to establish the Ethics and Anti-Corruption Commission.",
                'detailed': "Legislation on leadership."
            },
            '80': {
                'simple': "Parliament consists of the National Assembly and the Senate.",
                'detailed': "Establishment of Parliament."
            },
            '201': {
                'simple': "Government money must be managed with openness, participation, and fairness.",
                'detailed': "Principles of public finance."
            },
            '202': {
                'simple': "County governments get a share of national revenue.",
                'detailed': "Equitable sharing of national revenue."
            },
            '203': {
                'simple': "Commission on Revenue Allocation determines county shares.",
                'detailed': "Equitable share and other financial laws."
            },
            '204': {
                'simple': "Fund for marginalized areas.",
                'detailed': "Equalisation Fund."
            },
            '205': {
                'simple': "Consultation on division of revenue.",
                'detailed': "Consultation on division of revenue."
            },
            '206': {
                'simple': "Emergency fund for unforeseen circumstances.",
                'detailed': "Contingencies Fund."
            },
            '207': {
                'simple': "Consolidated Fund and other public funds.",
                'detailed': "Revenue Funds for national and county governments."
            },
            '208': {
                'simple': "Control of public money.",
                'detailed': "Control of public money."
            },
            '209': {
                'simple': "Power to impose taxes and charges.",
                'detailed': "Power to impose taxes and charges."
            },
            '210': {
                'simple': "Imposition of tax.",
                'detailed': "Imposition of tax."
            },
            '211': {
                'simple': "Borrowing by national government.",
                'detailed': "Borrowing by national government."
            },
            '212': {
                'simple': "Borrowing by counties.",
                'detailed': "Borrowing by counties."
            },
            '213': {
                'simple': "Loan guarantees by national government.",
                'detailed': "Loan guarantees by national government."
            },
            '214': {
                'simple': "Public debt management.",
                'detailed': "Public debt."
            },
            '215': {
                'simple': "Central Bank of Kenya.",
                'detailed': "Central Bank of Kenya."
            },
            '216': {
                'simple': "Financial offices and institutions.",
                'detailed': "Financial offices and institutions."
            },
            '217': {
                'simple': "Procurement of public goods and services.",
                'detailed': "Procurement of public goods and services."
            },
            '218': {
                'simple': "Financial control and accountability.",
                'detailed': "Financial control."
            },
            '219': {
                'simple': "Accounts and audit of public entities.",
                'detailed': "Accounts and audit of public entities."
            },
            '220': {
                'simple': "Procedures for dealing with public finance.",
                'detailed': "Procedure for dealing with finance bills."
            },
            '221': {
                'simple': "Budgets and spending.",
                'detailed': "Budgets."
            },
            '222': {
                'simple': "Supplementary budgets.",
                'detailed': "Supplementary appropriation."
            },
            '223': {
                'simple': "Authority to spend before approval by Parliament.",
                'detailed': "Authority to spend before appropriation."
            },
            '224': {
                'simple': "Unspent funds.",
                'detailed': "Unspent funds."
            },
            '225': {
                'simple': "Controller of Budget.",
                'detailed': "Controller of Budget."
            },
            '226': {
                'simple': "Auditor-General.",
                'detailed': "Auditor-General."
            },
            '227': {
                'simple': "Reports of Controller of Budget and Auditor-General.",
                'detailed': "Reports of Controller of Budget and Auditor-General."
            },
            '228': {
                'simple': "Legislation on public finance.",
                'detailed': "Legislation on public finance."
            },
            '229': {
                'simple': "Public service values and principles.",
                'detailed': "Values and principles of public service."
            },
            '230': {
                'simple': "The public service.",
                'detailed': "The public service."
            },
            '231': {
                'simple': "Teachers Service Commission.",
                'detailed': "Teachers Service Commission."
            },
            '232': {
                'simple': "Values and principles of public service.",
                'detailed': "Values and principles of public service."
            }
        }
    
    def setup_logging(self, log_level):
        """Setup logging configuration"""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'constitution_extractor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract and structure the entire Constitution
        
        Args:
            pdf_path: Path to the Constitution PDF file
            
        Returns:
            Dict containing structured constitution data
        """
        self.logger.info(f"Starting extraction of Constitution from: {pdf_path}")
        
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"Constitution PDF not found: {pdf_path}")
        
        try:
            # Extract raw text
            raw_text = self._extract_raw_text(pdf_path)
            
            # Extract structure
            structure = self._extract_structure(raw_text)
            
            # Extract articles
            articles = self._extract_articles(raw_text)
            
            # Extract preamble
            preamble = self._extract_preamble(raw_text)
            
            # Extract amendment history
            amendments = self._extract_amendments(raw_text)
            
            # Create comprehensive output
            result = {
                'metadata': {
                    'source_file': pdf_path,
                    'extraction_date': datetime.now().isoformat(),
                    'total_pages': len(raw_text),
                    'total_articles': len(articles),
                    'constitution_version': 'Kenya 2010 with Amendments'
                },
                'preamble': preamble,
                'structure': asdict(structure),
                'articles': [asdict(article) for article in articles],
                'amendments': amendments,
                'article_index': self._create_article_index(articles),
                'chapter_index': self._create_chapter_index(structure, articles),
                'rights_index': self._create_rights_index(articles)
            }
            
            self.logger.info(f"Constitution extraction completed. Found {len(articles)} articles.")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting constitution: {str(e)}")
            raise
    
    def _extract_raw_text(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract raw text from PDF with page-level structure"""
        raw_pages = []
        
        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    # Clean the text
                    cleaned_text = self._clean_constitution_text(text)
                    
                    raw_pages.append({
                        'page_number': page_num,
                        'raw_text': text,
                        'cleaned_text': cleaned_text,
                        'has_articles': 'Article' in text,
                        'has_chapter': 'CHAPTER' in text,
                        'has_part': 'PART' in text
                    })
                    
                    self.logger.debug(f"Processed page {page_num}: {len(cleaned_text)} chars")
            
            self.logger.info(f"Extracted text from {len(raw_pages)} pages")
            return raw_pages
            
        except Exception as e:
            self.logger.error(f"Error extracting raw text: {str(e)}")
            return []
    
    def _clean_constitution_text(self, text: str) -> str:
        """Clean and normalize constitution text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR/PDF extraction issues
        replacements = {
            '�': '',
            '\x00': '',
            '\uf0b7': '•',
            '\uf0a7': '§',
            'A rticle': 'Article',
            'C hapter': 'Chapter',
            'P art': 'Part'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Normalize article references
        text = re.sub(r'Article\s+(\d+)', r'Article \1', text)
        
        return text.strip()
    
    def _extract_structure(self, raw_pages: List[Dict]) -> ConstitutionStructure:
        """Extract the structure of the constitution"""
        chapters = {}
        parts = {}
        preamble = ""
        
        current_chapter = None
        current_part = None
        
        for page in raw_pages:
            text = page['cleaned_text']
            
            # Extract preamble (usually on first few pages)
            if page['page_number'] <= 3:
                preamble_match = re.search(self.patterns['preamble'], text, re.DOTALL | re.IGNORECASE)
                if preamble_match:
                    preamble = preamble_match.group(1).strip()
            
            # Extract chapters
            chapter_matches = re.finditer(self.patterns['chapter'], text, re.IGNORECASE)
            for match in chapter_matches:
                chapter_num = match.group(1).strip()
                chapter_title = match.group(2).strip()
                current_chapter = chapter_num
                
                if chapter_num not in chapters:
                    chapters[chapter_num] = {
                        'title': chapter_title,
                        'page': page['page_number'],
                        'articles': []
                    }
            
            # Extract parts
            part_matches = re.finditer(self.patterns['part'], text, re.IGNORECASE)
            for match in part_matches:
                part_num = match.group(1).strip()
                part_title = match.group(2).strip()
                current_part = part_num
                
                if part_num not in parts:
                    parts[part_num] = {
                        'title': part_title,
                        'page': page['page_number'],
                        'chapters': []
                    }
        
        return ConstitutionStructure(
            preamble=preamble,
            chapters=chapters,
            parts=parts,
            total_articles=0,  # Will be updated
            total_pages=len(raw_pages),
            amendment_history=[]
        )
    
    def _extract_articles(self, raw_pages: List[Dict]) -> List[ConstitutionalArticle]:
        """Extract all constitutional articles"""
        all_articles = []
        
        for page in raw_pages:
            text = page['cleaned_text']
            page_num = page['page_number']
            
            # Extract articles using the article pattern
            article_matches = re.finditer(self.patterns['article'], text, re.DOTALL)
            
            for match in article_matches:
                article_num = match.group(1).strip()
                article_text = match.group(2).strip()
                
                # Clean article number (remove trailing punctuation)
                article_num = re.sub(r'[^\w]', '', article_num)
                
                # Extract sections and subsections
                sections = self._extract_sections(article_text)
                subsections = self._extract_subsections(article_text)
                
                # Extract rights, obligations, prohibitions
                rights = self._extract_rights(article_text)
                obligations = self._extract_obligations(article_text)
                prohibitions = self._extract_prohibitions(article_text)
                
                # Get simplified summary
                simple_summary = self._get_article_summary(article_num, article_text)
                
                # Determine chapter and part
                chapter, part = self._determine_article_location(article_num, raw_pages)
                
                # Create article object
                article = ConstitutionalArticle(
                    article_number=article_num,
                    full_text=article_text,
                    title=self._extract_article_title(article_text),
                    chapter=chapter,
                    part=part,
                    page_number=page_num,
                    section=sections[0] if sections else None,
                    subsection=subsections[0] if subsections else None,
                    simplified_summary=simple_summary,
                    rights_guaranteed=rights,
                    obligations=obligations,
                    prohibitions=prohibitions
                )
                
                all_articles.append(article)
                self.logger.debug(f"Extracted Article {article_num} from page {page_num}")
        
        # Sort articles by number
        all_articles.sort(key=lambda x: self._article_sort_key(x.article_number))
        
        return all_articles
    
    def _extract_sections(self, article_text: str) -> List[str]:
        """Extract sections from article text"""
        sections = []
        section_matches = re.finditer(self.patterns['section'], article_text, re.DOTALL)
        
        for match in section_matches:
            section_num = match.group(1)
            section_text = match.group(2).strip()
            sections.append(f"{section_num}. {section_text}")
        
        return sections
    
    def _extract_subsections(self, article_text: str) -> List[str]:
        """Extract subsections from article text"""
        subsections = []
        subsection_matches = re.finditer(self.patterns['subsection'], article_text, re.DOTALL)
        
        for match in subsection_matches:
            subsection_letter = match.group(1)
            subsection_text = match.group(2).strip()
            subsections.append(f"({subsection_letter}) {subsection_text}")
        
        return subsections
    
    def _extract_rights(self, article_text: str) -> List[str]:
        """Extract rights guaranteed by the article"""
        rights = []
        rights_matches = re.finditer(self.patterns['rights'], article_text, re.IGNORECASE)
        
        for match in rights_matches:
            right = match.group(1).strip()
            if right and len(right) > 3:  # Filter out very short matches
                rights.append(right)
        
        return rights
    
    def _extract_obligations(self, article_text: str) -> List[str]:
        """Extract obligations imposed by the article"""
        obligations = []
        obligation_matches = re.finditer(self.patterns['obligations'], article_text, re.IGNORECASE)
        
        for match in obligation_matches:
            obligation = match.group(1).strip()
            if obligation and len(obligation) > 3:
                obligations.append(obligation)
        
        return obligations
    
    def _extract_prohibitions(self, article_text: str) -> List[str]:
        """Extract prohibitions in the article"""
        prohibitions = []
        prohibition_matches = re.finditer(self.patterns['prohibitions'], article_text, re.IGNORECASE)
        
        for match in prohibition_matches:
            prohibition = match.group(1).strip()
            if prohibition and len(prohibition) > 3:
                prohibitions.append(prohibition)
        
        return prohibitions
    
    def _extract_article_title(self, article_text: str) -> str:
        """Extract the title/heading of an article"""
        # Look for the first sentence or phrase before a period or colon
        first_sentence = article_text.split('.')[0].split(':')[0].strip()
        
        # If it's too long, take first 100 chars
        if len(first_sentence) > 100:
            first_sentence = first_sentence[:100] + "..."
        
        return first_sentence
    
    def _get_article_summary(self, article_num: str, article_text: str) -> str:
        """Get simplified summary of an article"""
        clean_num = re.sub(r'[^\d]', '', article_num)
        
        if clean_num in self.article_summaries:
            return self.article_summaries[clean_num]['simple']
        
        # Fallback: generate a simple summary
        if 'right' in article_text.lower():
            return f"Article {article_num} guarantees certain rights to Kenyan citizens."
        elif 'shall' in article_text.lower() or 'must' in article_text.lower():
            return f"Article {article_num} imposes obligations on the government or citizens."
        else:
            return f"Article {article_num} of the Constitution of Kenya."
    
    def _determine_article_location(self, article_num: str, raw_pages: List[Dict]) -> tuple:
        """Determine which chapter and part an article belongs to"""
        # Default values
        chapter = "Unknown"
        part = "Unknown"
        
        # Simple mapping based on common constitutional structure
        article_num_clean = re.sub(r'[^\d]', '', article_num)
        
        if article_num_clean.isdigit():
            num = int(article_num_clean)
            
            # Chapter mapping (simplified)
            if 1 <= num <= 3:
                chapter = "1"
                part = "I"
            elif 4 <= num <= 19:
                chapter = "4"
                part = "II"
            elif 20 <= num <= 58:
                chapter = "4"
                part = "II"
            elif 59 <= num <= 72:
                chapter = "5"
                part = "III"
            elif 73 <= num <= 80:
                chapter = "6"
                part = "IV"
            elif 81 <= num <= 98:
                chapter = "7"
                part = "V"
            elif 99 <= num <= 118:
                chapter = "8"
                part = "VI"
            elif 119 <= num <= 132:
                chapter = "9"
                part = "VII"
            elif 133 <= num <= 159:
                chapter = "10"
                part = "VIII"
            elif 160 <= num <= 173:
                chapter = "11"
                part = "IX"
            elif 174 <= num <= 200:
                chapter = "11"
                part = "IX"
            elif 201 <= num <= 228:
                chapter = "12"
                part = "X"
            elif 229 <= num <= 232:
                chapter = "13"
                part = "XI"
            elif 233 <= num <= 261:
                chapter = "14"
                part = "XII"
            elif 262 <= num <= 264:
                chapter = "15"
                part = "XIII"
            elif 265 <= num <= 269:
                chapter = "16"
                part = "XIV"
            elif 270 <= num <= 274:
                chapter = "17"
                part = "XV"
            else:
                chapter = "Unknown"
                part = "Unknown"
        
        return chapter, part
    
    def _article_sort_key(self, article_num: str) -> tuple:
        """Create sort key for article numbers"""
        # Handle numbers like "1", "1A", "1(1)", etc.
        match = re.match(r'(\d+)([A-Za-z]*)', article_num)
        if match:
            num = int(match.group(1))
            suffix = match.group(2)
            return (num, suffix)
        return (9999, article_num)  # Put unrecognized at end
    
    def _extract_preamble(self, raw_pages: List[Dict]) -> str:
        """Extract the preamble of the constitution"""
        preamble_pages = raw_pages[:3]  # Preamble is usually on first few pages
        
        preamble_text = ""
        for page in preamble_pages:
            text = page['cleaned_text']
            
            # Look for preamble pattern
            preamble_match = re.search(self.patterns['preamble'], text, re.DOTALL | re.IGNORECASE)
            if preamble_match:
                preamble_text += preamble_match.group(1).strip() + "\n\n"
        
        if not preamble_text:
            # Fallback: look for "WE, THE PEOPLE OF KENYA"
            for page in preamble_pages:
                if "WE, THE PEOPLE OF KENYA" in page['cleaned_text']:
                    start = page['cleaned_text'].find("WE, THE PEOPLE OF KENYA")
                    preamble_text = page['cleaned_text'][start:start+2000]  # First 2000 chars
                    break
        
        return preamble_text.strip()
    
    def _extract_amendments(self, raw_pages: List[Dict]) -> List[Dict]:
        """Extract amendment history"""
        amendments = []
        
        for page in raw_pages:
            text = page['cleaned_text']
            
            # Look for amendment references
            amendment_matches = re.finditer(self.patterns['amendment'], text, re.IGNORECASE)
            
            for match in amendment_matches:
                amendment_num = match.group(1)
                year = match.group(2)
                
                amendments.append({
                    'amendment_number': amendment_num,
                    'year': year,
                    'page': page['page_number'],
                    'context': text[match.start():match.end()+100]  # Context around match
                })
        
        return amendments
    
    def _create_article_index(self, articles: List[ConstitutionalArticle]) -> Dict[str, Any]:
        """Create an index of articles by number"""
        index = {}
        
        for article in articles:
            index[article.article_number] = {
                'title': article.title,
                'chapter': article.chapter,
                'page': article.page_number,
                'summary': article.simplified_summary,
                'rights_count': len(article.rights_guaranteed),
                'obligations_count': len(article.obligations)
            }
        
        return index
    
    def _create_chapter_index(self, structure: ConstitutionStructure, 
                            articles: List[ConstitutionalArticle]) -> Dict[str, Any]:
        """Create an index of chapters with their articles"""
        chapter_index = {}
        
        for chapter_num, chapter_data in structure.chapters.items():
            chapter_articles = [a for a in articles if a.chapter == chapter_num]
            
            chapter_index[chapter_num] = {
                'title': chapter_data['title'],
                'page': chapter_data['page'],
                'article_count': len(chapter_articles),
                'articles': [a.article_number for a in chapter_articles]
            }
        
        return chapter_index
    
    def _create_rights_index(self, articles: List[ConstitutionalArticle]) -> Dict[str, List[str]]:
        """Create an index of rights by type"""
        rights_index = {
            'economic_social': [],
            'civil_political': [],
            'procedural': [],
            'group_rights': []
        }
        
        economic_keywords = ['health', 'food', 'water', 'housing', 'education', 'social security', 'work']
        civil_keywords = ['speech', 'assembly', 'religion', 'privacy', 'life', 'dignity']
        procedural_keywords = ['fair trial', 'arrest', 'detention', 'justice', 'hearing']
        group_keywords = ['children', 'women', 'disabled', 'youth', 'minorities', 'older']
        
        for article in articles:
            for right in article.rights_guaranteed:
                right_lower = right.lower()
                
                # Categorize the right
                if any(keyword in right_lower for keyword in economic_keywords):
                    rights_index['economic_social'].append(f"Article {article.article_number}: {right}")
                elif any(keyword in right_lower for keyword in civil_keywords):
                    rights_index['civil_political'].append(f"Article {article.article_number}: {right}")
                elif any(keyword in right_lower for keyword in procedural_keywords):
                    rights_index['procedural'].append(f"Article {article.article_number}: {right}")
                elif any(keyword in right_lower for keyword in group_keywords):
                    rights_index['group_rights'].append(f"Article {article.article_number}: {right}")
        
        return rights_index
    
    def get_article_by_number(self, article_num: str, articles: List[ConstitutionalArticle]) -> Optional[ConstitutionalArticle]:
        """Get a specific article by number"""
        for article in articles:
            if article.article_number == article_num:
                return article
        return None
    
    def search_articles(self, search_term: str, articles: List[ConstitutionalArticle]) -> List[ConstitutionalArticle]:
        """Search articles by text content"""
        results = []
        search_term_lower = search_term.lower()
        
        for article in articles:
            if (search_term_lower in article.full_text.lower() or 
                search_term_lower in article.title.lower() or
                search_term_lower in article.simplified_summary.lower()):
                results.append(article)
        
        return results
    
    def export_to_json(self, constitution_data: Dict[str, Any], output_path: str):
        """Export constitution data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(constitution_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Constitution data exported to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            raise
    
    def export_to_sqlite(self, constitution_data: Dict[str, Any], db_path: str):
        """Export constitution data to SQLite database"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_number TEXT UNIQUE,
                    title TEXT,
                    full_text TEXT,
                    chapter TEXT,
                    part TEXT,
                    page_number INTEGER,
                    simplified_summary TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_number TEXT,
                    right_text TEXT,
                    FOREIGN KEY (article_number) REFERENCES articles (article_number)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS obligations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_number TEXT,
                    obligation_text TEXT,
                    FOREIGN KEY (article_number) REFERENCES articles (article_number)
                )
            ''')
            
            # Insert data
            for article_dict in constitution_data['articles']:
                cursor.execute('''
                    INSERT OR REPLACE INTO articles 
                    (article_number, title, full_text, chapter, part, page_number, simplified_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article_dict['article_number'],
                    article_dict['title'],
                    article_dict['full_text'],
                    article_dict['chapter'],
                    article_dict['part'],
                    article_dict['page_number'],
                    article_dict['simplified_summary']
                ))
                
                # Insert rights
                for right in article_dict['rights_guaranteed']:
                    cursor.execute('''
                        INSERT INTO rights (article_number, right_text)
                        VALUES (?, ?)
                    ''', (article_dict['article_number'], right))
                
                # Insert obligations
                for obligation in article_dict['obligations']:
                    cursor.execute('''
                        INSERT INTO obligations (article_number, obligation_text)
                        VALUES (?, ?)
                    ''', (article_dict['article_number'], obligation))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Constitution data exported to SQLite database: {db_path}")
            
        except ImportError:
            self.logger.warning("SQLite not available. Skipping database export.")
        except Exception as e:
            self.logger.error(f"Error exporting to SQLite: {str(e)}")
            raise

# Utility function for standalone usage
def extract_constitution(pdf_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Standalone function to extract constitution data
    
    Args:
        pdf_path: Path to Constitution PDF
        output_dir: Optional directory to save outputs
        
    Returns:
        Extracted constitution data
    """
    extractor = ConstitutionExtractor()
    result = extractor.extract(pdf_path)
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Export to JSON
        json_path = output_path / 'constitution_extracted.json'
        extractor.export_to_json(result, str(json_path))
        
        # Export to SQLite if possible
        try:
            db_path = output_path / 'constitution.db'
            extractor.export_to_sqlite(result, str(db_path))
        except:
            pass  # SQLite export is optional
    
    return result

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"Extracting constitution from: {pdf_path}")
        data = extract_constitution(pdf_path, output_dir)
        
        print(f"\nExtraction complete!")
        print(f"Total articles extracted: {len(data['articles'])}")
        print(f"Total pages processed: {data['metadata']['total_pages']}")
        
        if output_dir:
            print(f"Output saved to: {output_dir}")
    else:
        print("Usage: python constitution_extractor.py <pdf_path> [output_dir]")