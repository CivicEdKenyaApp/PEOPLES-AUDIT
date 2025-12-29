# config.py
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PipelineConfig:
    """Enhanced Pipeline configuration with extraction optimizations"""
    
    # Directories
    root_dir: Path = Path("D:\\CEKA\\Scripts PROJECTS\\PEOPLES_AUDIT")
    input_dir: Path = root_dir / "input"
    reference_dir: Path = root_dir / "reference_materials"
    output_dir: Path = root_dir / "final_outputs"
    logs_dir: Path = root_dir / "logs"
    
    # Files
    source_pdf: Path = input_dir / "THE-PEOPLES-AUDIT_compressed.pdf"
    constitution_pdf: Path = input_dir / "constitution_of_kenya_2010.pdf"
    
    # Processing
    chunk_size: int = 1000  # Characters per chunk for processing
    max_workers: int = 4    # Parallel processing threads
    
    # Enhanced Extraction Settings
    extraction_optimization: Dict[str, Any] = field(default_factory=lambda: {
        'use_ocr': True,              # Enable OCR for low-quality pages
        'ocr_threshold': 100,          # Trigger OCR if page has < 100 words
        'use_concurrent_extraction': True,  # Run multiple extraction methods in parallel
        'use_pymupdf': True,           # Use PyMuPDF for better text extraction
        'use_camelot': True,           # Use Camelot for table extraction
        'use_tabula': True,            # Use Tabula as fallback for tables
        'merge_extraction_results': True,  # Merge results from multiple methods
        'quality_scoring': True,        # Calculate quality scores
        'save_quality_metrics': True,   # Save quality metrics to file
    })
    
    # Visualization
    chart_width: int = 1200
    chart_height: int = 800
    sankey_height: int = 1000
    
    # Output formats
    generate_pdf: bool = True
    generate_excel: bool = True
    generate_html: bool = True
    generate_images: bool = True
    
    # Quality settings
    min_paragraph_length: int = 50
    confidence_threshold: float = 0.7
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables"""
        root = Path(os.getenv('PEOPLES_AUDIT_ROOT', cls.root_dir))
        
        # Extract optimization settings from env
        extraction_opts = {
            'use_ocr': os.getenv('USE_OCR', 'true').lower() == 'true',
            'ocr_threshold': int(os.getenv('OCR_THRESHOLD', '100')),
            'use_concurrent_extraction': os.getenv('USE_CONCURRENT_EXTRACTION', 'true').lower() == 'true',
            'use_pymupdf': os.getenv('USE_PYMUPDF', 'true').lower() == 'true',
            'use_camelot': os.getenv('USE_CAMELOT', 'true').lower() == 'true',
            'use_tabula': os.getenv('USE_TABULA', 'true').lower() == 'true',
            'merge_extraction_results': os.getenv('MERGE_EXTRACTION_RESULTS', 'true').lower() == 'true',
            'quality_scoring': os.getenv('QUALITY_SCORING', 'true').lower() == 'true',
            'save_quality_metrics': os.getenv('SAVE_QUALITY_METRICS', 'true').lower() == 'true',
        }
        
        return cls(
            root_dir=root,
            input_dir=Path(os.getenv('INPUT_DIR', root / "input")),
            reference_dir=Path(os.getenv('REFERENCE_DIR', root / "reference_materials")),
            output_dir=Path(os.getenv('OUTPUT_DIR', root / "final_outputs")),
            logs_dir=Path(os.getenv('LOGS_DIR', root / "logs")),
            chunk_size=int(os.getenv('CHUNK_SIZE', 1000)),
            max_workers=int(os.getenv('MAX_WORKERS', 4)),
            extraction_optimization=extraction_opts
        )

# Create default config
config = PipelineConfig()
