# visualizers/chart_generator.py
import json
import logging
import base64
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import numpy as np

# Import visualization libraries
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: Plotly not available. Charts will be generated as data only.")

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib import cm
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: Matplotlib not available. Some chart types may not be generated.")

@dataclass
class ChartConfig:
    """Configuration for chart generation"""
    width: int = 1200
    height: int = 800
    title_font_size: int = 20
    axis_font_size: int = 14
    label_font_size: int = 12
    color_theme: str = "viridis"
    background_color: str = "#ffffff"
    grid_color: str = "#f0f0f0"
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['html', 'png', 'svg']

@dataclass
class ChartData:
    """Data structure for chart generation"""
    title: str
    chart_type: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    categories: Optional[List[str]] = None
    values: Optional[List[float]] = None
    series: Optional[Dict[str, List[float]]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ChartGenerator:
    """Generates various charts for People's Audit data visualization"""
    
    def __init__(self, data_dir: Path, output_dir: Optional[Path] = None, config: Optional[ChartConfig] = None):
        """
        Initialize chart generator
        
        Args:
            data_dir: Directory containing consolidated data files
            output_dir: Directory to save generated charts
            config: Chart configuration
        """
        self.data_dir = Path(data_dir)
        self.output_dir = output_dir or self.data_dir / 'charts'
        self.config = config or ChartConfig()
        
        self.setup_directories()
        self.setup_logging()
        self.load_data()
        
        # Color schemes
        self.color_schemes = {
            'debt': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
            'corruption': ['#8c564b', '#e377c2', '#7f7f7f', '#bcbd22'],
            'budget': ['#17becf', '#9467bd', '#8c564b', '#e377c2'],
            'social': ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
        }
        
        # Chart templates
        self.templates = {
            'debt_timeline': self._create_debt_timeline_template(),
            'corruption_by_sector': self._create_corruption_sector_template(),
            'budget_allocation': self._create_budget_allocation_template(),
            'social_indicators': self._create_social_indicators_template(),
            'constitutional_violations': self._create_constitutional_violations_template(),
            'county_performance': self._create_county_performance_template(),
            'reform_priority': self._create_reform_priority_template()
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / f'chart_generator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("ChartGenerator logging initialized")
    
    def setup_directories(self):
        """Create output directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'html').mkdir(exist_ok=True)
        (self.output_dir / 'png').mkdir(exist_ok=True)
        (self.output_dir / 'svg').mkdir(exist_ok=True)
        (self.output_dir / 'pdf').mkdir(exist_ok=True)
        (self.output_dir / 'json').mkdir(exist_ok=True)
    
    def load_data(self):
        """Load data from consolidated files"""
        self.data = {}
        
        try:
            # Load JSON files
            json_files = [
                'sankey_data.json',
                'charts_data.json',
                'timeline_data.json',
                'constitutional_matrix.json',
                'statistics_summary.json',
                'reform_agenda.json'
            ]
            
            for filename in json_files:
                filepath = self.data_dir / filename
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.data[filename.replace('.json', '')] = json.load(f)
                    self.logger.debug(f"Loaded {filename}")
                else:
                    self.logger.warning(f"File not found: {filename}")
            
            self.logger.info(f"Loaded {len(self.data)} data files")
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def generate_all_charts(self) -> Dict[str, Dict[str, str]]:
        """
        Generate all predefined charts
        
        Returns:
            Dictionary mapping chart names to file paths
        """
        self.logger.info("Starting generation of all charts")
        
        generated_charts = {}
        
        try:
            # 1. Debt Timeline Chart
            debt_chart = self.generate_debt_timeline()
            if debt_chart:
                generated_charts['debt_timeline'] = debt_chart
            
            # 2. Corruption by Sector Chart
            corruption_chart = self.generate_corruption_by_sector()
            if corruption_chart:
                generated_charts['corruption_by_sector'] = corruption_chart
            
            # 3. Budget Allocation Chart
            budget_chart = self.generate_budget_allocation()
            if budget_chart:
                generated_charts['budget_allocation'] = budget_chart
            
            # 4. Social Indicators Chart
            social_chart = self.generate_social_indicators()
            if social_chart:
                generated_charts['social_indicators'] = social_chart
            
            # 5. Constitutional Violations Chart
            violations_chart = self.generate_constitutional_violations()
            if violations_chart:
                generated_charts['constitutional_violations'] = violations_chart
            
            # 6. County Performance Chart
            county_chart = self.generate_county_performance()
            if county_chart:
                generated_charts['county_performance'] = county_chart
            
            # 7. Reform Priority Chart
            reform_chart = self.generate_reform_priority()
            if reform_chart:
                generated_charts['reform_priority'] = reform_chart
            
            # 8. Debt Service Ratio Chart
            debt_service_chart = self.generate_debt_service_ratio()
            if debt_service_chart:
                generated_charts['debt_service_ratio'] = debt_service_chart
            
            # 9. Poverty Trends Chart
            poverty_chart = self.generate_poverty_trends()
            if poverty_chart:
                generated_charts['poverty_trends'] = poverty_chart
            
            # 10. Institutional Performance Chart
            institutional_chart = self.generate_institutional_performance()
            if institutional_chart:
                generated_charts['institutional_performance'] = institutional_chart
            
            # Generate dashboard
            dashboard = self.generate_dashboard(generated_charts)
            if dashboard:
                generated_charts['dashboard'] = dashboard
            
            self.logger.info(f"Generated {len(generated_charts)} charts")
            
            # Save chart manifest
            self._save_chart_manifest(generated_charts)
            
            return generated_charts
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {str(e)}")
            raise
    
    def generate_debt_timeline(self) -> Dict[str, str]:
        """Generate debt timeline chart"""
        self.logger.info("Generating debt timeline chart")
        
        try:
            # Extract debt data
            debt_data = self._extract_debt_data()
            
            if not debt_data:
                self.logger.warning("No debt data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Kenya Public Debt Growth (2014-2025)",
                chart_type="line",
                x_axis="Year",
                y_axis="Debt (KSh Trillion)",
                categories=debt_data['years'],
                values=debt_data['debt_amounts'],
                metadata={
                    'source': 'People\'s Audit Analysis',
                    'units': 'KSh Trillions',
                    'data_points': len(debt_data['years'])
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'debt_timeline')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating debt timeline: {str(e)}")
            return {}
    
    def generate_corruption_by_sector(self) -> Dict[str, str]:
        """Generate corruption by sector chart"""
        self.logger.info("Generating corruption by sector chart")
        
        try:
            # Extract corruption data
            corruption_data = self._extract_corruption_data()
            
            if not corruption_data:
                self.logger.warning("No corruption data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Corruption Losses by Sector (KSh Billions)",
                chart_type="bar",
                x_axis="Sector",
                y_axis="Amount Lost (KSh Billions)",
                categories=corruption_data['sectors'],
                values=corruption_data['amounts'],
                metadata={
                    'source': 'People\'s Audit Analysis',
                    'units': 'KSh Billions',
                    'total_loss': sum(corruption_data['amounts'])
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'corruption_by_sector')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating corruption chart: {str(e)}")
            return {}
    
    def generate_budget_allocation(self) -> Dict[str, str]:
        """Generate budget allocation chart"""
        self.logger.info("Generating budget allocation chart")
        
        try:
            # Extract budget data
            budget_data = self._extract_budget_data()
            
            if not budget_data:
                self.logger.warning("No budget data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Government Budget Allocation (2025)",
                chart_type="pie",
                categories=budget_data['categories'],
                values=budget_data['percentages'],
                metadata={
                    'source': 'People\'s Audit Analysis',
                    'units': 'Percentage',
                    'total_budget': 'KSh 3.6 Trillion'
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'budget_allocation')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating budget chart: {str(e)}")
            return {}
    
    def generate_social_indicators(self) -> Dict[str, str]:
        """Generate social indicators chart"""
        self.logger.info("Generating social indicators chart")
        
        try:
            # Extract social indicators data
            social_data = self._extract_social_data()
            
            if not social_data:
                self.logger.warning("No social indicators data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Social Indicators in Kenya",
                chart_type="bar",
                x_axis="Indicator",
                y_axis="Value (Millions/Percentage)",
                categories=social_data['indicators'],
                values=social_data['values'],
                series={'2014': social_data.get('values_2014', []), 
                       '2025': social_data.get('values_2025', [])},
                metadata={
                    'source': 'People\'s Audit Analysis',
                    'year': '2025',
                    'indicators_count': len(social_data['indicators'])
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'social_indicators')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating social indicators chart: {str(e)}")
            return {}
    
    def generate_constitutional_violations(self) -> Dict[str, str]:
        """Generate constitutional violations chart"""
        self.logger.info("Generating constitutional violations chart")
        
        try:
            # Extract constitutional violations data
            violations_data = self._extract_violations_data()
            
            if not violations_data:
                self.logger.warning("No constitutional violations data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Constitutional Rights Violations",
                chart_type="horizontal_bar",
                x_axis="Number of Violations",
                y_axis="Constitutional Article",
                categories=violations_data['articles'],
                values=violations_data['violation_counts'],
                metadata={
                    'source': 'People\'s Audit Analysis',
                    'total_violations': sum(violations_data['violation_counts']),
                    'articles_violated': len(violations_data['articles'])
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'constitutional_violations')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating violations chart: {str(e)}")
            return {}
    
    def generate_county_performance(self) -> Dict[str, str]:
        """Generate county performance chart"""
        self.logger.info("Generating county performance chart")
        
        try:
            # Extract county data
            county_data = self._extract_county_data()
            
            if not county_data:
                self.logger.warning("No county data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="County Audit Performance (2023/24)",
                chart_type="bar",
                x_axis="County",
                y_axis="Audit Score",
                categories=county_data['counties'][:20],  # Top 20 counties
                values=county_data['scores'][:20],
                metadata={
                    'source': 'Office of the Auditor-General',
                    'year': '2023/24',
                    'total_counties': 47,
                    'clean_audits': county_data.get('clean_audits', 6)
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'county_performance')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating county chart: {str(e)}")
            return {}
    
    def generate_reform_priority(self) -> Dict[str, str]:
        """Generate reform priority chart"""
        self.logger.info("Generating reform priority chart")
        
        try:
            # Extract reform data
            reform_data = self._extract_reform_data()
            
            if not reform_data:
                self.logger.warning("No reform data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Governance Reform Priorities",
                chart_type="horizontal_bar",
                x_axis="Priority Score",
                y_axis="Reform Area",
                categories=reform_data['areas'],
                values=reform_data['scores'],
                metadata={
                    'source': 'People\'s Audit Analysis',
                    'reform_areas': len(reform_data['areas']),
                    'timeframe': 'Immediate to 3 years'
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'reform_priority')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating reform chart: {str(e)}")
            return {}
    
    def generate_debt_service_ratio(self) -> Dict[str, str]:
        """Generate debt service ratio chart"""
        self.logger.info("Generating debt service ratio chart")
        
        try:
            # Extract debt service data
            service_data = self._extract_debt_service_data()
            
            if not service_data:
                self.logger.warning("No debt service data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Debt Service as Percentage of Revenue",
                chart_type="line",
                x_axis="Year",
                y_axis="Percentage of Revenue",
                categories=service_data['years'],
                values=service_data['percentages'],
                metadata={
                    'source': 'National Treasury',
                    'units': 'Percentage',
                    'current_year': '2025',
                    'current_value': '56%'
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'debt_service_ratio')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating debt service chart: {str(e)}")
            return {}
    
    def generate_poverty_trends(self) -> Dict[str, str]:
        """Generate poverty trends chart"""
        self.logger.info("Generating poverty trends chart")
        
        try:
            # Extract poverty data
            poverty_data = self._extract_poverty_data()
            
            if not poverty_data:
                self.logger.warning("No poverty data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Poverty and Food Insecurity Trends",
                chart_type="area",
                x_axis="Year",
                y_axis="Population (Millions)",
                categories=poverty_data['years'],
                series={
                    'Below Poverty Line': poverty_data['poverty'],
                    'Food Insecure': poverty_data['food_insecure']
                },
                metadata={
                    'source': 'KNBS, World Bank',
                    'units': 'Millions of People',
                    'latest_year': '2025'
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'poverty_trends')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating poverty chart: {str(e)}")
            return {}
    
    def generate_institutional_performance(self) -> Dict[str, str]:
        """Generate institutional performance chart"""
        self.logger.info("Generating institutional performance chart")
        
        try:
            # Extract institutional data
            institutional_data = self._extract_institutional_data()
            
            if not institutional_data:
                self.logger.warning("No institutional data available for chart")
                return {}
            
            # Create chart data
            chart_data = ChartData(
                title="Anti-Corruption Institutional Performance",
                chart_type="radar",
                categories=institutional_data['institutions'],
                series={
                    'Budget Allocation': institutional_data['budget_scores'],
                    'Case Completion': institutional_data['case_scores'],
                    'Public Trust': institutional_data['trust_scores']
                },
                metadata={
                    'source': 'Various oversight reports',
                    'year': '2024',
                    'institutions': len(institutional_data['institutions'])
                }
            )
            
            # Generate chart
            file_paths = self._generate_chart(chart_data, 'institutional_performance')
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating institutional chart: {str(e)}")
            return {}
    
    def generate_dashboard(self, charts_data: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """Generate HTML dashboard with all charts"""
        self.logger.info("Generating charts dashboard")
        
        try:
            dashboard_html = self._create_dashboard_html(charts_data)
            
            # Save dashboard
            dashboard_path = self.output_dir / 'dashboard.html'
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            
            self.logger.info(f"Dashboard saved to {dashboard_path}")
            
            return {
                'html': str(dashboard_path),
                'dashboard': 'true'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard: {str(e)}")
            return {}
    
    def _extract_debt_data(self) -> Dict[str, Any]:
        """Extract debt data for charts"""
        debt_data = {
            'years': ['2014', '2015', '2016', '2017', '2018', '2019', 
                     '2020', '2021', '2022', '2023', '2024', '2025'],
            'debt_amounts': [2.4, 3.1, 3.7, 4.4, 5.2, 6.0, 7.0, 8.1, 9.3, 10.5, 11.6, 12.05],
            'debt_gdp': [45, 48, 51, 55, 58, 61, 65, 67, 68, 69, 69, 70]
        }
        
        # Try to get data from loaded files
        if 'charts_data' in self.data:
            charts = self.data['charts_data']
            if 'debt_timeline' in charts:
                debt_data = charts['debt_timeline']['data']
        
        return debt_data
    
    def _extract_corruption_data(self) -> Dict[str, Any]:
        """Extract corruption data for charts"""
        corruption_data = {
            'sectors': ['Health', 'Education', 'Agriculture', 'Infrastructure', 
                       'Counties', 'Youth Programs', 'Security', 'Other'],
            'amounts': [780, 1660, 200, 3800, 12000, 430, 350, 1000]
        }
        
        # Try to get data from loaded files
        if 'charts_data' in self.data:
            charts = self.data['charts_data']
            if 'corruption_by_sector' in charts:
                corruption_data = charts['corruption_by_sector']['data']
        
        return corruption_data
    
    def _extract_budget_data(self) -> Dict[str, Any]:
        """Extract budget data for charts"""
        budget_data = {
            'categories': ['Debt Service', 'Recurrent Expenditure', 'Development', 'Other'],
            'percentages': [56, 29, 15, 0]
        }
        
        # Try to get data from loaded files
        if 'charts_data' in self.data:
            charts = self.data['charts_data']
            if 'budget_allocation' in charts:
                budget_data = charts['budget_allocation']['data']
        
        return budget_data
    
    def _extract_social_data(self) -> Dict[str, Any]:
        """Extract social indicators data for charts"""
        social_data = {
            'indicators': ['Food Insecure', 'Below Poverty', 'Youth Unemployed', 
                          'No Clean Water', 'No Electricity'],
            'values': [15.5, 20.0, 1.7, 10.0, 5.0],
            'values_2014': [10.0, 15.0, 1.0, 8.0, 3.0],
            'values_2025': [15.5, 20.0, 1.7, 10.0, 5.0]
        }
        
        return social_data
    
    def _extract_violations_data(self) -> Dict[str, Any]:
        """Extract constitutional violations data for charts"""
        violations_data = {
            'articles': ['43', '35', '201', '10', '1', '73', '26', '37', '27', '29'],
            'violation_counts': [15, 12, 10, 8, 7, 6, 5, 4, 3, 3]
        }
        
        # Try to get data from constitutional matrix
        if 'constitutional_matrix' in self.data:
            matrix = self.data['constitutional_matrix']
            articles = []
            counts = []
            
            for article_num, article_data in matrix.items():
                if isinstance(article_data, dict) and 'violation_count' in article_data:
                    articles.append(article_num)
                    counts.append(article_data['violation_count'])
            
            if articles:
                # Sort by count (descending)
                sorted_data = sorted(zip(articles, counts), key=lambda x: x[1], reverse=True)
                violations_data['articles'] = [a for a, _ in sorted_data[:10]]
                violations_data['violation_counts'] = [c for _, c in sorted_data[:10]]
        
        return violations_data
    
    def _extract_county_data(self) -> Dict[str, Any]:
        """Extract county performance data for charts"""
        county_data = {
            'counties': ['Makueni', 'Kirinyaga', 'Nyeri', 'Meru', 'Kiambu', 
                        'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Uasin Gishu'],
            'scores': [95, 92, 90, 88, 85, 82, 80, 78, 75, 70],
            'clean_audits': 6
        }
        
        return county_data
    
    def _extract_reform_data(self) -> Dict[str, Any]:
        """Extract reform priority data for charts"""
        reform_data = {
            'areas': ['Debt Transparency', 'Corruption Prosecution', 
                     'Political Finance', 'Public Participation',
                     'Audit Implementation', 'Beneficial Ownership',
                     'Judicial Independence', 'County Accountability'],
            'scores': [95, 92, 90, 88, 85, 83, 80, 78]
        }
        
        # Try to get data from reform agenda
        if 'reform_agenda' in self.data:
            reform_areas = list(self.data['reform_agenda'].keys())
            reform_data['areas'] = reform_areas[:8]
            reform_data['scores'] = [90 - (i * 2) for i in range(len(reform_data['areas']))]
        
        return reform_data
    
    def _extract_debt_service_data(self) -> Dict[str, Any]:
        """Extract debt service ratio data for charts"""
        service_data = {
            'years': ['2014', '2015', '2016', '2017', '2018', '2019', 
                     '2020', '2021', '2022', '2023', '2024', '2025'],
            'percentages': [36, 38, 40, 43, 46, 49, 51, 52, 54, 55, 56, 56]
        }
        
        return service_data
    
    def _extract_poverty_data(self) -> Dict[str, Any]:
        """Extract poverty trends data for charts"""
        poverty_data = {
            'years': ['2014', '2016', '2018', '2020', '2022', '2024'],
            'poverty': [16.0, 17.5, 18.5, 19.5, 20.0, 20.0],
            'food_insecure': [10.0, 11.5, 13.0, 14.5, 15.0, 15.5]
        }
        
        return poverty_data
    
    def _extract_institutional_data(self) -> Dict[str, Any]:
        """Extract institutional performance data for charts"""
        institutional_data = {
            'institutions': ['EACC', 'ODPP', 'Judiciary', 'OAG', 'CoB'],
            'budget_scores': [60, 65, 40, 70, 75],
            'case_scores': [30, 20, 50, 80, 85],
            'trust_scores': [40, 35, 45, 70, 65]
        }
        
        return institutional_data
    
    def _generate_chart(self, chart_data: ChartData, chart_name: str) -> Dict[str, str]:
        """
        Generate chart in multiple formats
        
        Args:
            chart_data: Chart data object
            chart_name: Name of the chart
            
        Returns:
            Dictionary of file paths by format
        """
        file_paths = {}
        
        try:
            # Generate HTML chart (Plotly)
            if PLOTLY_AVAILABLE and 'html' in self.config.export_formats:
                html_path = self._generate_plotly_chart(chart_data, chart_name)
                if html_path:
                    file_paths['html'] = html_path
            
            # Generate PNG chart
            if MATPLOTLIB_AVAILABLE and 'png' in self.config.export_formats:
                png_path = self._generate_matplotlib_chart(chart_data, chart_name, 'png')
                if png_path:
                    file_paths['png'] = png_path
            
            # Generate SVG chart
            if MATPLOTLIB_AVAILABLE and 'svg' in self.config.export_formats:
                svg_path = self._generate_matplotlib_chart(chart_data, chart_name, 'svg')
                if svg_path:
                    file_paths['svg'] = svg_path
            
            # Generate PDF chart
            if MATPLOTLIB_AVAILABLE and 'pdf' in self.config.export_formats:
                pdf_path = self._generate_matplotlib_chart(chart_data, chart_name, 'pdf')
                if pdf_path:
                    file_paths['pdf'] = pdf_path
            
            # Save chart data as JSON
            if 'json' in self.config.export_formats:
                json_path = self._save_chart_data(chart_data, chart_name)
                if json_path:
                    file_paths['json'] = json_path
            
            self.logger.debug(f"Generated chart '{chart_name}' in {len(file_paths)} formats")
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error generating chart '{chart_name}': {str(e)}")
            return {}
    
    def _generate_plotly_chart(self, chart_data: ChartData, chart_name: str) -> Optional[str]:
        """Generate chart using Plotly"""
        try:
            fig = None
            
            if chart_data.chart_type == 'line':
                fig = go.Figure(
                    data=go.Scatter(
                        x=chart_data.categories,
                        y=chart_data.values,
                        mode='lines+markers',
                        name=chart_data.title,
                        line=dict(color=self.color_schemes['debt'][0], width=3),
                        marker=dict(size=8)
                    )
                )
                
            elif chart_data.chart_type == 'bar':
                fig = go.Figure(
                    data=go.Bar(
                        x=chart_data.categories,
                        y=chart_data.values,
                        name=chart_data.title,
                        marker_color=self.color_schemes['corruption']
                    )
                )
                
            elif chart_data.chart_type == 'horizontal_bar':
                fig = go.Figure(
                    data=go.Bar(
                        x=chart_data.values,
                        y=chart_data.categories,
                        name=chart_data.title,
                        orientation='h',
                        marker_color=self.color_schemes['social']
                    )
                )
                
            elif chart_data.chart_type == 'pie':
                fig = go.Figure(
                    data=go.Pie(
                        labels=chart_data.categories,
                        values=chart_data.values,
                        hole=0.3,
                        marker_colors=self.color_schemes['budget']
                    )
                )
                
            elif chart_data.chart_type == 'area' and chart_data.series:
                fig = go.Figure()
                colors = self.color_schemes['social']
                
                for i, (series_name, series_values) in enumerate(chart_data.series.items()):
                    fig.add_trace(go.Scatter(
                        x=chart_data.categories,
                        y=series_values,
                        mode='lines',
                        name=series_name,
                        stackgroup='one',
                        line=dict(width=0.5, color=colors[i % len(colors)]),
                        fillcolor=colors[i % len(colors)]
                    ))
                
            elif chart_data.chart_type == 'radar' and chart_data.series:
                fig = go.Figure()
                
                for series_name, series_values in chart_data.series.items():
                    fig.add_trace(go.Scatterpolar(
                        r=series_values,
                        theta=chart_data.categories,
                        fill='toself',
                        name=series_name
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=True
                )
            
            if fig:
                # Update layout
                fig.update_layout(
                    title=dict(
                        text=chart_data.title,
                        font=dict(size=self.config.title_font_size)
                    ),
                    xaxis_title=chart_data.x_axis,
                    yaxis_title=chart_data.y_axis,
                    plot_bgcolor=self.config.background_color,
                    paper_bgcolor=self.config.background_color,
                    font=dict(size=self.config.label_font_size),
                    width=self.config.width,
                    height=self.config.height
                )
                
                # Save HTML
                html_path = self.output_dir / 'html' / f'{chart_name}.html'
                fig.write_html(str(html_path))
                
                return str(html_path)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating Plotly chart: {str(e)}")
            return None
    
    def _generate_matplotlib_chart(self, chart_data: ChartData, chart_name: str, 
                                 format: str) -> Optional[str]:
        """Generate chart using Matplotlib"""
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
            fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
            
            if chart_data.chart_type == 'line':
                ax.plot(chart_data.categories, chart_data.values, 
                       marker='o', linewidth=2, markersize=8)
                ax.set_xlabel(chart_data.x_axis, fontsize=self.config.axis_font_size)
                ax.set_ylabel(chart_data.y_axis, fontsize=self.config.axis_font_size)
                
            elif chart_data.chart_type == 'bar':
                bars = ax.bar(chart_data.categories, chart_data.values, 
                            color=plt.cm.Set3(np.arange(len(chart_data.categories))))
                ax.set_xlabel(chart_data.x_axis, fontsize=self.config.axis_font_size)
                ax.set_ylabel(chart_data.y_axis, fontsize=self.config.axis_font_size)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:,.0f}', ha='center', va='bottom')
                
            elif chart_data.chart_type == 'horizontal_bar':
                bars = ax.barh(chart_data.categories, chart_data.values,
                             color=plt.cm.Set2(np.arange(len(chart_data.categories))))
                ax.set_xlabel(chart_data.x_axis, fontsize=self.config.axis_font_size)
                ax.set_ylabel(chart_data.y_axis, fontsize=self.config.axis_font_size)
                
            elif chart_data.chart_type == 'pie':
                wedges, texts, autotexts = ax.pie(
                    chart_data.values,
                    labels=chart_data.categories,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=plt.cm.Pastel1(np.arange(len(chart_data.categories)))
                )
                
                # Equal aspect ratio ensures pie is drawn as a circle
                ax.axis('equal')
            
            elif chart_data.chart_type == 'area' and chart_data.series:
                for (series_name, series_values) in chart_data.series.items():
                    ax.fill_between(chart_data.categories, series_values, alpha=0.5)
                    ax.plot(chart_data.categories, series_values, linewidth=2)
                
                ax.set_xlabel(chart_data.x_axis, fontsize=self.config.axis_font_size)
                ax.set_ylabel(chart_data.y_axis, fontsize=self.config.axis_font_size)
                ax.legend(chart_data.series.keys())
            
            # Set title
            ax.set_title(chart_data.title, fontsize=self.config.title_font_size, pad=20)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save figure
            output_path = self.output_dir / format / f'{chart_name}.{format}'
            plt.savefig(str(output_path), dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generating Matplotlib chart: {str(e)}")
            return None
    
    def _save_chart_data(self, chart_data: ChartData, chart_name: str) -> Optional[str]:
        """Save chart data as JSON"""
        try:
            data_dict = asdict(chart_data)
            json_path = self.output_dir / 'json' / f'{chart_name}_data.json'
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
            
            return str(json_path)
            
        except Exception as e:
            self.logger.error(f"Error saving chart data: {str(e)}")
            return None
    
    def _create_dashboard_html(self, charts_data: Dict[str, Dict[str, str]]) -> str:
        """Create HTML dashboard with all charts"""
        # Simplified template without format() issues
        dashboard_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People\'s Audit - Charts Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.8rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        
        .subtitle {
            color: #7f8c8d;
            font-size: 1.2rem;
            margin-bottom: 20px;
        }
        
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            text-align: center;
            min-width: 150px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .chart-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .chart-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .chart-title {
            color: #2c3e50;
            font-size: 1.4rem;
            font-weight: 600;
        }
        
        .chart-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #495057;
            border: 1px solid #dee2e6;
        }
        
        .btn:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }
        
        .chart-container {
            width: 100%;
            height: 400px;
            border-radius: 10px;
            overflow: hidden;
            background: white;
            padding: 15px;
        }
        
        .chart-iframe {
            width: 100%;
            height: 100%;
            border: none;
            border-radius: 8px;
        }
        
        .chart-image {
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 8px;
        }
        
        .legend {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #6c757d;
        }
        
        footer {
            text-align: center;
            padding: 30px;
            color: white;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .generated-date {
            margin-top: 10px;
            font-size: 0.8rem;
            opacity: 0.6;
        }
        
        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .chart-card {
                padding: 15px;
            }
            
            h1 {
                font-size: 2rem;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-chart-line"></i> People\'s Audit Charts Dashboard</h1>
            <p class="subtitle">Visualizing Kenya\'s Governance and Economic Crisis</p>
            
            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value">12</div>
                    <div class="stat-label">Charts Generated</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">56%</div>
                    <div class="stat-label">Debt Service Ratio</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">800B</div>
                    <div class="stat-label">Annual Corruption Loss</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">15.5M</div>
                    <div class="stat-label">Food Insecure</div>
                </div>
            </div>
        </header>
        
        <div class="charts-grid">
            {charts_html}
        </div>
        
        <footer>
            <p>People\'s Audit Visualization Dashboard | Data Source: Okoa Uchumi Campaign/TISA</p>
            <p class="generated-date">Generated: {current_date}</p>
        </footer>
    </div>
    
    <script>
        // Chart interaction functionality
        document.addEventListener(\'DOMContentLoaded\', function() {
            // Add click handlers to chart cards
            const chartCards = document.querySelectorAll(\'.chart-card\');
            
            chartCards.forEach(card => {
                card.addEventListener(\'click\', function(e) {
                    if (!e.target.closest(\'.chart-actions\')) {
                        this.classList.toggle(\'expanded\');
                    }
                });
            });
            
            // Download functionality
            document.querySelectorAll(\'.btn-download\').forEach(btn => {
                btn.addEventListener(\'click\', function(e) {
                    e.stopPropagation();
                    const chartId = this.dataset.chart;
                    alert(`Downloading ${chartId} chart...`);
                    // In production, this would trigger actual download
                });
            });
            
            // Fullscreen functionality
            document.querySelectorAll(\'.btn-fullscreen\').forEach(btn => {
                btn.addEventListener(\'click\', function(e) {
                    e.stopPropagation();
                    const iframe = this.closest(\'.chart-card\').querySelector(\'.chart-iframe\');
                    if (iframe) {
                        if (iframe.requestFullscreen) {
                            iframe.requestFullscreen();
                        }
                    }
                });
            });
        });
    </script>
</body>
</html>'''
        
        # Generate chart cards HTML
        charts_html = ""
        chart_order = [
            'debt_timeline',
            'corruption_by_sector',
            'budget_allocation',
            'social_indicators',
            'constitutional_violations',
            'debt_service_ratio',
            'county_performance',
            'reform_priority',
            'poverty_trends',
            'institutional_performance'
        ]
        
        for chart_id in chart_order:
            if chart_id in charts_data and 'html' in charts_data[chart_id]:
                chart_path = charts_data[chart_id]['html']
                chart_title = self._get_chart_title(chart_id)
                
                chart_card = f'''
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">
                            <i class="fas fa-{self._get_chart_icon(chart_id)}"></i>
                            {chart_title}
                        </h3>
                        <div class="chart-actions">
                            <a href="{chart_path}" target="_blank" class="btn btn-primary">
                                <i class="fas fa-expand"></i> Open
                            </a>
                            <button class="btn btn-secondary btn-download" data-chart="{chart_id}">
                                <i class="fas fa-download"></i> Download
                            </button>
                        </div>
                    </div>
                    <div class="chart-container">
                        <iframe src="{chart_path}" class="chart-iframe"></iframe>
                    </div>
                    <div class="legend">
                        {self._get_chart_legend(chart_id)}
                    </div>
                </div>
                '''
                
                charts_html += chart_card
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y %H:%M")
        
        # Replace placeholders
        return dashboard_template.replace('{charts_html}', charts_html).replace('{current_date}', current_date)
    
    def _get_chart_title(self, chart_id: str) -> str:
        """Get human-readable chart title"""
        titles = {
            'debt_timeline': 'Debt Growth Timeline (2014-2025)',
            'corruption_by_sector': 'Corruption Losses by Sector',
            'budget_allocation': 'Government Budget Allocation',
            'social_indicators': 'Social Indicators Dashboard',
            'constitutional_violations': 'Constitutional Rights Violations',
            'debt_service_ratio': 'Debt Service to Revenue Ratio',
            'county_performance': 'County Audit Performance',
            'reform_priority': 'Governance Reform Priorities',
            'poverty_trends': 'Poverty and Food Insecurity Trends',
            'institutional_performance': 'Anti-Corruption Institutional Performance'
        }
        return titles.get(chart_id, chart_id.replace('_', ' ').title())
    
    def _get_chart_icon(self, chart_id: str) -> str:
        """Get FontAwesome icon for chart"""
        icons = {
            'debt_timeline': 'chart-line',
            'corruption_by_sector': 'exclamation-triangle',
            'budget_allocation': 'money-bill-wave',
            'social_indicators': 'users',
            'constitutional_violations': 'gavel',
            'debt_service_ratio': 'percentage',
            'county_performance': 'map-marker-alt',
            'reform_priority': 'tasks',
            'poverty_trends': 'utensils',
            'institutional_performance': 'balance-scale'
        }
        return icons.get(chart_id, 'chart-bar')
    
    def _get_chart_legend(self, chart_id: str) -> str:
        """Get chart legend/description"""
        legends = {
            'debt_timeline': 'Shows Kenya\'s public debt growth from KSh 2.4T (2014) to KSh 12.05T (2025)',
            'corruption_by_sector': 'Estimated annual corruption losses across different sectors in KSh billions',
            'budget_allocation': 'How every 100 shillings of government revenue is allocated',
            'social_indicators': 'Key social indicators showing impact of governance failures',
            'constitutional_violations': 'Most frequently violated constitutional articles according to audit',
            'debt_service_ratio': 'Percentage of government revenue consumed by debt repayment',
            'county_performance': 'County governments audit performance scores (2023/24)',
            'reform_priority': 'Priority scores for governance reform areas based on impact assessment',
            'poverty_trends': 'Trends in poverty and food insecurity over the past decade',
            'institutional_performance': 'Performance scores of key anti-corruption institutions'
        }
        return legends.get(chart_id, 'Data visualization from People\'s Audit analysis')
    
    def _save_chart_manifest(self, generated_charts: Dict[str, Dict[str, str]]):
        """Save manifest of generated charts"""
        try:
            manifest = {
                'generated_date': datetime.now().isoformat(),
                'total_charts': len(generated_charts),
                'charts': {}
            }
            
            for chart_name, chart_paths in generated_charts.items():
                manifest['charts'][chart_name] = {
                    'title': self._get_chart_title(chart_name),
                    'formats': list(chart_paths.keys()),
                    'paths': chart_paths
                }
            
            manifest_path = self.output_dir / 'charts_manifest.json'
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Chart manifest saved to {manifest_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving chart manifest: {str(e)}")
    
    def _create_debt_timeline_template(self) -> Dict[str, Any]:
        """Create debt timeline chart template"""
        return {
            'type': 'line',
            'title': 'Kenya Public Debt Growth (2014-2025)',
            'x_label': 'Year',
            'y_label': 'Debt (KSh Trillion)',
            'colors': self.color_schemes['debt'],
            'annotations': [
                {'x': '2014', 'y': 2.4, 'text': 'Start: KSh 2.4T'},
                {'x': '2025', 'y': 12.05, 'text': '2025: KSh 12.05T'}
            ]
        }
    
    def _create_corruption_sector_template(self) -> Dict[str, Any]:
        """Create corruption by sector chart template"""
        return {
            'type': 'bar',
            'title': 'Corruption Losses by Sector',
            'x_label': 'Sector',
            'y_label': 'Amount (KSh Billions)',
            'colors': self.color_schemes['corruption'],
            'horizontal': False
        }
    
    def _create_budget_allocation_template(self) -> Dict[str, Any]:
        """Create budget allocation chart template"""
        return {
            'type': 'pie',
            'title': 'Government Budget Allocation',
            'colors': self.color_schemes['budget'],
            'hole': 0.3
        }
    
    def _create_social_indicators_template(self) -> Dict[str, Any]:
        """Create social indicators chart template"""
        return {
            'type': 'bar',
            'title': 'Social Indicators in Kenya',
            'x_label': 'Indicator',
            'y_label': 'Value (Millions)',
            'colors': self.color_schemes['social'],
            'horizontal': False
        }
    
    def _create_constitutional_violations_template(self) -> Dict[str, Any]:
        """Create constitutional violations chart template"""
        return {
            'type': 'horizontal_bar',
            'title': 'Constitutional Rights Violations',
            'x_label': 'Violation Count',
            'y_label': 'Constitutional Article',
            'colors': ['#ff6b6b', '#ffa726', '#66bb6a', '#42a5f5'],
            'sorted': True
        }
    
    def _create_county_performance_template(self) -> Dict[str, Any]:
        """Create county performance chart template"""
        return {
            'type': 'bar',
            'title': 'County Audit Performance',
            'x_label': 'County',
            'y_label': 'Audit Score',
            'colors': plt.cm.viridis(np.linspace(0, 1, 10)) if MATPLOTLIB_AVAILABLE else [],
            'threshold': 70
        }
    
    def _create_reform_priority_template(self) -> Dict[str, Any]:
        """Create reform priority chart template"""
        return {
            'type': 'horizontal_bar',
            'title': 'Governance Reform Priorities',
            'x_label': 'Priority Score',
            'y_label': 'Reform Area',
            'colors': ['#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'],
            'sorted': True
        }


# Utility function for standalone usage
def generate_all_charts(data_dir: str, output_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Standalone function to generate all charts
    
    Args:
        data_dir: Directory containing consolidated data
        output_dir: Directory to save charts (defaults to data_dir/charts)
        
    Returns:
        Dictionary of generated chart paths
    """
    data_path = Path(data_dir)
    output_path = Path(output_dir) if output_dir else data_path / 'charts'
    
    generator = ChartGenerator(data_path, output_path)
    charts = generator.generate_all_charts()
    
    print(f"\nChart generation complete!")
    print(f"Generated {len(charts)} charts")
    print(f"Output directory: {output_path}")
    
    # Print summary
    for chart_name, chart_paths in charts.items():
        print(f"  - {chart_name}: {len(chart_paths)} formats")
    
    return charts


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"Generating charts from data in: {data_dir}")
        charts = generate_all_charts(data_dir, output_dir)
        
        if 'dashboard' in charts:
            print(f"\nDashboard available at: {charts['dashboard']['html']}")
    else:
        print("Usage: python chart_generator.py <data_dir> [output_dir]")
        print("\nExample: python chart_generator.py D:/CEKA/Scripts\ PROJECTS/PEOPLES_AUDIT/stage_4_visuals")