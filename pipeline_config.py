# config.py
import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    
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
        
        return cls(
            root_dir=root,
            input_dir=Path(os.getenv('INPUT_DIR', root / "input")),
            reference_dir=Path(os.getenv('REFERENCE_DIR', root / "reference_materials")),
            output_dir=Path(os.getenv('OUTPUT_DIR', root / "final_outputs")),
            logs_dir=Path(os.getenv('LOGS_DIR', root / "logs")),
            chunk_size=int(os.getenv('CHUNK_SIZE', 1000)),
            max_workers=int(os.getenv('MAX_WORKERS', 4))
        )

# Create default config
config = PipelineConfig()