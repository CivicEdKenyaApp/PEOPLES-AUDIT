# validators/constitutional_validator.py
import json
import re
from typing import Dict, List, Any
from pathlib import Path
import logging

class ConstitutionalValidator:
    def __init__(self, stage1_dir: Path, constitution_data_path: Path):
        self.stage1_dir = stage1_dir
        self.constitution_data_path = constitution_data_path
        self.logger = logging.getLogger(__name__)
        self.constitution_data = self.load_constitution_data()
    
    def load_constitution_data(self) -> Dict:
        """Load extracted constitution data"""
        try:
            with open(self.constitution_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load constitution data: {str(e)}")
            return {}
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all constitutional references"""
        self.logger.info("Starting constitutional validation")
        
        validation_results = {
            'detailed': {},
            'summary': {},
            'guide': ''
        }
        
        try:
            # Load references from stage 1
            references_path = self.stage1_dir / 'references.json'
            if references_path.exists():
                with open(references_path, 'r', encoding='utf-8') as f:
                    references_data = json.load(f)
                
                # Validate each article reference
                validation_results['detailed'] = self.validate_articles(references_data)
                
                # Generate summary
                validation_results['summary'] = self.generate_summary(validation_results['detailed'])
                
                # Generate citizen guide
                validation_results['guide'] = self.generate_citizen_guide(validation_results['detailed'])
            
            self.logger.info("Constitutional validation completed")
            
        except Exception as e:
            self.logger.error(f"Error in constitutional validation: {str(e)}")
            raise
        
        return validation_results
    
    def validate_articles(self, references_data: Dict) -> Dict:
        """Validate each constitutional article reference"""
        validated_articles = {}
        
        # Extract article references
        article_references = self.extract_article_references(references_data)
        
        for article_num, references in article_references.items():
            # Get article text from constitution
            article_text = self.get_article_text(article_num)
            
            if article_text:
                # Validate each reference
                validations = []
                for ref in references:
                    validation = self.validate_reference(ref, article_text)
                    validations.append(validation)
                
                # Overall assessment
                overall_status = self.assess_overall_status(validations)
                
                validated_articles[article_num] = {
                    'article_number': article_num,
                    'article_text': article_text[:500] + '...',  # Truncated
                    'references': references,
                    'validations': validations,
                    'overall_status': overall_status,
                    'violation_count': sum(1 for v in validations if v['is_violation'])
                }
        
        return validated_articles
    
    def extract_article_references(self, references_data: Dict) -> Dict[str, List]:
        """Extract article references from data"""
        article_references = {}
        
        # Navigate through references data structure
        for page_key, page_data in references_data.items():
            if isinstance(page_data, dict):
                # Check for constitutional articles in various possible fields
                articles = []
                
                if 'constitutional_articles' in page_data:
                    articles.extend(page_data['constitutional_articles'])
                
                if 'articles' in page_data:
                    articles.extend(page_data['articles'])
                
                # Extract from text if present
                if 'text' in page_data:
                    text_articles = re.findall(r'Article\s*(\d+(?:[a-z])?)', page_data['text'])
                    articles.extend(text_articles)
                
                # Add to collection
                for article in articles:
                    if article not in article_references:
                        article_references[article] = []
                    
                    article_references[article].append({
                        'page': page_key,
                        'context': page_data.get('text', '')[:200] if isinstance(page_data, dict) else str(page_data)[:200]
                    })
        
        return article_references
    
    def get_article_text(self, article_num: str) -> str:
        """Get article text from constitution data"""
        # Try different key formats
        possible_keys = [
            f"Article_{article_num}",
            f"article_{article_num}",
            article_num
        ]
        
        for key in possible_keys:
            if key in self.constitution_data:
                article_data = self.constitution_data[key]
                if isinstance(article_data, dict):
                    return article_data.get('full_text', '')
                elif isinstance(article_data, str):
                    return article_data
        
        self.logger.warning(f"Article {article_num} not found in constitution data")
        return ""
    
    def validate_reference(self, reference: Dict, article_text: str) -> Dict:
        """Validate a single reference against article text"""
        context = reference.get('context', '').lower()
        
        # Check for violation indicators
        violation_indicators = [
            'violat', 'breach', 'fail', 'deny', 'ignore',
            'disregard', 'not implement', 'not fulfill',
            'lack of', 'absence of', 'contrary to'
        ]
        
        is_violation = any(indicator in context for indicator in violation_indicators)
        
        # Check for compliance indicators
        compliance_indicators = [
            'comply', 'implement', 'fulfill', 'respect',
            'uphold', 'honor', 'accordance with'
        ]
        
        is_compliant = any(indicator in context for indicator in compliance_indicators)
        
        # Determine status
        if is_violation:
            status = 'violation'
        elif is_compliant:
            status = 'compliant'
        else:
            status = 'reference'
        
        return {
            'page': reference.get('page'),
            'context': reference.get('context', ''),
            'is_violation': is_violation,
            'is_compliant': is_compliant,
            'status': status,
            'violation_indicators': [ind for ind in violation_indicators if ind in context],
            'compliance_indicators': [ind for ind in compliance_indicators if ind in context]
        }
    
    def assess_overall_status(self, validations: List[Dict]) -> str:
        """Assess overall status for an article"""
        violation_count = sum(1 for v in validations if v['is_violation'])
        compliance_count = sum(1 for v in validations if v['is_compliant'])
        
        if violation_count > compliance_count:
            return 'mostly_violated'
        elif compliance_count > violation_count:
            return 'mostly_complied'
        elif violation_count > 0:
            return 'mixed_violations'
        elif compliance_count > 0:
            return 'mixed_compliance'
        else:
            return 'referenced_only'
    
    def generate_summary(self, validated_articles: Dict) -> Dict:
        """Generate summary statistics"""
        total_articles = len(validated_articles)
        violated_articles = sum(1 for a in validated_articles.values() 
                              if a['overall_status'] in ['mostly_violated', 'mixed_violations'])
        complied_articles = sum(1 for a in validated_articles.values() 
                              if a['overall_status'] in ['mostly_complied', 'mixed_compliance'])
        
        total_violations = sum(a['violation_count'] for a in validated_articles.values())
        
        # Most violated articles
        most_violated = sorted(
            [(num, data['violation_count']) for num, data in validated_articles.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_articles_referenced': total_articles,
            'articles_with_violations': violated_articles,
            'articles_with_compliance': complied_articles,
            'total_violation_instances': total_violations,
            'most_violated_articles': most_violated,
            'violation_rate': (violated_articles / total_articles * 100) if total_articles > 0 else 0
        }
    
    def generate_citizen_guide(self, validated_articles: Dict) -> str:
        """Generate citizen-friendly constitutional guide"""
        guide = "YOUR CONSTITUTIONAL RIGHTS: What They Promise vs. What You Get\n"
        guide += "=" * 80 + "\n\n"
        
        guide += "INTRODUCTION\n"
        guide += "The Constitution of Kenya (2010) is your contract with the government. "
        guide += "It lists what the government must do for you and what rights you have. "
        guide += "This guide shows you which parts of the Constitution are being violated.\n\n"
        
        guide += "KEY FINDINGS\n"
        summary = self.generate_summary(validated_articles)
        guide += f"- {summary['total_articles_referenced']} constitutional articles were referenced in the audit\n"
        guide += f"- {summary['articles_with_violations']} articles show evidence of violation\n"
        guide += f"- {summary['total_violation_instances']} specific violations were documented\n\n"
        
        guide += "MOST VIOLATED RIGHTS\n"
        guide += "=" * 80 + "\n\n"
        
        # Add details for top violated articles
        most_violated = sorted(
            [(num, data) for num, data in validated_articles.items() 
             if data['violation_count'] > 0],
            key=lambda x: x[1]['violation_count'],
            reverse=True
        )[:15]
        
        for article_num, article_data in most_violated:
            guide += f"ARTICLE {article_num}\n"
            guide += "-" * 40 + "\n"
            
            # Add simplified explanation
            simple_exp = self.get_simple_explanation(article_num)
            guide += f"What it means: {simple_exp}\n\n"
            
            # Add violation examples
            violation_examples = [v for v in article_data['validations'] if v['is_violation']]
            if violation_examples:
                guide += "How it's being violated:\n"
                for i, violation in enumerate(violation_examples[:3], 1):  # Top 3 examples
                    guide += f"{i}. {violation['context'][:150]}...\n"
                guide += "\n"
            
            guide += f"Total violations found: {article_data['violation_count']}\n\n"
        
        guide += "WHAT YOU CAN DO\n"
        guide += "=" * 80 + "\n\n"
        guide += "1. KNOW YOUR RIGHTS: The Constitution belongs to you\n"
        guide += "2. DEMAND INFORMATION: Use Article 35 to request documents\n"
        guide += "3. REPORT VIOLATIONS: File complaints with EACC and KNCHR\n"
        guide += "4. PARTICIPATE: Attend county budget forums\n"
        guide += "5. ORGANIZE: Join with others to demand accountability\n\n"
        
        guide += "Remember: Sovereignty belongs to you (Article 1). Use it.\n\n"
        
        guide += "Generated from the People's Audit analysis\n"
        guide += f"Date: {self.get_current_date()}\n"
        
        return guide
    
    def get_simple_explanation(self, article_num: str) -> str:
        """Get simple explanation of constitutional article"""
        explanations = {
            '1': "All power belongs to the people of Kenya. Government gets authority from you.",
            '10': "Lists the values that should guide government: honesty, fairness, participation.",
            '35': "You have the right to get information from the government. They must give you documents when you ask.",
            '43': "You have rights to healthcare, food, water, housing, education, and social security.",
            '201': "Government money must be managed openly, with public participation, and fairly.",
            '73': "Public officials must act with integrity. Authority is a public trust, not for private gain.",
            '229': "Public jobs must be given based on merit, not connections."
        }
        
        # Clean article number (remove parentheses etc.)
        clean_num = re.sub(r'\(.*?\)', '', article_num).strip()
        
        return explanations.get(clean_num, f"Article {article_num} of the Constitution")
    
    def get_current_date(self) -> str:
        """Get current date in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")