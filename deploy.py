# deploy.py - Production Deployment Script
import shutil
import sys
from pathlib import Path

def deploy_production():
    """Deploy pipeline to production environment"""
    
    source_root = Path("D:\\CEKA\\Scripts PROJECTS\\PEOPLES_AUDIT")
    deploy_root = Path("D:\\CEKA\\Scripts PROJECTS\\PEOPLES_AUDIT_PRODUCTION")
    
    print(f"Deploying from {source_root} to {deploy_root}")
    
    # Create production directory structure
    deploy_root.mkdir(exist_ok=True)
    
    # Copy essential files
    essential_files = [
        'main.py',
        'requirements.txt',
        'setup.sh',
        'README.md',
        'config.py'
    ]
    
    essential_dirs = [
        'extractors',
        'processors',
        'validators',
        'generators',
        'visualizers'
    ]
    
    print("Copying essential files...")
    for file in essential_files:
        source = source_root / file
        if source.exists():
            shutil.copy2(source, deploy_root / file)
            print(f"  ✓ {file}")
    
    print("\nCopying module directories...")
    for dir_name in essential_dirs:
        source_dir = source_root / dir_name
        if source_dir.exists():
            dest_dir = deploy_root / dir_name
            shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
            print(f"  ✓ {dir_name}/")
    
    # Create production-specific directories
    print("\nCreating production directories...")
    (deploy_root / 'data').mkdir(exist_ok=True)
    (deploy_root / 'logs').mkdir(exist_ok=True)
    (deploy_root / 'config').mkdir(exist_ok=True)
    
    # Create production configuration
    print("\nCreating production configuration...")
    prod_config = f"""
# Production Configuration
import os

DEBUG = False
LOG_LEVEL = 'INFO'
DATA_DIR = '{deploy_root / 'data'}'
LOG_DIR = '{deploy_root / 'logs'}'

# Performance settings
MAX_WORKERS = 8
CHUNK_SIZE = 2000
CACHE_ENABLED = True

# Output settings
GENERATE_ALL_FORMATS = True
COMPRESS_OUTPUTS = True
BACKUP_ENABLED = True

# Security
ENCRYPT_SENSITIVE_DATA = True
LOG_SANITIZATION = True
"""
    
    with open(deploy_root / 'config' / 'production.py', 'w') as f:
        f.write(prod_config)
    
    # Create startup script
    print("\nCreating startup script...")
    startup_script = f"""#!/bin/bash
# startup.sh - Production Startup Script

cd "{deploy_root}"

# Activate virtual environment
source "{deploy_root}\\venv\\Scripts\\activate"

# Set environment variables
export PEOPLES_AUDIT_ROOT="{deploy_root}"
export LOG_LEVEL=INFO
export MAX_WORKERS=8

# Run pipeline
python main.py

# Deactivate virtual environment
deactivate
"""
    
    with open(deploy_root / 'startup.sh', 'w') as f:
        f.write(startup_script)
    
    print(f"\nDeployment complete!")
    print(f"Production environment ready at: {deploy_root}")
    print(f"\nTo start production pipeline:")
    print(f"1. cd {deploy_root}")
    print(f"2. bash startup.sh")

if __name__ == "__main__":
    deploy_production()