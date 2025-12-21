# visualizers/sankey_generator.py
import json
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict
import logging

class SankeyGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_sankey(self, sankey_data: Dict) -> str:
        """Generate Sankey diagram HTML"""
        try:
            # Extract nodes and links
            nodes = sankey_data.get('nodes', [])
            links = sankey_data.get('links', [])
            
            # Prepare data for Plotly
            source_indices = []
            target_indices = []
            values = []
            node_labels = []
            node_colors = []
            
            # Create node mapping
            node_map = {}
            for i, node in enumerate(nodes):
                node_name = node['name']
                node_map[node_name] = i
                node_labels.append(node_name)
                
                # Assign colors based on category
                color = self.get_node_color(node.get('category', 'other'))
                node_colors.append(color)
            
            # Create links
            for link in links:
                source = link['source']
                target = link['target']
                value = link['value']
                
                if source in node_map and target in node_map:
                    source_indices.append(node_map[source])
                    target_indices.append(node_map[target])
                    values.append(value)
            
            # Create Sankey diagram
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=node_labels,
                    color=node_colors
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=values,
                    color="rgba(150, 150, 150, 0.3)"
                )
            )])
            
            # Update layout
            fig.update_layout(
                title_text="Flow of Public Funds in Kenya (KSh Billions)",
                font_size=12,
                height=800,
                annotations=[
                    dict(
                        x=0.5,
                        y=1.1,
                        xref="paper",
                        yref="paper",
                        text="Source: People's Audit Analysis",
                        showarrow=False
                    )
                ]
            )
            
            # Convert to HTML
            html_content = fig.to_html(full_html=False, include_plotlyjs='cdn')
            
            # Wrap in complete HTML document
            full_html = self.create_html_wrapper(html_content)
            
            self.logger.info("Sankey diagram generated successfully")
            return full_html
            
        except Exception as e:
            self.logger.error(f"Error generating Sankey: {str(e)}")
            raise
    
    def get_node_color(self, category: str) -> str:
        """Get color for node based on category"""
        colors = {
            'source': 'rgba(31, 119, 180, 0.8)',
            'flow': 'rgba(255, 127, 14, 0.8)',
            'destination': 'rgba(44, 160, 44, 0.8)',
            'other': 'rgba(214, 39, 40, 0.8)'
        }
        return colors.get(category, 'rgba(148, 103, 189, 0.8)')
    
    def create_html_wrapper(self, plotly_html: str) -> str:
        """Create complete HTML wrapper for visualization"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>People's Audit - Sankey Diagram</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                header {{
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .explanation {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    margin: 20px 0;
                }}
                .legend {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin: 20px 0;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    margin-right: 20px;
                }}
                .legend-color {{
                    width: 20px;
                    height: 20px;
                    margin-right: 5px;
                    border-radius: 3px;
                }}
                footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Flow of Public Funds in Kenya</h1>
                    <p>Sankey Diagram showing how government money moves (KSh Billions)</p>
                </header>
                
                <div class="explanation">
                    <h3>How to Read This Diagram:</h3>
                    <p>The width of each flow represents the amount of money. 
                    Follow the flows from left (sources) to right (destinations). 
                    Hover over any element to see exact amounts.</p>
                </div>
                
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: rgba(31, 119, 180, 0.8);"></div>
                        <span>Sources (Where money comes from)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: rgba(255, 127, 14, 0.8);"></div>
                        <span>Flows (Where money goes through)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: rgba(44, 160, 44, 0.8);"></div>
                        <span>Destinations (Where money ends up)</span>
                    </div>
                </div>
                
                <div id="plotly-chart">
                    {plotly_html}
                </div>
                
                <div class="explanation">
                    <h3>Key Insights:</h3>
                    <ul>
                        <li><strong>KSh 800 billion</strong> flows to corruption annually</li>
                        <li><strong>KSh 750 billion</strong> goes to debt service</li>
                        <li>Only <strong>KSh 150 billion</strong> reaches health sector</li>
                        <li>Education receives <strong>KSh 120 billion</strong></li>
                    </ul>
                    <p><em>Note: Figures are approximate based on People's Audit analysis</em></p>
                </div>
                
                <footer>
                    <p>Data Source: People's Audit (December 8, 2025) | Generated: {date}</p>
                    <p>Interactive visualization - Use mouse to hover, drag, and zoom</p>
                </footer>
            </div>
        </body>
        </html>
        """

        from datetime import datetime
        date_str = datetime.now().strftime("%B %d, %Y")

        return html_template.format(plotly_html=plotly_html, date=date_str)

    
    def save_visualizations(self, html_content: str, output_dir: Path):
        """Save visualizations to files"""
        try:
            # Save HTML
            html_path = output_dir / 'sankey.html'
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Sankey HTML saved to {html_path}")
            
            # Note: For PNG export, would need additional setup
            # In production, would use kaleido or orca to export static images
            
        except Exception as e:
            self.logger.error(f"Error saving visualizations: {str(e)}")
            raise