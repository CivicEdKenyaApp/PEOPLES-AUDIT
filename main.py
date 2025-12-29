#!/usr/bin/env python3
"""
PEOPLE'S AUDIT PIPELINE - MAIN ENTRY POINT
==========================================
Complete pipeline for analyzing Kenya's economic governance crisis
"""

import os
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
import logging
import traceback

class PeopleAuditPipeline:
    """Main pipeline controller for People's Audit analysis"""
    
    def __init__(self, root_path: str):
        """
        Initialize the complete pipeline system
        
        Args:
            root_path: Root directory for the pipeline
        """
        self.root = Path(root_path)
        self.setup_logging()
        self.initialize_directories()
        self.load_configuration()
        
        self.logger.info(f"Pipeline initialized at {self.root}")
        self.logger.info(f"Source PDF: {self.config['source_pdf']}")
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        logs_dir = self.root / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(
                    logs_dir / f'pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
                    encoding='utf-8'
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_directories(self):
        """Create the complete directory structure"""
        directories = [
            'input',
            'input/reference_materials',
            'reference_materials',
            'reference_materials/legal_frameworks',
            'reference_materials/oversight_reports',
            'reference_materials/statistical_baselines',
            'reference_materials/comparative_studies',
            'reference_materials/institutional_contacts',
            'stage_1_extract',
            'stage_2_semantic',
            'stage_3_llm_text',
            'stage_4_visuals',
            'stage_5_validation',
            'final_outputs/summaries',
            'final_outputs/visuals',
            'final_outputs/reports',
            'final_outputs/data',
            'logs',
            'temp',
            'test_output',
            'test_charts'
        ]
        
        for directory in directories:
            dir_path = self.root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {dir_path}")
    
    def load_configuration(self):
        """Load system configuration with extraction optimizations"""
        # Try to load from pipeline_config, fallback to defaults
        try:
            from pipeline_config import config as pipeline_config
            extraction_opts = pipeline_config.extraction_optimization
            self.logger.info("Loaded extraction optimization settings from pipeline_config")
        except Exception as e:
            self.logger.warning(f"Could not load pipeline_config, using defaults: {e}")
            extraction_opts = {
                'use_ocr': True,
                'ocr_threshold': 100,
                'use_concurrent_extraction': True,
                'use_pymupdf': True,
                'use_camelot': True,
                'use_tabula': True,
                'merge_extraction_results': True,
                'quality_scoring': True,
                'save_quality_metrics': True,
            }
        
        self.config = {
            'source_pdf': self.root / 'input' / 'THE-PEOPLES-AUDIT_compressed.pdf',
            'constitution_pdf': self.root / 'input' / 'constitution_of_kenya_2010.pdf',
            'reference_dir': self.root / 'reference_materials',
            'output_dir': self.root / 'final_outputs',
            'stages': {
                '1': self.root / 'stage_1_extract',
                '2': self.root / 'stage_2_semantic',
                '3': self.root / 'stage_3_llm_text',
                '4': self.root / 'stage_4_visuals',
                '5': self.root / 'stage_5_validation'
            },
            'extraction_optimization': extraction_opts
        }
        
        # Verify critical files exist
        if not self.config['source_pdf'].exists():
            self.logger.warning(f"Source PDF not found: {self.config['source_pdf']}")
            self.logger.info("Please ensure THE-PEOPLES-AUDIT_compressed.pdf is in the input directory")
        
        if not self.config['constitution_pdf'].exists():
            self.logger.warning(f"Constitution PDF not found: {self.config['constitution_pdf']}")
            self.logger.info("Please ensure constitution_of_kenya_2010.pdf is in the input directory")

        self.config['reference_input_dir'] = self.root / 'input' / 'reference_materials'
        self.config['reference_extract_dir'] = self.root / 'reference_materials' / 'extracted'
        self.config['reference_extract_dir'].mkdir(parents=True, exist_ok=True)
        
        # Log extraction optimization settings
        self.logger.info("=" * 80)
        self.logger.info("EXTRACTION OPTIMIZATION SETTINGS")
        self.logger.info("=" * 80)
        for key, value in extraction_opts.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("=" * 80)
    
    def execute_pipeline(self):
        """Execute the complete pipeline"""
        self.logger.info("=" * 80)
        self.logger.info("STARTING PEOPLE'S AUDIT PIPELINE")
        self.logger.info("=" * 80)
        
        try:
            # Stage 1: Pure Python Extraction
            self.stage_1_extraction()
            
            # Stage 2: Semantic Tagging
            self.stage_2_semantic()
            
            # Stage 3: Data Consolidation
            self.stage_3_consolidation()
            
            # Stage 4: Constitutional Validation
            self.stage_4_validation()
            
            # Stage 5: LLM Text Generation
            self.stage_5_llm_generation()
            
            # Stage 6: Visualization Generation
            self.stage_6_visualization()
            
            # Stage 7: Final Assembly
            self.stage_7_final_assembly()
            
            self.logger.info("=" * 80)
            self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 80)
            self.logger.info(f"Check final outputs in: {self.config['output_dir']}")
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stage_1_extraction(self):
        """Stage 1: Pure Python PDF Extraction"""
        self.logger.info("Starting Stage 1: PDF Extraction")
        
        try:
            # Import modules
            from extractors.pdf_extractor import PDFExtractor
            from extractors.constitution_extractor import ConstitutionExtractor
            
            # Extract main PDF if exists
            if self.config['source_pdf'].exists():
                # Get extraction optimization settings
                opts = self.config.get('extraction_optimization', {})
                
                # Check available extraction methods
                available_methods = self._check_extraction_methods(opts)
                
                # Determine OCR availability
                use_ocr = opts.get('use_ocr', True) and available_methods.get('ocr', False)
                ocr_threshold = opts.get('ocr_threshold', 100)
                
                if use_ocr:
                    self.logger.info("✓ OCR enabled - will be used for low-quality pages")
                else:
                    self.logger.info("⚠ OCR not available - install pytesseract and Pillow for scanned PDF support")
                
                # Log available methods
                self.logger.info("Available extraction methods:")
                for method, available in available_methods.items():
                    status = "✓" if available else "✗"
                    self.logger.info(f"  {status} {method}")
                
                # Create extractor with all optimizations
                pdf_extractor = PDFExtractor(
                    log_level=logging.INFO,
                    use_ocr=use_ocr,
                    ocr_threshold=ocr_threshold
                )
                
                self.logger.info("Starting enhanced PDF extraction with all available methods...")
                extraction_results = pdf_extractor.extract_all(str(self.config['source_pdf']))
                
                # Save extraction results
                extraction_dir = self.config['stages']['1']
                
                # Save raw text with structure
                with open(extraction_dir / 'raw_text.json', 'w', encoding='utf-8') as f:
                    json.dump(extraction_results['text'], f, indent=2, ensure_ascii=False)
                
                # Save document structure
                with open(extraction_dir / 'document_structure.json', 'w', encoding='utf-8') as f:
                    json.dump(extraction_results['structure'], f, indent=2, ensure_ascii=False)
                
                # Save numeric facts
                with open(extraction_dir / 'numeric_facts.json', 'w', encoding='utf-8') as f:
                    json.dump(extraction_results['numerics'], f, indent=2, ensure_ascii=False)
                
                # Save references
                with open(extraction_dir / 'references.json', 'w', encoding='utf-8') as f:
                    json.dump(extraction_results['references'], f, indent=2, ensure_ascii=False)
                
                # Save metadata
                with open(extraction_dir / 'extraction_metadata.json', 'w', encoding='utf-8') as f:
                    json.dump(extraction_results['metadata'], f, indent=2, ensure_ascii=False)
                
                # Save statistics
                with open(extraction_dir / 'extraction_statistics.json', 'w', encoding='utf-8') as f:
                    json.dump(extraction_results['statistics'], f, indent=2, ensure_ascii=False)
                
                # Save quality metrics if available
                if 'quality_metrics' in extraction_results and opts.get('save_quality_metrics', True):
                    with open(extraction_dir / 'quality_metrics.json', 'w', encoding='utf-8') as f:
                        json.dump(extraction_results['quality_metrics'], f, indent=2, ensure_ascii=False)
                    self.logger.info("✓ Quality metrics saved")
                
                # Log extraction summary
                stats = extraction_results['statistics']
                self.logger.info("=" * 80)
                self.logger.info("STAGE 1 EXTRACTION COMPLETE")
                self.logger.info("=" * 80)
                self.logger.info(f"Pages extracted: {stats.get('total_pages', 0)}")
                self.logger.info(f"Total words: {stats.get('total_words', 0):,}")
                self.logger.info(f"Total paragraphs: {stats.get('total_paragraphs', 0):,}")
                self.logger.info(f"Tables found: {stats.get('tables_count', 0)}")
                self.logger.info(f"Figures found: {stats.get('figures_count', 0)}")
                self.logger.info(f"Constitutional articles: {stats.get('total_constitutional_articles', 0)}")
                self.logger.info(f"Monetary values: {len(extraction_results['numerics'].get('monetary_values', []))}")
                self.logger.info(f"Scandals referenced: {stats.get('total_scandals', 0)}")
                
                # Log quality metrics if available
                if 'quality_metrics' in extraction_results:
                    quality = extraction_results['quality_metrics']
                    self.logger.info("=" * 80)
                    self.logger.info("EXTRACTION QUALITY METRICS")
                    self.logger.info("=" * 80)
                    self.logger.info(f"Overall Quality Score: {quality.get('overall_score', 0):.2%}")
                    self.logger.info(f"Average Words/Page: {quality.get('average_words_per_page', 0):.0f}")
                    self.logger.info(f"Table Coverage: {quality.get('table_coverage', 0):.2%}")
                    self.logger.info(f"Figure Coverage: {quality.get('figure_coverage', 0):.2%}")
                
                self.logger.info(f"Files saved to: {extraction_dir}")
                self.logger.info("=" * 80)
            else:
                self.logger.warning("Source PDF not found. Creating sample data for testing.")
                self.create_sample_stage1_data()
            
            # Extract constitution if available
            if self.config['constitution_pdf'].exists():
                const_extractor = ConstitutionExtractor()
                const_data = const_extractor.extract(str(self.config['constitution_pdf']))
                
                with open(self.root / 'reference_materials' / 'constitution_extracted.json', 'w', encoding='utf-8') as f:
                    json.dump(const_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info("Constitution extraction complete")
                self.logger.info(f"Found {len(const_data.get('articles', []))} constitutional articles")
            else:
                self.logger.warning("Constitution PDF not found. Using sample constitutional data.")
                self.create_sample_constitution_data()

            self.extract_reference_materials()    
                
        except Exception as e:
            self.logger.error(f"Error in Stage 1: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stage_2_semantic(self):
        """Stage 2: Semantic Tagging with Local LLM"""
        self.logger.info("Starting Stage 2: Semantic Tagging")
        
        try:
            # Import modules
            from processors.semantic_tagger import SemanticTagger
            
            # Load Stage 1 outputs
            extraction_dir = self.config['stages']['1']
            raw_text_path = extraction_dir / 'raw_text.json'
            
            if raw_text_path.exists():
                with open(raw_text_path, 'r', encoding='utf-8') as f:
                    raw_text = json.load(f)
                
                # Initialize tagger
                tagger = SemanticTagger()
                
                # Process each paragraph
                tagged_results = tagger.process_all(raw_text)
                
                # Save tagged results
                output_dir = self.config['stages']['2']
                
                with open(output_dir / 'tagged_paragraphs.json', 'w', encoding='utf-8') as f:
                    json.dump(tagged_results['paragraphs'], f, indent=2, ensure_ascii=False)
                
                with open(output_dir / 'recommendations.json', 'w', encoding='utf-8') as f:
                    json.dump(tagged_results['recommendations'], f, indent=2, ensure_ascii=False)
                
                with open(output_dir / 'key_findings.json', 'w', encoding='utf-8') as f:
                    json.dump(tagged_results['findings'], f, indent=2, ensure_ascii=False)
                
                with open(output_dir / 'timeline_events.json', 'w', encoding='utf-8') as f:
                    json.dump(tagged_results['timeline'], f, indent=2, ensure_ascii=False)
                
                with open(output_dir / 'semantic_statistics.json', 'w', encoding='utf-8') as f:
                    stats = {
                        'total_paragraphs': len(tagged_results['paragraphs']),
                        'total_recommendations': len(tagged_results['recommendations']),
                        'total_findings': len(tagged_results['findings']),
                        'total_timeline_events': len(tagged_results['timeline']),
                        'processing_date': datetime.now().isoformat()
                    }
                    json.dump(stats, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Stage 2 complete. Files saved to {output_dir}")
                self.logger.info(f"Processed {len(tagged_results['paragraphs'])} paragraphs")
                self.logger.info(f"Found {len(tagged_results['recommendations'])} recommendations")
            else:
                self.logger.warning("Stage 1 outputs not found. Creating sample semantic data.")
                self.create_sample_stage2_data()
                
        except Exception as e:
            self.logger.error(f"Error in Stage 2: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stage_3_consolidation(self):
        """Stage 3: Data Consolidation"""
        self.logger.info("Starting Stage 3: Data Consolidation")
        
        try:
            # Import modules
            from processors.data_consolidator import DataConsolidator
            
            # Load data from stages 1 and 2
            stage1_dir = self.config['stages']['1']
            stage2_dir = self.config['stages']['2']
            
            # Check if required files exist
            required_files = [
                stage1_dir / 'raw_text.json',
                stage1_dir / 'numeric_facts.json',
                stage1_dir / 'references.json',
                stage2_dir / 'tagged_paragraphs.json',
                stage2_dir / 'recommendations.json'
            ]
            
            if all(f.exists() for f in required_files):
                output_dir = self.config['stages']['4']
                consolidator = DataConsolidator(stage1_dir, stage2_dir, output_dir)
                consolidated_data = consolidator.consolidate_all()
                
                for filename, data in consolidated_data.items():
                    filepath = output_dir / filename
                    if filename.endswith('.json'):
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        self.logger.info(f"Saved {filename} ({len(str(data))} bytes)")
                    elif filename.endswith('.csv'):
                        import pandas as pd
                        if isinstance(data, pd.DataFrame):
                            data.to_csv(filepath, index=False, encoding='utf-8')
                            self.logger.info(f"Saved {filename} ({data.shape[0]} rows)")
                
                self.logger.info(f"Stage 3 complete. Files saved to {output_dir}")
                
                # Verify the missing files were created
                missing_files = ['timeline_data.json', 'constitutional_matrix.json', 'reform_agenda.json']
                for missing_file in missing_files:
                    if (output_dir / missing_file).exists():
                        self.logger.info(f"✓ Created missing file: {missing_file}")
                    else:
                        self.logger.warning(f"✗ Missing file not created: {missing_file}")
                        
            else:
                self.logger.warning("Required input files missing. Creating sample consolidated data.")
                self.create_sample_stage3_data()
                
        except Exception as e:
            self.logger.error(f"Error in Stage 3: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stage_4_validation(self):
        """Stage 4: Constitutional Validation"""
        self.logger.info("Starting Stage 4: Constitutional Validation")
        
        try:
            # Import modules
            from validators.constitutional_validator import ConstitutionalValidator
            
            # Check if required files exist
            stage1_dir = self.config['stages']['1']
            constitution_path = self.root / 'reference_materials' / 'constitution_extracted.json'
            
            if constitution_path.exists() and (stage1_dir / 'references.json').exists():
                validator = ConstitutionalValidator(stage1_dir, constitution_path)
                validation_results = validator.validate_all()
                
                # Save validation results
                output_dir = self.config['stages']['5']
                
                with open(output_dir / 'constitutional_validation.json', 'w', encoding='utf-8') as f:
                    json.dump(validation_results['detailed'], f, indent=2, ensure_ascii=False)
                
                with open(output_dir / 'validation_summary.json', 'w', encoding='utf-8') as f:
                    json.dump(validation_results['summary'], f, indent=2, ensure_ascii=False)
                
                with open(output_dir / 'citizen_constitutional_guide.txt', 'w', encoding='utf-8') as f:
                    f.write(validation_results['guide'])
                
                # Create PDF version if we have reportlab
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    
                    pdf_path = output_dir / 'citizen_constitutional_guide.pdf'
                    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []
                    
                    # Add title
                    title = Paragraph("Your Constitutional Rights: A Citizen's Guide", styles['Title'])
                    story.append(title)
                    story.append(Spacer(1, 12))
                    
                    # Add content
                    for line in validation_results['guide'].split('\n'):
                        if line.strip():
                            if line.startswith('='):
                                # This is a separator
                                story.append(Spacer(1, 6))
                            elif line.startswith('ARTICLE'):
                                story.append(Paragraph(line, styles['Heading2']))
                            elif line.startswith('What it means:'):
                                story.append(Paragraph(line, styles['Normal']))
                            else:
                                story.append(Paragraph(line, styles['Normal']))
                    
                    doc.build(story)
                    self.logger.info(f"Created PDF guide: {pdf_path}")
                    
                except ImportError:
                    self.logger.warning("ReportLab not installed. Skipping PDF generation.")
                
                self.logger.info(f"Stage 4 complete. Files saved to {output_dir}")
                self.logger.info(f"Validated {len(validation_results['detailed'])} constitutional articles")
                
            else:
                self.logger.warning("Required files missing for constitutional validation.")
                self.create_sample_stage4_data()
                
        except Exception as e:
            self.logger.error(f"Error in Stage 4: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stage_5_llm_generation(self):
        """Stage 5: High-quality Text Generation"""
        self.logger.info("Starting Stage 5: LLM Text Generation")
        
        try:
            # Import modules
            from generators.text_generator import TextGenerator
            
            # Load consolidated data
            stage4_dir = self.config['stages']['4']
            
            # Check if required files exist
            required_files = [
                stage4_dir / 'statistics_summary.json',
                stage4_dir / 'reform_agenda.json'
            ]
            
            if all(f.exists() for f in required_files):
                generator = TextGenerator(stage4_dir)
                documents = generator.generate_all_documents()
                
                # Save documents
                output_dir = self.config['stages']['3']
                
                for doc_name, content in documents.items():
                    filepath = output_dir / f"{doc_name}.md"
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.info(f"Generated document: {doc_name}.md")
                
                self.logger.info(f"Stage 5 complete. Files saved to {output_dir}")
                
            else:
                self.logger.warning("Required files missing for text generation.")
                self.create_sample_stage5_data()
                
        except Exception as e:
            self.logger.error(f"Error in Stage 5: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stage_6_visualization(self):
        """Stage 6: Visualization Generation"""
        self.logger.info("Starting Stage 6: Visualization Generation")
        
        try:
            # Import modules
            from visualizers.sankey_generator import SankeyGenerator
            from visualizers.chart_generator import ChartGenerator, ChartConfig
            
            # Load data for visualization
            stage4_dir = self.config['stages']['4']
            
            # Check if required files exist
            sankey_data_path = stage4_dir / 'sankey_data.json'
            charts_data_path = stage4_dir / 'charts_data.json'
            
            if sankey_data_path.exists():
                # Generate Sankey diagram
                sankey_gen = SankeyGenerator()
                
                with open(sankey_data_path, 'r', encoding='utf-8') as f:
                    sankey_data = json.load(f)
                
                sankey_html = sankey_gen.generate_sankey(sankey_data)
                
                # Save Sankey visualizations
                sankey_gen.save_visualizations(sankey_html, stage4_dir)
                self.logger.info("Sankey diagram generated successfully")
            else:
                self.logger.warning("Sankey data not found. Skipping Sankey generation.")
            
            # Generate other charts
            if charts_data_path.exists() or any(f.exists() for f in stage4_dir.glob('*.json')):
                # Create chart configuration
                chart_config = ChartConfig(
                    width=1200,
                    height=800,
                    title_font_size=20,
                    axis_font_size=14,
                    label_font_size=12,
                    export_formats=['html', 'png', 'svg', 'json']
                )
                
                # Generate charts
                chart_gen = ChartGenerator(stage4_dir, config=chart_config)
                charts = chart_gen.generate_all_charts()
                
                self.logger.info(f"Generated {len(charts)} charts")
                
                # List generated files
                chart_output_dir = stage4_dir / 'charts'
                if chart_output_dir.exists():
                    html_files = list(chart_output_dir.glob('html/*.html'))
                    png_files = list(chart_output_dir.glob('png/*.png'))
                    self.logger.info(f"Created {len(html_files)} HTML charts")
                    self.logger.info(f"Created {len(png_files)} PNG charts")
                    
                    # Dashboard
                    dashboard_path = chart_output_dir / 'dashboard.html'
                    if dashboard_path.exists():
                        self.logger.info(f"Dashboard available at: {dashboard_path}")
            else:
                self.logger.warning("Chart data not found. Creating sample charts.")
                self.create_sample_visualizations()
            
            self.logger.info("Stage 6 complete. Visualizations generated")
            
        except Exception as e:
            self.logger.error(f"Error in Stage 6: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stage_7_final_assembly(self):
        """Stage 7: Final Assembly"""
        self.logger.info("Starting Stage 7: Final Assembly")
        
        try:
            # Create final outputs directory
            final_dir = self.config['output_dir']
            final_dir.mkdir(exist_ok=True)
            
            # Copy and organize all final outputs
            sources = {
                'summaries': self.config['stages']['3'],
                'visuals': self.config['stages']['4'],
                'reports': self.config['stages']['5'],
                'data': self.config['stages']['4']  # Contains consolidated data
            }
            
            for target, source in sources.items():
                target_dir = final_dir / target
                target_dir.mkdir(exist_ok=True)
                
                # Copy relevant files
                if source.exists():
                    for file in source.iterdir():
                        if file.is_file() and not file.name.startswith('.'):
                            shutil.copy2(file, target_dir / file.name)
                            self.logger.debug(f"Copied {file.name} to {target}")
            
            # Create additional consolidated files
            self.create_final_consolidated_files(final_dir)
            
            # Create dashboard
            self.create_dashboard(final_dir)
            
            # Create README
            self.create_readme(final_dir)
            
            # Create manifest
            self.create_manifest(final_dir)
            
            self.logger.info(f"Stage 7 complete. Final outputs in {final_dir}")
            
            # Print summary
            self.print_final_summary(final_dir)
            
        except Exception as e:
            self.logger.error(f"Error in Stage 7: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _check_extraction_methods(self, opts: dict) -> dict:
        """Check which extraction methods are available"""
        methods = {
            'pypdf2': True,  # Always available (required)
            'pdfplumber': True,  # Always available (required)
            'pymupdf': False,
            'ocr': False,
            'camelot': False,
            'tabula': False,
        }
        
        # Check PyMuPDF
        if opts.get('use_pymupdf', True):
            try:
                import fitz
                methods['pymupdf'] = True
            except ImportError:
                pass
        
        # Check OCR
        if opts.get('use_ocr', True):
            try:
                import pytesseract
                from PIL import Image
                methods['ocr'] = True
            except ImportError:
                pass
        
        # Check Camelot
        if opts.get('use_camelot', True):
            try:
                import camelot
                methods['camelot'] = True
            except ImportError:
                pass
        
        # Check Tabula
        if opts.get('use_tabula', True):
            try:
                import tabula
                methods['tabula'] = True
            except ImportError:
                pass
        
        return methods
    
    def extract_reference_materials(self):
        """Extract all reference PDFs from input/reference_materials recursively with optimizations"""
        from extractors.pdf_extractor import PDFExtractor

        ref_root = self.config['reference_input_dir']
        out_root = self.config['reference_extract_dir']

        if not ref_root.exists():
            self.logger.info("No input/reference_materials directory found. Skipping reference extraction.")
            return

        # Use same optimization settings as main extraction
        opts = self.config.get('extraction_optimization', {})
        available_methods = self._check_extraction_methods(opts)
        use_ocr = opts.get('use_ocr', True) and available_methods.get('ocr', False)
        
        extractor = PDFExtractor(
            log_level=logging.INFO,
            use_ocr=use_ocr,
            ocr_threshold=opts.get('ocr_threshold', 100)
        )
        index = {}

        pdf_files = list(ref_root.rglob('*.pdf'))
        if not pdf_files:
            self.logger.info("No PDF files found in reference_materials. Skipping.")
            return
        
        self.logger.info(f"Found {len(pdf_files)} reference PDF(s) to extract")

        for file_path in pdf_files:
            if not file_path.is_file():
                continue

            try:
                self.logger.info(f"Extracting reference document: {file_path.name}")

                result = extractor.extract_all(str(file_path))

                relative = file_path.relative_to(ref_root).with_suffix('')
                target_dir = out_root / relative
                target_dir.mkdir(parents=True, exist_ok=True)

                with open(target_dir / 'raw_text.json', 'w', encoding='utf-8') as f:
                    json.dump(result['text'], f, indent=2, ensure_ascii=False)

                with open(target_dir / 'metadata.json', 'w', encoding='utf-8') as f:
                    json.dump(result['metadata'], f, indent=2, ensure_ascii=False)
                
                # Save quality metrics if available
                if 'quality_metrics' in result and opts.get('save_quality_metrics', True):
                    with open(target_dir / 'quality_metrics.json', 'w', encoding='utf-8') as f:
                        json.dump(result['quality_metrics'], f, indent=2, ensure_ascii=False)

                index[str(relative)] = {
                    'source_file': str(file_path),
                    'pages': result['statistics'].get('total_pages', 0),
                    'words': result['statistics'].get('total_words', 0),
                    'quality_score': result.get('quality_metrics', {}).get('overall_score', 0.0)
                }

            except Exception as e:
                self.logger.error(f"Reference extraction failed for {file_path}: {e}")

        with open(out_root / 'reference_index.json', 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Reference extraction complete: {len(index)} documents processed")

    
    def create_final_consolidated_files(self, final_dir: Path):
        """Create final consolidated files"""
        try:
            # Consolidated data file
            consolidated_data = {}
            
            # Gather data from all stages
            stages = ['1', '2', '3', '4', '5']
            for stage in stages:
                stage_dir = self.config['stages'][stage]
                if stage_dir.exists():
                    for json_file in stage_dir.glob('*.json'):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                key = f"stage_{stage}_{json_file.stem}"
                                consolidated_data[key] = data
                        except:
                            pass
            
            # Save consolidated data
            with open(final_dir / 'data' / 'all_consolidated_data.json', 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
            
            # Create Excel summary if pandas is available
            try:
                import pandas as pd
                
                # Create summary DataFrame
                summary_data = []
                
                # Add key statistics
                stats_path = self.config['stages']['4'] / 'statistics_summary.json'
                if stats_path.exists():
                    with open(stats_path, 'r', encoding='utf-8') as f:
                        stats = json.load(f)
                    
                    for key, value in stats.items():
                        if key != 'generated_date':
                            summary_data.append({
                                'Category': 'Key Statistics',
                                'Metric': key.replace('_', ' ').title(),
                                'Value': value,
                                'Source': 'People\'s Audit'
                            })
                
                # Add to Excel
                if summary_data:
                    df = pd.DataFrame(summary_data)
                    excel_path = final_dir / 'data' / 'Kenya_Governance_By_The_Numbers.xlsx'
                    
                    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Summary', index=False)
                        
                        # Add detailed sheets if available
                        detailed_files = [
                            ('corruption_cases.csv', 'Corruption Cases'),
                            ('debt_analysis.csv', 'Debt Analysis'),
                            ('budget_analysis.csv', 'Budget Analysis')
                        ]
                        
                        for filename, sheetname in detailed_files:
                            filepath = self.config['stages']['4'] / filename
                            if filepath.exists():
                                try:
                                    detail_df = pd.read_csv(filepath)
                                    detail_df.to_excel(writer, sheet_name=sheetname, index=False)
                                except:
                                    pass
                    
                    self.logger.info(f"Created Excel summary: {excel_path}")
                    
            except ImportError:
                self.logger.warning("Pandas not installed. Skipping Excel generation.")
                
        except Exception as e:
            self.logger.error(f"Error creating consolidated files: {str(e)}")
    
    def create_dashboard(self, final_dir: Path):
        """Create HTML dashboard"""
        try:
            dashboard_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People\'s Audit Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; background: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); }
        header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #eee; }
        h1 { color: #2c3e50; font-size: 2.8rem; margin-bottom: 10px; background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .subtitle { color: #7f8c8d; font-size: 1.2rem; margin-bottom: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); }
        .stat-value { font-size: 2.5rem; font-weight: bold; margin-bottom: 5px; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .section { margin: 40px 0; }
        .section-title { color: #2c3e50; font-size: 1.8rem; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }
        .file-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .file-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); border-left: 4px solid #3498db; transition: transform 0.3s ease; }
        .file-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); }
        .file-title { color: #2c3e50; font-size: 1.2rem; margin-bottom: 10px; }
        .file-desc { color: #7f8c8d; font-size: 0.9rem; margin-bottom: 15px; }
        .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; font-weight: 500; transition: background 0.3s ease; }
        .btn:hover { background: #2980b9; }
        .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin: 20px 0; }
        .chart-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); }
        .chart-title { color: #2c3e50; font-size: 1.2rem; margin-bottom: 15px; }
        footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #7f8c8d; font-size: 0.9rem; }
        @media (max-width: 768px) { .container { padding: 15px; } h1 { font-size: 2rem; } .chart-grid { grid-template-columns: 1fr; } }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-chart-line"></i> People\'s Audit Dashboard</h1>
            <p class="subtitle">Comprehensive Analysis of Kenya\'s Economic Governance Crisis</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="total-debt">KSh 12.05T</div>
                    <div class="stat-label">Total Public Debt (2025)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="debt-ratio">56%</div>
                    <div class="stat-label">Debt Service to Revenue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="corruption-loss">KSh 800B</div>
                    <div class="stat-label">Annual Corruption Loss</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="food-insecure">15.5M</div>
                    <div class="stat-label">Food Insecure Kenyans</div>
                </div>
            </div>
        </header>
        
        <div class="section">
            <h2 class="section-title"><i class="fas fa-file-alt"></i> Key Documents</h2>
            <div class="file-grid">
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-users"></i> Citizen\'s Summary</h3>
                    <p class="file-desc">Simple English guide for ordinary Kenyans explaining the economic crisis</p>
                    <a href="summaries/citizen_summary.md" class="btn" download><i class="fas fa-download"></i> Download</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-chart-bar"></i> Data Compendium</h3>
                    <p class="file-desc">Complete statistics and analysis in Excel format with all data points</p>
                    <a href="data/Kenya_Governance_By_The_Numbers.xlsx" class="btn" download><i class="fas fa-download"></i> Download</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-gavel"></i> Constitutional Guide</h3>
                    <p class="file-desc">Your rights under the Constitution and how they\'re being violated</p>
                    <a href="reports/citizen_constitutional_guide.txt" class="btn" download><i class="fas fa-download"></i> Download</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-hands-helping"></i> Action Handbook</h3>
                    <p class="file-desc">What you can do to demand accountability and fight corruption</p>
                    <a href="summaries/action_handbook.md" class="btn" download><i class="fas fa-download"></i> Download</a>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title"><i class="fas fa-chart-pie"></i> Visualizations</h2>
            <div class="chart-grid">
                <div class="chart-container">
                    <h3 class="chart-title">Debt Growth Timeline (2014-2025)</h3>
                    <img src="visuals/charts/png/debt_timeline.png" alt="Debt Timeline" style="width: 100%; border-radius: 5px;">
                    <p style="color: #7f8c8d; font-size: 0.9rem; margin-top: 10px;">Kenya\'s public debt grew from KSh 2.4T to KSh 12.05T in 11 years</p>
                </div>
                <div class="chart-container">
                    <h3 class="chart-title">Corruption Losses by Sector</h3>
                    <img src="visuals/charts/png/corruption_by_sector.png" alt="Corruption by Sector" style="width: 100%; border-radius: 5px;">
                    <p style="color: #7f8c8d; font-size: 0.9rem; margin-top: 10px;">Estimated annual losses across different government sectors</p>
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="final_outputs/dashboard.html" class="btn" target="_blank"><i class="fas fa-expand"></i> View Interactive Dashboard</a>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title"><i class="fas fa-database"></i> Data Files</h2>
            <div class="file-grid">
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-code"></i> JSON Data</h3>
                    <p class="file-desc">Complete extracted data in JSON format for developers and researchers</p>
                    <a href="data/all_consolidated_data.json" class="btn"><i class="fas fa-eye"></i> View Data</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-project-diagram"></i> Sankey Diagram</h3>
                    <p class="file-desc">Interactive visualization of public fund flows and corruption</p>
                    <a href="visuals/sankey.html" class="btn" target="_blank"><i class="fas fa-external-link-alt"></i> Open Interactive</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-clipboard-list"></i> Validation Reports</h3>
                    <p class="file-desc">Constitutional violation analysis and legal compliance reports</p>
                    <a href="reports/constitutional_validation.json" class="btn"><i class="fas fa-eye"></i> View Report</a>
                </div>
                <div class="file-card">
                    <h3 class="file-title"><i class="fas fa-cogs"></i> Reform Agenda</h3>
                    <p class="file-desc">Priority actions and governance reforms needed</p>
                    <a href="data/reform_agenda.json" class="btn"><i class="fas fa-eye"></i> View Agenda</a>
                </div>
            </div>
        </div>
        
        <footer>
            <p>People\'s Audit Pipeline | Data Source: Okoa Uchumi Campaign / TISA</p>
            <p>Generated: {current_date} | Pipeline Version: 1.0</p>
            <p style="margin-top: 10px; font-size: 0.8rem; opacity: 0.7;">
                <i class="fas fa-info-circle"></i> This dashboard provides access to all analysis outputs. Use the links above to download or view specific files.
            </p>
        </footer>
    </div>
    
    <script>
        // Load dynamic data if available
        fetch(\'data/statistics_summary.json\')
            .then(response => response.json())
            .then(data => {
                if (data.total_debt) {
                    document.getElementById(\'total-debt\').textContent = data.total_debt;
                }
                if (data.debt_service_ratio) {
                    document.getElementById(\'debt-ratio\').textContent = data.debt_service_ratio;
                }
                if (data.corruption_loss_annual) {
                    document.getElementById(\'corruption-loss\').textContent = data.corruption_loss_annual;
                }
                if (data.food_insecure) {
                    document.getElementById(\'food-insecure\').textContent = data.food_insecure;
                }
            })
            .catch(error => console.log(\'Error loading statistics:\', error));
    </script>
</body>
</html>'''
            
            # Fill in current date
            current_date = datetime.now().strftime("%B %d, %Y %H:%M")
            dashboard_html = dashboard_template.replace('{current_date}', current_date)
            
            # Save dashboard
            dashboard_path = final_dir / 'dashboard.html'
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            
            self.logger.info(f"Dashboard created: {dashboard_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {str(e)}")
    
    def create_readme(self, final_dir: Path):
        """Create README documentation"""
        readme_content = f"""# People's Audit Pipeline Outputs

## Overview
This directory contains the complete outputs from the People's Audit pipeline analysis. 
The audit examines Kenya's economic governance, corruption, and constitutional violations.

## Generation Details
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Pipeline Version**: 1.0
- **Source Document**: THE-PEOPLES-AUDIT_compressed.pdf
- **Constitution**: Constitution of Kenya 2010

## Directory Structure

### summaries/
- `citizen_summary.md`: Simple English guide for ordinary Kenyans
- `executive_summary.md`: Brief overview for policymakers
- `action_handbook.md`: Practical steps citizens can take

### data/
- `Kenya_Governance_By_The_Numbers.xlsx`: Complete dataset in Excel format
- `statistics_summary.json`: Key statistics in JSON format
- `constitutional_violations.json`: Documented constitutional violations
- `reform_agenda.json`: Priority governance reforms
- `all_consolidated_data.json`: All extracted data combined

### visuals/
- `sankey.html`: Interactive Sankey diagram of fund flows
- `charts/`: Directory containing all generated charts
  - `html/`: Interactive HTML charts
  - `png/`: Static PNG images
  - `svg/`: Vector SVG images
  - `dashboard.html`: Interactive charts dashboard
- `debt_timeline.png`: Chart showing debt growth 2014-2025
- `corruption_by_sector.png`: Map of corruption by sector

### reports/
- `citizen_constitutional_guide.txt`: Constitutional rights guide
- `constitutional_validation.json`: Constitutional validation findings
- `validation_summary.json`: Summary of constitutional violations

## Key Findings

### 1. Debt Crisis
- Kenya's debt grew from KSh 2.4 trillion (2014) to KSh 12.05 trillion (2025)
- 56% of government revenue goes to debt service
- Each Kenyan owes approximately KSh 240,000 in public debt

### 2. Corruption
- Estimated KSh 800 billion lost annually to corruption
- Only 6 of 47 counties received clean audit opinions (2023/24)
- Conviction rate for corruption cases: <10%

### 3. Human Impact
- 15.5 million Kenyans food insecure
- 20 million below poverty line
- 1.7 million university graduates unemployed
- 200+ killed in 2024 protests demanding accountability

### 4. Constitutional Violations
- Articles 1, 35, 43 routinely violated
- Right to information requests ignored
- Social and economic rights unfulfilled

## How to Use These Materials

### For Citizens:
1. Start with `summaries/citizen_summary.md`
2. Use `summaries/action_handbook.md` for practical steps
3. Refer to `reports/citizen_constitutional_guide.txt` for legal rights

### For Researchers:
1. Use `data/` directory for complete datasets
2. Analyze `reports/` for detailed findings
3. Reference `visuals/` for graphical representations

### For Media:
1. Use `summaries/executive_summary.md` for quick overview
2. Reference key statistics from `data/statistics_summary.json`
3. Use visuals from `visuals/` for reporting

## Data Sources
All data is extracted from:
1. "THE-PEOPLES-AUDIT: From hustle to hardship" (December 8, 2025)
2. Constitution of Kenya 2010
3. Official government reports (OAG, CoB, KNBS)

## Pipeline Architecture
The analysis was conducted through a 7-stage pipeline:

1. **PDF Extraction**: Raw text and structure extraction
2. **Semantic Tagging**: Categorization and tagging of content
3. **Data Consolidation**: Aggregation and structuring of data
4. **Constitutional Validation**: Analysis against constitutional provisions
5. **Text Generation**: Creation of human-readable reports
6. **Visualization**: Chart and diagram generation
7. **Final Assembly**: Packaging of all outputs

## Contact
For questions or additional analysis, contact the Okoa Uchumi Coalition.

## License
This work is licensed under Creative Commons Attribution 4.0 International.

---
Generated by People's Audit Pipeline v1.0
"""
        
        with open(final_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def create_manifest(self, final_dir: Path):
        """Create manifest file listing all outputs"""
        manifest = {
            'generated_date': datetime.now().isoformat(),
            'pipeline_version': '1.0',
            'files': [],
            'statistics': {}
        }
        
        # Count files by type
        file_types = {}
        total_size = 0
        
        for root, dirs, files in os.walk(final_dir):
            for file in files:
                filepath = Path(root) / file
                relative_path = filepath.relative_to(final_dir)
                file_type = filepath.suffix.lower()
                file_size = filepath.stat().st_size
                
                manifest['files'].append({
                    'path': str(relative_path),
                    'type': file_type,
                    'size_bytes': file_size,
                    'size_human': self._human_readable_size(file_size)
                })
                
                file_types[file_type] = file_types.get(file_type, 0) + 1
                total_size += file_size
        
        manifest['statistics'] = {
            'total_files': len(manifest['files']),
            'file_types': file_types,
            'total_size_bytes': total_size,
            'total_size_human': self._human_readable_size(total_size)
        }
        
        with open(final_dir / 'manifest.json', 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def print_final_summary(self, final_dir: Path):
        """Print final summary of outputs"""
        self.logger.info("=" * 80)
        self.logger.info("FINAL OUTPUT SUMMARY")
        self.logger.info("=" * 80)
        
        # Count files by directory
        for subdir in ['summaries', 'data', 'visuals', 'reports']:
            dir_path = final_dir / subdir
            if dir_path.exists():
                files = list(dir_path.glob('*'))
                files = [f for f in files if f.is_file()]
                self.logger.info(f"{subdir}/: {len(files)} files")
                
                # List key files
                for file in sorted(files)[:5]:  # First 5 files
                    size = self._human_readable_size(file.stat().st_size)
                    self.logger.info(f"  - {file.name} ({size})")
                
                if len(files) > 5:
                    self.logger.info(f"  ... and {len(files) - 5} more files")
        
        # Special files
        special_files = [
            ('dashboard.html', 'Interactive dashboard'),
            ('README.md', 'Documentation'),
            ('manifest.json', 'File manifest')
        ]
        
        for filename, description in special_files:
            filepath = final_dir / filename
            if filepath.exists():
                size = self._human_readable_size(filepath.stat().st_size)
                self.logger.info(f"{filename}: {description} ({size})")
        
        self.logger.info("=" * 80)
        self.logger.info(f"All outputs available in: {final_dir}")
        self.logger.info(f"Open {final_dir / 'dashboard.html'} in your browser to explore")
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    # Sample data creation methods for when real data is missing
    def create_sample_stage1_data(self):
        """Create sample Stage 1 data for testing"""
        sample_data = {
            'text': {
                'page_1': {
                    'page_number': 1,
                    'text': 'Sample page text for testing. This is the People\'s Audit document.',
                    'paragraphs': ['Sample paragraph 1', 'Sample paragraph 2'],
                    'figures': [],
                    'tables': [],
                    'monetary_values': [{'amount': 1000000000, 'unit': 'KSh', 'context': 'Sample debt amount'}],
                    'percentages': [{'value': 56, 'context': 'Debt service ratio'}],
                    'years': [2025, 2024],
                    'constitutional_articles': ['43', '35'],
                    'legal_references': ['Public Finance Management Act'],
                    'scandals': [{'keyword': 'corruption', 'context': 'Sample corruption scandal'}]
                }
            }
        }
        
        stage1_dir = self.config['stages']['1']
        with open(stage1_dir / 'raw_text.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info("Created sample Stage 1 data")
    
    def create_sample_constitution_data(self):
        """Create sample constitutional data"""
        sample_data = {
            'metadata': {'total_articles': 191},
            'articles': [
                {'article_number': '43', 'title': 'Economic and social rights', 'full_text': 'Every person has the right...'},
                {'article_number': '35', 'title': 'Access to information', 'full_text': 'Every citizen has the right...'}
            ]
        }
        
        with open(self.root / 'reference_materials' / 'constitution_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info("Created sample constitutional data")
    
    def create_sample_stage2_data(self):
        """Create sample Stage 2 data"""
        sample_data = {
            'paragraphs': [
                {'paragraph_id': 'para_000001', 'text': 'Sample paragraph', 'tags': ['finding'], 'category': 'finding'}
            ],
            'recommendations': [
                {'id': 'rec_001', 'text': 'Sample recommendation', 'priority': 'high'}
            ],
            'findings': [
                {'id': 'find_001', 'text': 'Sample finding', 'severity': 'high'}
            ],
            'timeline': [
                {'year': '2025', 'event': 'Sample event'}
            ]
        }
        
        stage2_dir = self.config['stages']['2']
        with open(stage2_dir / 'tagged_paragraphs.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data['paragraphs'], f, indent=2, ensure_ascii=False)
        
        with open(stage2_dir / 'recommendations.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data['recommendations'], f, indent=2, ensure_ascii=False)
        
        with open(stage2_dir / 'key_findings.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data['findings'], f, indent=2, ensure_ascii=False)
        
        with open(stage2_dir / 'timeline_events.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data['timeline'], f, indent=2, ensure_ascii=False)
        
        self.logger.info("Created sample Stage 2 data")
    
    def create_sample_stage3_data(self):
        """Create the missing Stage 3 data files"""
        stage4_dir = self.config['stages']['4']
        
        # Create timeline_data.json
        timeline_data = {
            'events': [
                {'year': '2014', 'event': 'Debt: KSh 2.4T', 'category': 'debt'},
                {'year': '2025', 'event': 'Debt: KSh 12.05T', 'category': 'debt'}
            ]
        }
        
        with open(stage4_dir / 'timeline_data.json', 'w', encoding='utf-8') as f:
            json.dump(timeline_data, f, indent=2, ensure_ascii=False)
        
        # Create constitutional_matrix.json
        constitutional_matrix = {
            '43': {
                'count': 15,
                'violations': [
                    {'text': 'Right to food violated for 15.5 million Kenyans', 'page': 1}
                ]
            },
            '35': {
                'count': 12,
                'violations': [
                    {'text': 'Information requests denied or ignored', 'page': 2}
                ]
            }
        }
        
        with open(stage4_dir / 'constitutional_matrix.json', 'w', encoding='utf-8') as f:
            json.dump(constitutional_matrix, f, indent=2, ensure_ascii=False)
        
        # Create reform_agenda.json
        reform_agenda = {
            'fiscal_governance': [
                {'text': 'Publish all debt contracts', 'priority': 'high'}
            ],
            'anti_corruption': [
                {'text': 'Fast-track corruption cases', 'priority': 'high'}
            ]
        }
        
        with open(stage4_dir / 'reform_agenda.json', 'w', encoding='utf-8') as f:
            json.dump(reform_agenda, f, indent=2, ensure_ascii=False)
        
        # Create other expected files
        charts_data = {
            'debt_timeline': {
                'title': 'Kenya Public Debt Growth',
                'data': {
                    'years': ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'],
                    'debt_amounts': [2.4, 3.1, 3.7, 4.4, 5.2, 6.0, 7.0, 8.1, 9.3, 10.5, 11.6, 12.05]
                }
            }
        }
        
        with open(stage4_dir / 'charts_data.json', 'w', encoding='utf-8') as f:
            json.dump(charts_data, f, indent=2, ensure_ascii=False)
        
        statistics_summary = {
            'total_debt': '12.05 trillion',
            'debt_service_ratio': '56%',
            'corruption_loss_annual': '800 billion',
            'food_insecure': '15.5 million',
            'youth_unemployed': '1.7 million',
            'generated_date': datetime.now().isoformat()
        }
        
        with open(stage4_dir / 'statistics_summary.json', 'w', encoding='utf-8') as f:
            json.dump(statistics_summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info("Created sample Stage 3 data including missing files")
    
    def create_sample_stage4_data(self):
        """Create sample Stage 4 data"""
        stage5_dir = self.config['stages']['5']
        
        validation_data = {
            'detailed': {
                '43': {
                    'article_number': '43',
                    'article_text': 'Economic and social rights...',
                    'violation_count': 15
                }
            },
            'summary': {
                'total_articles_referenced': 10,
                'articles_with_violations': 8
            },
            'guide': 'Sample constitutional guide text'
        }
        
        with open(stage5_dir / 'constitutional_validation.json', 'w', encoding='utf-8') as f:
            json.dump(validation_data['detailed'], f, indent=2, ensure_ascii=False)
        
        with open(stage5_dir / 'validation_summary.json', 'w', encoding='utf-8') as f:
            json.dump(validation_data['summary'], f, indent=2, ensure_ascii=False)
        
        with open(stage5_dir / 'citizen_constitutional_guide.txt', 'w', encoding='utf-8') as f:
            f.write(validation_data['guide'])
        
        self.logger.info("Created sample Stage 4 data")
    
    def create_sample_stage5_data(self):
        """Create sample Stage 5 data"""
        stage3_dir = self.config['stages']['3']
        
        sample_docs = {
            'citizen_summary': '# Sample Citizen Summary\n\nThis is a sample document.',
            'executive_summary': '# Sample Executive Summary\n\nFor policymakers.',
            'action_handbook': '# Sample Action Handbook\n\nSteps citizens can take.'
        }
        
        for doc_name, content in sample_docs.items():
            with open(stage3_dir / f'{doc_name}.md', 'w', encoding='utf-8') as f:
                f.write(content)
        
        self.logger.info("Created sample Stage 5 data")
    
    def create_sample_visualizations(self):
        """Create sample visualizations"""
        stage4_dir = self.config['stages']['4']
        
        # Create sample sankey data
        sankey_data = {
            'nodes': [
                {'name': 'Government Revenue', 'category': 'source'},
                {'name': 'Corruption Losses', 'category': 'flow'},
                {'name': 'Health', 'category': 'destination'}
            ],
            'links': [
                {'source': 'Government Revenue', 'target': 'Corruption Losses', 'value': 800},
                {'source': 'Government Revenue', 'target': 'Health', 'value': 150}
            ]
        }
        
        with open(stage4_dir / 'sankey_data.json', 'w', encoding='utf-8') as f:
            json.dump(sankey_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info("Created sample visualization data")

def main():
    """Main entry point for the pipeline"""
    print("=" * 80)
    print("PEOPLE'S AUDIT PIPELINE")
    print("=" * 80)
    print("Comprehensive Analysis of Kenya's Economic Governance Crisis")
    print()
    
    # Get root directory
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        # Default to current directory
        root_path = os.getcwd()
    
    print(f"Root directory: {root_path}")
    print()
    
    try:
        # Initialize and run pipeline
        pipeline = PeopleAuditPipeline(root_path)
        pipeline.execute_pipeline()
        
        print()
        print("=" * 80)
        print("PIPELINE EXECUTION COMPLETE!")
        print("=" * 80)
        print(f"Check the following directories for outputs:")
        print(f"  - Final outputs: {root_path}/final_outputs/")
        print(f"  - Charts and visualizations: {root_path}/stage_4_visuals/")
        print(f"  - Logs: {root_path}/logs/")
        print()
        print(f"Open {root_path}/final_outputs/dashboard.html in your browser")
        print("to explore all outputs interactively.")
        print()
        
    except Exception as e:
        print(f"ERROR: Pipeline execution failed: {str(e)}")
        print("Check the log files for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()