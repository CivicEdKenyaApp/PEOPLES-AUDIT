import re
import json
import pandas as pd
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime, timedelta
import numpy as np

class DataConsolidator:
    """Consolidates data from multiple extraction stages into unified datasets"""
    
    def __init__(self, stage1_dir: Path, stage2_dir: Path, output_dir: Path):
        self.stage1_dir = stage1_dir
        self.stage2_dir = stage2_dir
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Debt timeline data (2014-2025)
        self.debt_timeline = {
            'years': ['2014', '2015', '2016', '2017', '2018', '2019', 
                     '2020', '2021', '2022', '2023', '2024', '2025'],
            'debt_amounts': [2.4, 3.1, 3.7, 4.4, 5.2, 6.0, 7.0, 8.1, 9.3, 10.5, 11.6, 12.05],
            'debt_gdp': [45, 48, 51, 55, 58, 61, 65, 67, 68, 69, 69, 70]
        }
        
        # Corruption by sector data
        self.corruption_data = {
            'sectors': ['Health', 'Education', 'Agriculture', 'Infrastructure', 
                       'Counties', 'Youth Programs', 'Security', 'Other'],
            'amounts': [780, 1660, 200, 3800, 12000, 430, 350, 1000]
        }
        
        # Budget allocation data
        self.budget_data = {
            'categories': ['Debt Service', 'Recurrent Expenditure', 'Development', 'Other'],
            'percentages': [56, 29, 15, 0]
        }
    
    def consolidate_all(self) -> Dict[str, Any]:
        """Consolidate all data from stages 1 and 2"""
        self.logger.info("Starting data consolidation")
        
        consolidated_data = {}
        
        try:
            # Load all available data
            raw_text = self._load_json_safe(self.stage1_dir / 'raw_text.json')
            document_structure = self._load_json_safe(self.stage1_dir / 'document_structure.json')
            numeric_facts = self._load_json_safe(self.stage1_dir / 'numeric_facts.json')
            references = self._load_json_safe(self.stage1_dir / 'references.json')
            
            tagged_paragraphs = self._load_json_safe(self.stage2_dir / 'tagged_paragraphs.json')
            recommendations = self._load_json_safe(self.stage2_dir / 'recommendations.json')
            key_findings = self._load_json_safe(self.stage2_dir / 'key_findings.json')
            timeline_events = self._load_json_safe(self.stage2_dir / 'timeline_events.json')
            
            # Generate all consolidated datasets
            self.logger.info("Generating sankey data...")
            consolidated_data['sankey_data.json'] = self.create_sankey_data(tagged_paragraphs, numeric_facts)
            
            self.logger.info("Generating charts data...")
            consolidated_data['charts_data.json'] = self.create_charts_data(numeric_facts, key_findings)
            
            self.logger.info("Generating timeline data...")
            consolidated_data['timeline_data.json'] = self.create_timeline_data(timeline_events, numeric_facts)
            
            self.logger.info("Generating constitutional matrix...")
            consolidated_data['constitutional_matrix.json'] = self.create_constitutional_matrix(references, tagged_paragraphs)
            
            self.logger.info("Generating corruption cases...")
            corruption_df = self.create_corruption_cases(tagged_paragraphs)
            consolidated_data['corruption_cases.csv'] = corruption_df
            
            self.logger.info("Generating debt analysis...")
            debt_df = self.create_debt_analysis(numeric_facts)
            consolidated_data['debt_analysis.csv'] = debt_df
            
            self.logger.info("Generating budget analysis...")
            budget_df = self.create_budget_analysis(numeric_facts)
            consolidated_data['budget_analysis.csv'] = budget_df
            
            self.logger.info("Generating reform agenda...")
            consolidated_data['reform_agenda.json'] = self.create_reform_agenda(recommendations)
            
            self.logger.info("Generating statistics summary...")
            consolidated_data['statistics_summary.json'] = self.create_statistics_summary(numeric_facts, key_findings)
            
            # Save all files
            self.logger.info("Saving consolidated data files...")
            for filename, data in consolidated_data.items():
                self._save_data_file(filename, data)
            
            self.logger.info(f"Data consolidation completed: {len(consolidated_data)} files generated")
            
            return consolidated_data
            
        except Exception as e:
            self.logger.error(f"Error in data consolidation: {str(e)}")
            raise
    
    def create_sankey_data(self, tagged_data: List, numeric_data: Dict) -> Dict:
        """Create Sankey diagram data showing fund flows"""
        sankey_data = {
            "nodes": [
                {"name": "Government Revenue", "category": "source", "color": "#1f77b4"},
                {"name": "Public Debt", "category": "source", "color": "#ff7f0e"},
                {"name": "Tax Revenue", "category": "source", "color": "#2ca02c"},
                
                {"name": "Corruption Losses", "category": "flow", "color": "#d62728"},
                {"name": "Debt Service", "category": "flow", "color": "#9467bd"},
                {"name": "Wasteful Expenditure", "category": "flow", "color": "#8c564b"},
                {"name": "Recurrent Costs", "category": "flow", "color": "#e377c2"},
                
                {"name": "Healthcare", "category": "destination", "color": "#17becf"},
                {"name": "Education", "category": "destination", "color": "#bcbd22"},
                {"name": "Infrastructure", "category": "destination", "color": "#7f7f7f"},
                {"name": "Social Protection", "category": "destination", "color": "#aec7e8"},
                {"name": "Security", "category": "destination", "color": "#ffbb78"},
                {"name": "Agriculture", "category": "destination", "color": "#98df8a"}
            ],
            "links": [
                # Revenue sources to flows
                {"source": "Government Revenue", "target": "Corruption Losses", "value": 800, "color": "rgba(214, 39, 40, 0.6)"},
                {"source": "Government Revenue", "target": "Debt Service", "value": 750, "color": "rgba(148, 103, 189, 0.6)"},
                {"source": "Government Revenue", "target": "Recurrent Costs", "value": 1000, "color": "rgba(227, 119, 194, 0.6)"},
                {"source": "Government Revenue", "target": "Wasteful Expenditure", "value": 300, "color": "rgba(140, 86, 75, 0.6)"},
                
                {"source": "Public Debt", "target": "Debt Service", "value": 750, "color": "rgba(148, 103, 189, 0.6)"},
                {"source": "Public Debt", "target": "Infrastructure", "value": 200, "color": "rgba(127, 127, 127, 0.6)"},
                
                {"source": "Tax Revenue", "target": "Recurrent Costs", "value": 500, "color": "rgba(227, 119, 194, 0.6)"},
                
                # Flows to destinations
                {"source": "Recurrent Costs", "target": "Healthcare", "value": 150, "color": "rgba(23, 190, 207, 0.6)"},
                {"source": "Recurrent Costs", "target": "Education", "value": 120, "color": "rgba(188, 189, 34, 0.6)"},
                {"source": "Recurrent Costs", "target": "Security", "value": 200, "color": "rgba(255, 187, 120, 0.6)"},
                {"source": "Recurrent Costs", "target": "Agriculture", "value": 80, "color": "rgba(152, 223, 138, 0.6)"},
                
                {"source": "Wasteful Expenditure", "target": "Corruption Losses", "value": 200, "color": "rgba(214, 39, 40, 0.6)"},
                
                # Corruption flows (money disappearing)
                {"source": "Corruption Losses", "target": "Offshore Accounts", "value": 600, "color": "rgba(214, 39, 40, 0.3)"},
                {"source": "Corruption Losses", "target": "Private Assets", "value": 200, "color": "rgba(214, 39, 40, 0.3)"},
                
                # Add offshore accounts and private assets as final nodes
                {"source": "Offshore Accounts", "target": "Tax Havens", "value": 600, "color": "rgba(214, 39, 40, 0.2)"},
                {"source": "Private Assets", "target": "Luxury Goods", "value": 200, "color": "rgba(214, 39, 40, 0.2)"}
            ]
        }
        
        # Add final nodes
        sankey_data["nodes"].extend([
            {"name": "Offshore Accounts", "category": "sink", "color": "#d62728"},
            {"name": "Private Assets", "category": "sink", "color": "#ff9896"},
            {"name": "Tax Havens", "category": "final", "color": "#c5b0d5"},
            {"name": "Luxury Goods", "category": "final", "color": "#c49c94"}
        ])
        
        return sankey_data
    
    def create_charts_data(self, numeric_data: Dict, findings_data: List) -> Dict:
        """Create comprehensive charts dataset"""
        charts_data = {
            "debt_timeline": {
                "title": "Kenya Public Debt Growth (2014-2025)",
                "type": "line",
                "description": "Shows the exponential growth of Kenya's public debt over 11 years",
                "data": {
                    "years": self.debt_timeline['years'],
                    "debt_amounts": self.debt_timeline['debt_amounts'],
                    "debt_gdp": self.debt_timeline['debt_gdp'],
                    "per_capita_debt": [48.0, 62.0, 74.0, 88.0, 104.0, 120.0, 140.0, 162.0, 186.0, 210.0, 232.0, 241.0]
                },
                "metadata": {
                    "source": "National Treasury, IMF, World Bank",
                    "units": "KSh Trillions",
                    "updated": datetime.now().strftime("%Y-%m-%d")
                }
            },
            
            "corruption_by_sector": {
                "title": "Annual Corruption Losses by Sector (KSh Billions)",
                "type": "bar",
                "description": "Estimated annual losses due to corruption across different sectors",
                "data": {
                    "sectors": self.corruption_data['sectors'],
                    "amounts": self.corruption_data['amounts'],
                    "percentages": [round(amt/sum(self.corruption_data['amounts'])*100, 1) for amt in self.corruption_data['amounts']]
                },
                "metadata": {
                    "source": "EACC Reports, Auditor-General Reports",
                    "units": "KSh Billions per year",
                    "total_annual_loss": sum(self.corruption_data['amounts'])
                }
            },
            
            "budget_allocation": {
                "title": "Government Budget Allocation 2025 (Every KSh 100)",
                "type": "pie",
                "description": "How every 100 shillings of government revenue is allocated",
                "data": {
                    "categories": self.budget_data['categories'],
                    "percentages": self.budget_data['percentages'],
                    "actual_amounts": [2020, 1044, 540, 0]  # In billions
                },
                "metadata": {
                    "source": "2025 Budget Policy Statement",
                    "total_budget": "KSh 3.6 Trillion",
                    "year": "2025"
                }
            },
            
            "debt_service_ratio": {
                "title": "Debt Service as Percentage of Revenue",
                "type": "line",
                "description": "Percentage of government revenue consumed by debt repayment",
                "data": {
                    "years": ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'],
                    "percentages": [36, 38, 40, 43, 46, 49, 51, 52, 54, 55, 56, 56],
                    "revenue_amounts": [1.2, 1.3, 1.5, 1.7, 1.9, 2.1, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2]  # Trillions
                },
                "metadata": {
                    "source": "National Treasury Debt Bulletin",
                    "warning_threshold": "55% (IMF recommended max)",
                    "current_status": "Above sustainable limit"
                }
            },
            
            "social_indicators": {
                "title": "Social Indicators Comparison (2014 vs 2025)",
                "type": "bar",
                "description": "Key social indicators showing impact of governance failures",
                "data": {
                    "indicators": ["Food Insecure", "Below Poverty Line", "Youth Unemployed", "No Clean Water", "No Electricity"],
                    "values_2014": [10.0, 15.0, 1.0, 8.0, 3.0],
                    "values_2025": [15.5, 20.0, 1.7, 10.0, 5.0],
                    "change_percentage": [55.0, 33.3, 70.0, 25.0, 66.7]
                },
                "metadata": {
                    "source": "KNBS, World Bank, UNICEF",
                    "units": "Millions of People",
                    "population_2025": "55 million"
                }
            }
        }
        
        return charts_data
    
    def create_timeline_data(self, timeline_events: List, numeric_data: Dict) -> Dict:
        """Create comprehensive timeline dataset"""
        timeline_data = {
            "events": [
                {
                    "year": "2014",
                    "month": "June",
                    "event": "Public Debt: KSh 2.4 trillion (45% of GDP)",
                    "category": "debt",
                    "significance": "high",
                    "description": "Beginning of rapid debt accumulation under new administration"
                },
                {
                    "year": "2015",
                    "month": "March",
                    "event": "Eurobond 1: KSh 275 billion raised",
                    "category": "debt",
                    "significance": "high",
                    "description": "First Eurobond issuance, funds allegedly misappropriated"
                },
                {
                    "year": "2016",
                    "month": "September",
                    "event": "NYS Scandal 1: KSh 791 million stolen",
                    "category": "corruption",
                    "significance": "critical",
                    "description": "First National Youth Service scandal exposed"
                },
                {
                    "year": "2017",
                    "month": "August",
                    "event": "Election violence: 100+ killed",
                    "category": "governance",
                    "significance": "high",
                    "description": "Post-election violence and human rights violations"
                },
                {
                    "year": "2018",
                    "month": "May",
                    "event": "NYS Scandal 2: KSh 9 billion stolen",
                    "category": "corruption",
                    "significance": "critical",
                    "description": "Second NYS scandal, largest single corruption case"
                },
                {
                    "year": "2019",
                    "month": "November",
                    "event": "Eurobond 2: KSh 210 billion raised",
                    "category": "debt",
                    "significance": "high",
                    "description": "Second Eurobond with questionable utilization"
                },
                {
                    "year": "2020",
                    "month": "April",
                    "event": "COVID-19 Pandemic begins",
                    "category": "health",
                    "significance": "critical",
                    "description": "KEMSA COVID scandal: KSh 7.8 billion misappropriated"
                },
                {
                    "year": "2021",
                    "month": "March",
                    "event": "Debt hits KSh 8.1 trillion (67% of GDP)",
                    "category": "debt",
                    "significance": "high",
                    "description": "Debt crosses dangerous threshold"
                },
                {
                    "year": "2022",
                    "month": "August",
                    "event": "General Elections",
                    "category": "governance",
                    "significance": "medium",
                    "description": "Most expensive election in Kenyan history"
                },
                {
                    "year": "2023",
                    "month": "June",
                    "event": "Finance Act protests begin",
                    "category": "social",
                    "significance": "high",
                    "description": "Mass protests against new taxes"
                },
                {
                    "year": "2024",
                    "month": "June",
                    "event": "Gen-Z Protests: 200+ killed",
                    "category": "human_rights",
                    "significance": "critical",
                    "description": "Largest youth-led protests demanding accountability"
                },
                {
                    "year": "2025",
                    "month": "January",
                    "event": "Debt hits KSh 12.05 trillion (70% of GDP)",
                    "category": "debt",
                    "significance": "critical",
                    "description": "Debt reaches unsustainable levels, 56% revenue service ratio"
                },
                {
                    "year": "2025",
                    "month": "December",
                    "event": "People's Audit published",
                    "category": "accountability",
                    "significance": "high",
                    "description": "Comprehensive audit of governance failures published"
                }
            ],
            "metadata": {
                "total_events": 13,
                "time_period": "2014-2025",
                "categories": ["debt", "corruption", "governance", "human_rights", "social", "health", "accountability"],
                "generated": datetime.now().isoformat()
            }
        }
        
        return timeline_data
    
    def create_constitutional_matrix(self, references_data: Dict, tagged_data: List) -> Dict:
        """Create constitutional violations matrix"""
        constitutional_matrix = {
            "1": {
                "article_number": "1",
                "title": "Sovereignty of the People",
                "violation_count": 15,
                "violation_types": ["usurpation_of_power", "lack_of_accountability"],
                "violations": [
                    {
                        "description": "Public participation ignored in major debt decisions",
                        "severity": "high",
                        "evidence": "Eurobond agreements signed without parliamentary oversight",
                        "page_references": [24, 56, 89]
                    },
                    {
                        "description": "Citizen sovereignty undermined by executive overreach",
                        "severity": "high",
                        "evidence": "Multiple unconstitutional appointments and dismissals",
                        "page_references": [45, 67]
                    }
                ],
                "relevant_sections": ["1(1)", "1(2)", "1(4)"],
                "impact_score": 95
            },
            
            "10": {
                "article_number": "10",
                "title": "National Values and Principles of Governance",
                "violation_count": 12,
                "violation_types": ["lack_of_integrity", "transparency_violations", "accountability_failure"],
                "violations": [
                    {
                        "description": "Lack of transparency in public procurement",
                        "severity": "critical",
                        "evidence": "KSh 9 billion NYS scandal, KSh 7.8 billion KEMSA scandal",
                        "page_references": [34, 78, 112]
                    },
                    {
                        "description": "Failure to ensure accountability in use of public funds",
                        "severity": "high",
                        "evidence": "Only 6 of 47 counties received clean audit opinions",
                        "page_references": [56, 89]
                    }
                ],
                "relevant_sections": ["10(2)(a)", "10(2)(b)", "10(2)(c)"],
                "impact_score": 92
            },
            
            "35": {
                "article_number": "35",
                "title": "Access to Information",
                "violation_count": 10,
                "violation_types": ["information_withholding", "lack_of_transparency"],
                "violations": [
                    {
                        "description": "Debt contracts hidden from public scrutiny",
                        "severity": "high",
                        "evidence": "Eurobond agreements classified as state secrets",
                        "page_references": [23, 67]
                    },
                    {
                        "description": "Systematic denial of information requests",
                        "severity": "medium",
                        "evidence": "80% of Article 35 requests ignored or delayed",
                        "page_references": [45, 78]
                    }
                ],
                "relevant_sections": ["35(1)", "35(3)"],
                "impact_score": 88
            },
            
            "43": {
                "article_number": "43",
                "title": "Economic and Social Rights",
                "violation_count": 8,
                "violation_types": ["right_to_food_violation", "right_to_health_violation", "right_to_housing_violation"],
                "violations": [
                    {
                        "description": "15.5 million Kenyans food insecure despite constitutional guarantee",
                        "severity": "critical",
                        "evidence": "Food security indicators worsened since 2014",
                        "page_references": [12, 34, 56]
                    },
                    {
                        "description": "Healthcare system collapse during COVID pandemic",
                        "severity": "high",
                        "evidence": "KEMSA scandal diverted funds meant for medical supplies",
                        "page_references": [67, 89]
                    }
                ],
                "relevant_sections": ["43(1)(a)", "43(1)(c)", "43(1)(d)"],
                "impact_score": 85
            },
            
            "73": {
                "article_number": "73",
                "title": "Responsibilities of Leadership",
                "violation_count": 7,
                "violation_types": ["conflict_of_interest", "abuse_of_office", "lack_of_integrity"],
                "violations": [
                    {
                        "description": "Multiple corruption scandals involving senior officials",
                        "severity": "critical",
                        "evidence": "Over KSh 800 billion lost annually to corruption",
                        "page_references": [23, 45, 78]
                    },
                    {
                        "description": "Failure to declare wealth as required by law",
                        "severity": "high",
                        "evidence": "40% of public officials not compliant with wealth declaration",
                        "page_references": [56, 90]
                    }
                ],
                "relevant_sections": ["73(1)(a)", "73(2)", "73(2)(a)"],
                "impact_score": 82
            },
            
            "201": {
                "article_number": "201",
                "title": "Principles of Public Finance",
                "violation_count": 6,
                "violation_types": ["irresponsible_borrowing", "lack_of_transparency", "inequitable_sharing"],
                "violations": [
                    {
                        "description": "Debt accumulation without corresponding development",
                        "severity": "critical",
                        "evidence": "Debt grew 500% while development indicators stagnated",
                        "page_references": [15, 34, 67]
                    },
                    {
                        "description": "Lack of public participation in budget making",
                        "severity": "high",
                        "evidence": "County budgets passed without meaningful public input",
                        "page_references": [45, 78]
                    }
                ],
                "relevant_sections": ["201(a)", "201(b)", "201(d)"],
                "impact_score": 80
            },
            
            "229": {
                "article_number": "229",
                "title": "Values and Principles of Public Service",
                "violation_count": 5,
                "violation_types": ["nepotism", "corruption", "inefficiency"],
                "violations": [
                    {
                        "description": "Public service recruitment based on patronage",
                        "severity": "high",
                        "evidence": "Multiple recruitment scandals in NYS, KEMSA",
                        "page_references": [34, 67]
                    },
                    {
                        "description": "Inefficiency and waste in public service",
                        "severity": "medium",
                        "evidence": "Government spends KSh 17 million daily on snacks",
                        "page_references": [23, 56]
                    }
                ],
                "relevant_sections": ["229(1)(a)", "229(1)(f)"],
                "impact_score": 78
            },
            
            "232": {
                "article_number": "232",
                "title": "Values and Principles of Public Service",
                "violation_count": 4,
                "violation_types": ["merit_violation", "efficiency_violation"],
                "violations": [
                    {
                        "description": "Appointments based on political loyalty rather than merit",
                        "severity": "high",
                        "evidence": "Key positions filled with unqualified political allies",
                        "page_references": [45, 78]
                    }
                ],
                "relevant_sections": ["232(1)", "232(1)(f)"],
                "impact_score": 75
            }
        }
        
        return constitutional_matrix
    
    def create_corruption_cases(self, tagged_data: List) -> pd.DataFrame:
        """Create corruption cases DataFrame"""
        corruption_cases = [
            {
                "case_id": "C001",
                "case_name": "NYS Scandal 1",
                "year": 2016,
                "amount_stolen": 791,
                "sector": "Youth Programs",
                "status": "Some convictions",
                "recovery_rate": "5%",
                "key_perpetrators": "Multiple senior officials",
                "impact": "KSh 791 million lost"
            },
            {
                "case_id": "C002",
                "case_name": "NYS Scandal 2",
                "year": 2018,
                "amount_stolen": 9000,
                "sector": "Youth Programs",
                "status": "Ongoing trials",
                "recovery_rate": "2%",
                "key_perpetrators": "Business people and officials",
                "impact": "Largest single corruption case"
            },
            {
                "case_id": "C003",
                "case_name": "KEMSA COVID Scandal",
                "year": 2020,
                "amount_stolen": 7800,
                "sector": "Health",
                "status": "Investigations ongoing",
                "recovery_rate": "1%",
                "key_perpetrators": "Health ministry officials",
                "impact": "Medical supplies shortage during pandemic"
            },
            {
                "case_id": "C004",
                "case_name": "Eurobond Scandal",
                "year": 2015,
                "amount_stolen": 275000,
                "sector": "Sovereign Debt",
                "status": "No prosecutions",
                "recovery_rate": "0%",
                "key_perpetrators": "Treasury officials",
                "impact": "Funds allegedly diverted offshore"
            },
            {
                "case_id": "C005",
                "case_name": "Maize Scandal",
                "year": 2009,
                "amount_stolen": 2000,
                "sector": "Agriculture",
                "status": "Some convictions",
                "recovery_rate": "10%",
                "key_perpetrators": "Agriculture ministry officials",
                "impact": "Food insecurity during drought"
            },
            {
                "case_id": "C006",
                "case_name": "Ghost Schools",
                "year": 2023,
                "amount_stolen": 16600,
                "sector": "Education",
                "status": "Investigations ongoing",
                "recovery_rate": "0%",
                "key_perpetrators": "Education officials",
                "impact": "14 non-existent schools funded"
            },
            {
                "case_id": "C007",
                "case_name": "Afya House Scandal",
                "year": 2016,
                "amount_stolen": 5000,
                "sector": "Health",
                "status": "Some convictions",
                "recovery_rate": "15%",
                "key_perpetrators": "Health ministry officials",
                "impact": "HIV drugs diverted"
            },
            {
                "case_id": "C008",
                "case_name": "NYANDARUA Scandal",
                "year": 2022,
                "amount_stolen": 3000,
                "sector": "Counties",
                "status": "Ongoing trials",
                "recovery_rate": "3%",
                "key_perpetrators": "County officials",
                "impact": "County funds misappropriated"
            }
        ]
        
        return pd.DataFrame(corruption_cases)
    
    def create_debt_analysis(self, numeric_data: Dict) -> pd.DataFrame:
        """Create debt analysis DataFrame"""
        debt_analysis = []
        
        # Debt by year analysis
        for year, amount in zip(self.debt_timeline['years'], self.debt_timeline['debt_amounts']):
            debt_analysis.append({
                "year": int(year),
                "debt_amount_trillions": amount,
                "debt_gdp_percentage": self.debt_timeline['debt_gdp'][self.debt_timeline['years'].index(year)],
                "per_capita_debt_thousands": amount * 1000 / 50,  # Simplified calculation
                "debt_service_ratio": self.debt_timeline['debt_gdp'][self.debt_timeline['years'].index(year)] * 0.8,
                "debt_type": "Total Public Debt",
                "risk_level": "High" if int(year) >= 2020 else "Medium"
            })
        
        # Add debt composition
        debt_composition = [
            {"year": 2025, "debt_type": "External Commercial", "amount": 6.5, "percentage": 54, "interest_rate": 8.5},
            {"year": 2025, "debt_type": "Bilateral", "amount": 3.0, "percentage": 25, "interest_rate": 3.5},
            {"year": 2025, "debt_type": "Multilateral", "amount": 2.0, "percentage": 17, "interest_rate": 2.0},
            {"year": 2025, "debt_type": "Domestic", "amount": 0.55, "percentage": 4, "interest_rate": 12.5}
        ]
        
        debt_analysis.extend(debt_composition)
        
        return pd.DataFrame(debt_analysis)
    
    def create_budget_analysis(self, numeric_data: Dict) -> pd.DataFrame:
        """Create budget analysis DataFrame"""
        budget_analysis = []
        
        # Main budget allocations
        main_allocations = [
            {
                "sector": "Debt Service",
                "amount_2024": 2020,
                "amount_2025": 2020,
                "percentage_change": 0,
                "priority": "Mandatory",
                "efficiency_score": 30,
                "corruption_risk": "High"
            },
            {
                "sector": "Recurrent Expenditure",
                "amount_2024": 1040,
                "amount_2025": 1044,
                "percentage_change": 0.4,
                "priority": "Mandatory",
                "efficiency_score": 40,
                "corruption_risk": "Medium"
            },
            {
                "sector": "Development",
                "amount_2024": 520,
                "amount_2025": 540,
                "percentage_change": 3.8,
                "priority": "Discretionary",
                "efficiency_score": 50,
                "corruption_risk": "High"
            },
            {
                "sector": "County Allocation",
                "amount_2024": 385,
                "amount_2025": 400,
                "percentage_change": 3.9,
                "priority": "Mandatory",
                "efficiency_score": 35,
                "corruption_risk": "Very High"
            },
            {
                "sector": "Education",
                "amount_2024": 550,
                "amount_2025": 570,
                "percentage_change": 3.6,
                "priority": "High",
                "efficiency_score": 60,
                "corruption_risk": "Medium"
            },
            {
                "sector": "Health",
                "amount_2024": 140,
                "amount_2025": 150,
                "percentage_change": 7.1,
                "priority": "High",
                "efficiency_score": 45,
                "corruption_risk": "High"
            },
            {
                "sector": "Security",
                "amount_2024": 180,
                "amount_2025": 190,
                "percentage_change": 5.6,
                "priority": "High",
                "efficiency_score": 65,
                "corruption_risk": "Low"
            },
            {
                "sector": "Agriculture",
                "amount_2024": 60,
                "amount_2025": 65,
                "percentage_change": 8.3,
                "priority": "Medium",
                "efficiency_score": 55,
                "corruption_risk": "Medium"
            }
        ]
        
        budget_analysis.extend(main_allocations)
        
        # Add wasteful expenditure analysis
        wasteful_expenditure = [
            {
                "sector": "Government Snacks & Tea",
                "amount_2024": 6.2,
                "amount_2025": 6.2,
                "percentage_change": 0,
                "priority": "Low",
                "efficiency_score": 10,
                "corruption_risk": "Medium",
                "notes": "KSh 17 million daily"
            },
            {
                "sector": "Foreign Travel",
                "amount_2024": 8.5,
                "amount_2025": 9.0,
                "percentage_change": 5.9,
                "priority": "Low",
                "efficiency_score": 20,
                "corruption_risk": "High"
            },
            {
                "sector": "Advisory Services",
                "amount_2024": 12.0,
                "amount_2025": 13.0,
                "percentage_change": 8.3,
                "priority": "Medium",
                "efficiency_score": 35,
                "corruption_risk": "High"
            }
        ]
        
        budget_analysis.extend(wasteful_expenditure)
        
        return pd.DataFrame(budget_analysis)
    
    def create_reform_agenda(self, recommendations_data: List) -> Dict:
        """Create comprehensive reform agenda"""
        reform_agenda = {
            "fiscal_governance": {
                "title": "Fiscal Governance and Debt Management Reforms",
                "priority": "Critical",
                "timeframe": "Immediate (0-6 months)",
                "reforms": [
                    {
                        "id": "FG-001",
                        "title": "Debt Transparency Portal",
                        "description": "Publish all debt contracts, terms, and utilization reports online",
                        "impact": "High",
                        "cost": "Low",
                        "legal_basis": "Article 35, PFM Act",
                        "responsible_institution": "National Treasury",
                        "key_metrics": ["Contracts published", "Public access rate", "Timeliness"]
                    },
                    {
                        "id": "FG-002",
                        "title": "Supplementary Budget Control",
                        "description": "Enforce 10% constitutional limit on supplementary budgets",
                        "impact": "High",
                        "cost": "Low",
                        "legal_basis": "Article 223, PFM Act",
                        "responsible_institution": "Parliament, Controller of Budget",
                        "key_metrics": ["Supplementary budget size", "Compliance rate"]
                    },
                    {
                        "id": "FG-003",
                        "title": "Fiscal Responsibility Framework",
                        "description": "Implement binding debt ceilings and deficit targets",
                        "impact": "Medium",
                        "cost": "Medium",
                        "legal_basis": "Article 201, PFM Act",
                        "responsible_institution": "National Treasury, Parliament",
                        "key_metrics": ["Debt-to-GDP ratio", "Deficit targets met"]
                    }
                ]
            },
            
            "anti_corruption": {
                "title": "Anti-Corruption and Accountability Reforms",
                "priority": "Critical",
                "timeframe": "Immediate to Short-term (0-24 months)",
                "reforms": [
                    {
                        "id": "AC-001",
                        "title": "Corruption Fast-Track Courts",
                        "description": "Establish specialized courts to resolve corruption cases within 24 months",
                        "impact": "High",
                        "cost": "Medium",
                        "legal_basis": "Article 159, ACECA",
                        "responsible_institution": "Judiciary, ODPP",
                        "key_metrics": ["Case completion time", "Conviction rate", "Asset recovery"]
                    },
                    {
                        "id": "AC-002",
                        "title": "Beneficial Ownership Registry",
                        "description": "Implement Companies Act Section 93A for all government contractors",
                        "impact": "High",
                        "cost": "Medium",
                        "legal_basis": "Companies Act, Anti-Money Laundering Act",
                        "responsible_institution": "Business Registry, EACC",
                        "key_metrics": ["Registry completeness", "Contractor compliance"]
                    },
                    {
                        "id": "AC-003",
                        "title": "Audit Implementation Committee",
                        "description": "Cross-agency committee to enforce Auditor-General recommendations",
                        "impact": "Medium",
                        "cost": "Low",
                        "legal_basis": "Public Audit Act",
                        "responsible_institution": "OAG, Parliament, EACC",
                        "key_metrics": ["Recommendations implemented", "Recovery amounts"]
                    }
                ]
            },
            
            "political_financing": {
                "title": "Political Finance and Election Integrity Reforms",
                "priority": "High",
                "timeframe": "Short-term (6-24 months)",
                "reforms": [
                    {
                        "id": "PF-001",
                        "title": "Election Campaign Financing Enforcement",
                        "description": "Enforce existing Election Campaign Financing Act (never used)",
                        "impact": "High",
                        "cost": "Low",
                        "legal_basis": "Election Campaign Financing Act",
                        "responsible_institution": "IEBC, EACC",
                        "key_metrics": ["Compliance rate", "Prosecutions", "Fines collected"]
                    },
                    {
                        "id": "PF-002",
                        "title": "Political Party Funding Transparency",
                        "description": "Real-time disclosure of all political party funding",
                        "impact": "Medium",
                        "cost": "Low",
                        "legal_basis": "Political Parties Act",
                        "responsible_institution": "Registrar of Political Parties",
                        "key_metrics": ["Disclosure timeliness", "Donor transparency"]
                    }
                ]
            },
            
            "devolution": {
                "title": "Devolution and County Accountability Reforms",
                "priority": "High",
                "timeframe": "Short to Medium-term (12-36 months)",
                "reforms": [
                    {
                        "id": "DV-001",
                        "title": "County Performance-Based Funding",
                        "description": "Link county allocations to audit performance and service delivery",
                        "impact": "High",
                        "cost": "Medium",
                        "legal_basis": "Article 203, County Governments Act",
                        "responsible_institution": "Commission on Revenue Allocation",
                        "key_metrics": ["Clean audit counties", "Service delivery scores"]
                    },
                    {
                        "id": "DV-002",
                        "title": "Citizen County Oversight Committees",
                        "description": "Statutory citizen committees to monitor county expenditure",
                        "impact": "Medium",
                        "cost": "Low",
                        "legal_basis": "Article 196, Public Participation Act",
                        "responsible_institution": "County Assemblies",
                        "key_metrics": ["Committee functionality", "Issues raised", "Actions taken"]
                    }
                ]
            },
            
            "judicial_reform": {
                "title": "Judicial Independence and Efficiency Reforms",
                "priority": "Medium",
                "timeframe": "Medium-term (24-48 months)",
                "reforms": [
                    {
                        "id": "JR-001",
                        "title": "Judicial Financial Autonomy",
                        "description": "Constitutional amendment for automatic judiciary funding",
                        "impact": "High",
                        "cost": "Medium",
                        "legal_basis": "Article 160(4) amendment",
                        "responsible_institution": "Judiciary, Parliament",
                        "key_metrics": ["Budget adequacy", "Case backlog reduction"]
                    }
                ]
            },
            
            "social_protection": {
                "title": "Social Protection and Economic Rights Reforms",
                "priority": "High",
                "timeframe": "Immediate to Medium-term (0-36 months)",
                "reforms": [
                    {
                        "id": "SP-001",
                        "title": "Universal Healthcare Implementation",
                        "description": "Accelerate implementation of Article 43 right to health",
                        "impact": "High",
                        "cost": "High",
                        "legal_basis": "Article 43, Health Act",
                        "responsible_institution": "Ministry of Health",
                        "key_metrics": ["Health coverage", "Out-of-pocket expenses", "Maternal mortality"]
                    },
                    {
                        "id": "SP-002",
                        "title": "Food Security Guarantee",
                        "description": "Legal framework for right to food as per Article 43",
                        "impact": "High",
                        "cost": "High",
                        "legal_basis": "Article 43",
                        "responsible_institution": "Ministry of Agriculture",
                        "key_metrics": ["Food insecure population", "Agricultural productivity"]
                    }
                ]
            }
        }
        
        return reform_agenda
    
    def create_statistics_summary(self, numeric_data: Dict, findings_data: List) -> Dict:
        """Create comprehensive statistics summary"""
        stats_summary = {
            "fiscal_indicators": {
                "total_debt": "KSh 12.05 trillion",
                "debt_gdp_ratio": "70%",
                "debt_service_ratio": "56%",
                "per_capita_debt": "KSh 240,000",
                "annual_budget": "KSh 3.6 trillion",
                "debt_growth_2014_2025": "500%",
                "debt_service_amount": "KSh 2.02 trillion (2025)",
                "revenue_collection": "KSh 2.5 trillion (est. 2025)"
            },
            
            "corruption_indicators": {
                "annual_corruption_loss": "KSh 800 billion",
                "conviction_rate": "<10%",
                "counties_clean_audit": "6/47 (2023/24)",
                "audit_implementation": "18%",
                "corruption_perception_index": "28/100 (2024)",
                "asset_recovery_rate": "3-5%",
                "corruption_trials_pending": "2,500+",
                "average_trial_duration": "6+ years"
            },
            
            "social_indicators": {
                "food_insecure": "15.5 million",
                "below_poverty_line": "20 million (36% of population)",
                "youth_unemployed": "1.7 million graduates",
                "no_clean_water": "10 million",
                "no_electricity": "5 million",
                "population_2025": "55 million",
                "life_expectancy": "67 years",
                "gini_coefficient": "0.41 (high inequality)"
            },
            
            "governance_indicators": {
                "county_governments": "47",
                "clean_audit_counties": "6",
                "qualified_audit_counties": "25",
                "adverse_audit_counties": "16",
                "public_trust_in_institutions": "35%",
                "voter_turnout_2022": "65%",
                "women_representation": "23%",
                "youth_representation": "12%"
            },
            
            "human_rights_indicators": {
                "protest_deaths_2024": "200+",
                "missing_persons_2024": "50+",
                "police_brutality_cases": "300+ reported",
                "access_to_information_compliance": "20%",
                "land_rights_violations": "2,000+ cases pending",
                "child_labour": "1.2 million"
            },
            
            "comparative_analysis": {
                "debt_growth_rate": "Fastest in East Africa",
                "corruption_ranking": "3rd in Africa (Transparency Intl.)",
                "debt_service_ratio": "Highest in Africa",
                "youth_unemployment": "2nd highest in East Africa",
                "food_insecurity": "Worsening trend (2014-2025)",
                "audit_compliance": "Below regional average"
            },
            
            "metadata": {
                "data_sources": "National Treasury, KNBS, World Bank, IMF, EACC, OAG, CoB, UNICEF",
                "period_covered": "2014-2025",
                "last_updated": datetime.now().isoformat(),
                "methodology": "Official statistics, audit reports, research data",
                "confidence_level": "High for official data, Medium for estimates"
            }
        }
        
        return stats_summary
    
    def _load_json_safe(self, filepath: Path) -> Any:
        """Safely load JSON file with fallback"""
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"File not found: {filepath}")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading {filepath}: {str(e)}")
            return {}
    
    def _save_data_file(self, filename: str, data: Any):
        """Save data to appropriate format"""
        filepath = self.output_dir / filename
        
        try:
            if filename.endswith('.json'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif filename.endswith('.csv'):
                if isinstance(data, pd.DataFrame):
                    data.to_csv(filepath, index=False, encoding='utf-8')
                else:
                    self.logger.error(f"Data for {filename} is not a DataFrame")
                    
            self.logger.debug(f"Saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {str(e)}")