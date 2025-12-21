# processors/semantic_tagger.py
import json
import re
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class TaggedParagraph:
    paragraph_id: str
    text: str
    tags: List[str]
    category: str
    confidence: float
    page_number: int
    metadata: Dict[str, Any]

class SemanticTagger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define tagging rules
        self.tag_keywords = {
            'finding': [
                'found that', 'discovered', 'revealed', 'identified',
                'shows that', 'indicates', 'demonstrates', 'evidence shows'
            ],
            'recommendation': [
                'recommend', 'should', 'must', 'need to', 'propose',
                'suggest', 'advise', 'call for', 'urge'
            ],
            'allegation': [
                'alleged', 'accused', 'claimed', 'reportedly',
                'suspected', 'under investigation', 'scandal'
            ],
            'statistic': [
                'percent', 'percentage', 'KSh', 'billion', 'million',
                'trillion', 'increased by', 'decreased by', 'growth of'
            ],
            'legal_reference': [
                'Article', 'Section', 'Act', 'Constitution',
                'law', 'regulation', 'statute'
            ],
            'corruption': [
                'corruption', 'embezzlement', 'fraud', 'theft',
                'bribery', 'kickback', 'misappropriation'
            ],
            'debt': [
                'debt', 'loan', 'borrowing', 'credit',
                'interest', 'repayment', 'default'
            ],
            'human_rights': [
                'right to', 'human rights', 'freedom',
                'dignity', 'equality', 'justice'
            ]
        }
        
        # Define classification patterns
        self.classification_patterns = {
            'finding': r'(?:The (?:study|audit|report) (?:found|identified|revealed)|It was (?:found|discovered)|Evidence shows)',
            'recommendation': r'(?:We recommend|It is recommended|The report recommends|Should|Must)',
            'fact': r'(?:According to|Data shows|Statistics indicate|Figures show)',
            'analysis': r'(?:This suggests|This indicates|Therefore|Thus|Consequently)'
        }
    
    def process_all(self, raw_text_data: Dict) -> Dict[str, Any]:
        """Process all paragraphs from raw text data"""
        self.logger.info("Starting semantic tagging process")
        
        results = {
            'paragraphs': [],
            'recommendations': [],
            'findings': [],
            'timeline': [],
            'statistics': [],
            'violations': []
        }
        
        try:
            paragraph_id = 0
            
            for page_key, page_data in raw_text_data.items():
                page_num = int(page_key.split('_')[1])
                paragraphs = page_data.get('paragraphs', [])
                
                for para_text in paragraphs:
                    if len(para_text.strip()) < 10:  # Skip very short paragraphs
                        continue
                    
                    paragraph_id += 1
                    tagged_para = self.tag_paragraph(para_text, paragraph_id, page_num)
                    
                    # Add to results
                    results['paragraphs'].append(asdict(tagged_para))
                    
                    # Categorize further
                    self.categorize_paragraph(tagged_para, results)
            
            self.logger.info(f"Processed {paragraph_id} paragraphs")
            
            # Post-process results
            self.post_process_results(results)
            
        except Exception as e:
            self.logger.error(f"Error in semantic tagging: {str(e)}")
            raise
        
        return results
    
    def tag_paragraph(self, text: str, para_id: int, page_num: int) -> TaggedParagraph:
        """Tag a single paragraph"""
        # Clean text
        clean_text = self.clean_text(text)
        
        # Initialize tags
        tags = []
        
        # Apply keyword tagging
        for tag, keywords in self.tag_keywords.items():
            for keyword in keywords:
                if keyword.lower() in clean_text.lower():
                    tags.append(tag)
                    break  # Found one keyword, move to next tag
        
        # Determine category
        category = self.determine_category(clean_text, tags)
        
        # Calculate confidence
        confidence = self.calculate_confidence(clean_text, tags, category)
        
        # Extract metadata
        metadata = self.extract_metadata(clean_text)
        
        return TaggedParagraph(
            paragraph_id=f"para_{para_id:06d}",
            text=clean_text,
            tags=list(set(tags)),  # Remove duplicates
            category=category,
            confidence=confidence,
            page_number=page_num,
            metadata=metadata
        )
    
    def determine_category(self, text: str, tags: List[str]) -> str:
        """Determine the primary category of a paragraph"""
        text_lower = text.lower()
        
        # Check for recommendations
        if any(word in text_lower for word in ['should', 'must', 'recommend', 'propose', 'urge']):
            return 'recommendation'
        
        # Check for findings
        if any(word in text_lower for word in ['found', 'discovered', 'revealed', 'identified']):
            return 'finding'
        
        # Check for allegations
        if any(word in text_lower for word in ['alleged', 'accused', 'scandal', 'fraud']):
            return 'allegation'
        
        # Check for statistics
        if any(word in text_lower for word in ['percent', 'KSh', 'billion', 'million', 'data']):
            return 'statistic'
        
        # Check for legal references
        if 'Article' in text or 'Section' in text or 'Act' in text:
            return 'legal_reference'
        
        # Default category
        if tags:
            return tags[0]  # Use first tag as category
        
        return 'narrative'
    
    def calculate_confidence(self, text: str, tags: List[str], category: str) -> float:
        """Calculate confidence score for tagging"""
        confidence = 0.0
        
        # Base confidence from number of tags
        if tags:
            confidence += min(len(tags) * 0.2, 0.6)
        
        # Category match boost
        if category in tags:
            confidence += 0.2
        
        # Length-based confidence (longer paragraphs are more likely to be correctly tagged)
        if len(text) > 100:
            confidence += 0.1
        
        # Keyword density boost
        keyword_count = sum(1 for tag in tags for keyword in self.tag_keywords.get(tag, []) 
                          if keyword.lower() in text.lower())
        if keyword_count > 0:
            confidence += min(keyword_count * 0.05, 0.2)
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from paragraph text"""
        metadata = {
            'has_monetary_value': False,
            'has_percentage': False,
            'has_year': False,
            'has_article': False,
            'has_institution': False,
            'word_count': len(text.split())
        }
        
        # Check for monetary values
        monetary_pattern = r'KSh\s*([\d,]+(?:\.\d+)?)\s*(?:billion|million|trillion)?'
        if re.search(monetary_pattern, text, re.IGNORECASE):
            metadata['has_monetary_value'] = True
        
        # Check for percentages
        if re.search(r'\d+(?:\.\d+)?\s*%', text):
            metadata['has_percentage'] = True
        
        # Check for years
        if re.search(r'\b(?:19|20)\d{2}\b', text):
            metadata['has_year'] = True
        
        # Check for constitutional articles
        if re.search(r'Article\s*\d+', text):
            metadata['has_article'] = True
        
        # Check for institutions
        institutions = ['Treasury', 'Parliament', 'County', 'EACC', 'OAG', 'CoB', 'IMF', 'World Bank']
        if any(inst.lower() in text.lower() for inst in institutions):
            metadata['has_institution'] = True
        
        return metadata
    
    def categorize_paragraph(self, paragraph: TaggedParagraph, results: Dict):
        """Categorize paragraph into specific result categories"""
        
        # Add to recommendations
        if paragraph.category == 'recommendation':
            results['recommendations'].append({
                'id': paragraph.paragraph_id,
                'text': paragraph.text,
                'page': paragraph.page_number,
                'tags': paragraph.tags,
                'priority': self.determine_recommendation_priority(paragraph.text)
            })
        
        # Add to findings
        elif paragraph.category == 'finding':
            results['findings'].append({
                'id': paragraph.paragraph_id,
                'text': paragraph.text,
                'page': paragraph.page_number,
                'tags': paragraph.tags,
                'severity': self.determine_finding_severity(paragraph.text)
            })
        
        # Add to timeline if contains year
        if paragraph.metadata.get('has_year'):
            year_match = re.search(r'\b(?:19|20)(\d{2})\b', paragraph.text)
            if year_match:
                results['timeline'].append({
                    'id': paragraph.paragraph_id,
                    'year': f"20{year_match.group(1)}" if year_match.group(1).startswith('0') 
                          else f"19{year_match.group(1)}" if int(year_match.group(1)) > 50
                          else f"20{year_match.group(1)}",
                    'text': paragraph.text[:200],  # Truncate
                    'page': paragraph.page_number,
                    'category': paragraph.category
                })
        
        # Add to statistics if contains numbers
        if paragraph.metadata.get('has_monetary_value') or paragraph.metadata.get('has_percentage'):
            results['statistics'].append({
                'id': paragraph.paragraph_id,
                'text': paragraph.text,
                'page': paragraph.page_number,
                'has_monetary': paragraph.metadata['has_monetary_value'],
                'has_percentage': paragraph.metadata['has_percentage']
            })
        
        # Add to violations if contains legal references and negative context
        if paragraph.metadata.get('has_article'):
            negative_words = ['violat', 'breach', 'fail', 'deny', 'ignore', 'disregard']
            if any(word in paragraph.text.lower() for word in negative_words):
                results['violations'].append({
                    'id': paragraph.paragraph_id,
                    'text': paragraph.text,
                    'page': paragraph.page_number,
                    'article': self.extract_article_number(paragraph.text)
                })
    
    def determine_recommendation_priority(self, text: str) -> str:
        """Determine priority level of recommendation"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['immediately', 'urgent', 'without delay', 'asap']):
            return 'high'
        elif any(word in text_lower for word in ['should', 'must', 'need to']):
            return 'medium'
        else:
            return 'low'
    
    def determine_finding_severity(self, text: str) -> str:
        """Determine severity of finding"""
        text_lower = text.lower()
        
        severe_words = ['critical', 'severe', 'serious', 'grave', 'alarming', 'crisis']
        moderate_words = ['significant', 'considerable', 'substantial', 'notable']
        
        if any(word in text_lower for word in severe_words):
            return 'high'
        elif any(word in text_lower for word in moderate_words):
            return 'medium'
        else:
            return 'low'
    
    def extract_article_number(self, text: str) -> str:
        """Extract article number from text"""
        article_match = re.search(r'Article\s*(\d+(?:[a-z])?)', text, re.IGNORECASE)
        return article_match.group(1) if article_match else None
    
    def post_process_results(self, results: Dict):
        """Post-process and deduplicate results"""
        
        # Remove duplicate recommendations
        unique_recommendations = []
        seen_recommendations = set()
        
        for rec in results['recommendations']:
            rec_hash = hash(rec['text'][:100])  # Hash first 100 chars
            if rec_hash not in seen_recommendations:
                seen_recommendations.add(rec_hash)
                unique_recommendations.append(rec)
        
        results['recommendations'] = unique_recommendations
        
        # Sort timeline by year
        results['timeline'] = sorted(results['timeline'], key=lambda x: x['year'])
        
        # Group findings by tag
        findings_by_tag = {}
        for finding in results['findings']:
            for tag in finding['tags']:
                if tag not in findings_by_tag:
                    findings_by_tag[tag] = []
                findings_by_tag[tag].append(finding)
        
        results['findings_by_tag'] = findings_by_tag
    
    def clean_text(self, text: str) -> str:
        """Clean text for processing"""
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s.,;:!?\'"-]', ' ', text)
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()