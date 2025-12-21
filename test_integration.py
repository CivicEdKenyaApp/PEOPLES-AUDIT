# test_integration.py
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path("D:\\CEKA\\Scripts PROJECTS\\PEOPLES_AUDIT")
sys.path.append(str(project_root))

def test_constitution_extractor():
    """Test the constitution extractor module"""
    print("Testing Constitution Extractor...")
    print("=" * 60)
    
    try:
        from extractors.constitution_extractor import ConstitutionExtractor
        
        # Test with sample constitution path
        constitution_path = project_root / "input" / "constitution_of_kenya_2010.pdf"
        
        if constitution_path.exists():
            print(f"Found constitution at: {constitution_path}")
            
            # Create extractor
            extractor = ConstitutionExtractor()
            
            # Extract constitution
            print("Extracting constitution...")
            constitution_data = extractor.extract(str(constitution_path))
            
            # Print summary
            print(f"\nExtraction Summary:")
            print(f"  Total articles: {len(constitution_data['articles'])}")
            print(f"  Total pages: {constitution_data['metadata']['total_pages']}")
            
            # Show sample articles
            print(f"\nSample Articles:")
            for article in constitution_data['articles'][:5]:
                print(f"  Article {article['article_number']}: {article['title'][:50]}...")
            
            # Export to JSON
            output_dir = project_root / "test_output"
            output_dir.mkdir(exist_ok=True)
            
            extractor.export_to_json(constitution_data, str(output_dir / "constitution_test.json"))
            print(f"\nTest data exported to: {output_dir / 'constitution_test.json'}")
            
            return True
        else:
            print(f"Constitution file not found at: {constitution_path}")
            print("Please ensure the constitution PDF is in the input directory.")
            return False
            
    except Exception as e:
        print(f"Error testing constitution extractor: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chart_generator():
    """Test the chart generator module"""
    print("\n" + "=" * 60)
    print("Testing Chart Generator...")
    print("=" * 60)
    
    try:
        from visualizers.chart_generator import ChartGenerator, ChartConfig
        
        # Test data directory
        test_data_dir = project_root / "stage_4_visuals"
        test_data_dir.mkdir(exist_ok=True)
        
        # Create sample data files if they don't exist
        sample_data = {
            'sankey_data.json': {
                'nodes': [{'name': 'Source', 'category': 'source'}],
                'links': [{'source': 'Source', 'target': 'Target', 'value': 100}]
            },
            'charts_data.json': {
                'debt_timeline': {
                    'title': 'Test Debt Timeline',
                    'data': {
                        'years': ['2020', '2021', '2022'],
                        'debt_amounts': [100, 120, 150]
                    }
                }
            }
        }
        
        for filename, data in sample_data.items():
            filepath = test_data_dir / filename
            if not filepath.exists():
                import json
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Created sample file: {filename}")
        
        # Create chart generator
        config = ChartConfig(
            width=800,
            height=600,
            export_formats=['html', 'png']
        )
        
        generator = ChartGenerator(test_data_dir, project_root / "test_charts", config)
        
        # Test individual chart generation
        print("\nTesting individual charts...")
        
        # Test debt timeline
        debt_chart = generator.generate_debt_timeline()
        if debt_chart:
            print(f"  ✓ Debt timeline chart generated: {len(debt_chart)} formats")
        
        # Test corruption chart
        corruption_chart = generator.generate_corruption_by_sector()
        if corruption_chart:
            print(f"  ✓ Corruption chart generated: {len(corruption_chart)} formats")
        
        # Test generating all charts
        print("\nTesting generation of all charts...")
        all_charts = generator.generate_all_charts()
        
        print(f"\nChart Generation Summary:")
        print(f"  Total charts generated: {len(all_charts)}")
        
        for chart_name, chart_data in all_charts.items():
            print(f"  - {chart_name}: {len(chart_data)} file(s)")
        
        return True
        
    except Exception as e:
        print(f"Error testing chart generator: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_module_integration():
    """Test integration of both modules with main pipeline"""
    print("\n" + "=" * 60)
    print("Testing Module Integration with Main Pipeline...")
    print("=" * 60)
    
    try:
        # Import main pipeline components
        from main import PeopleAuditPipeline
        
        # Test pipeline initialization
        print("Testing pipeline initialization...")
        pipeline = PeopleAuditPipeline(str(project_root))
        
        print("  ✓ Pipeline initialized successfully")
        print(f"  Root directory: {pipeline.root}")
        print(f"  Config loaded: {len(pipeline.config)} settings")
        
        # Test that the modules can be imported from main
        print("\nTesting module imports from main...")
        
        try:
            from extractors.pdf_extractor import PDFExtractor
            print("  ✓ PDFExtractor import successful")
        except ImportError as e:
            print(f"  ✗ PDFExtractor import failed: {e}")
        
        try:
            from extractors.constitution_extractor import ConstitutionExtractor
            print("  ✓ ConstitutionExtractor import successful")
        except ImportError as e:
            print(f"  ✗ ConstitutionExtractor import failed: {e}")
        
        try:
            from visualizers.sankey_generator import SankeyGenerator
            print("  ✓ SankeyGenerator import successful")
        except ImportError as e:
            print(f"  ✗ SankeyGenerator import failed: {e}")
        
        try:
            from visualizers.chart_generator import ChartGenerator
            print("  ✓ ChartGenerator import successful")
        except ImportError as e:
            print(f"  ✗ ChartGenerator import failed: {e}")
        
        # Test directory structure
        print("\nTesting directory structure...")
        required_dirs = [
            'input',
            'reference_materials',
            'stage_1_extract',
            'stage_2_semantic',
            'stage_3_llm_text',
            'stage_4_visuals',
            'final_outputs',
            'logs'
        ]
        
        all_dirs_exist = True
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                print(f"  ✓ {dir_name}/ directory exists")
            else:
                print(f"  ✗ {dir_name}/ directory missing")
                all_dirs_exist = False
        
        return all_dirs_exist
        
    except Exception as e:
        print(f"Error testing integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data_structure():
    """Create sample data structure for testing"""
    print("\n" + "=" * 60)
    print("Creating Sample Data Structure...")
    print("=" * 60)
    
    # Create stage_4_visuals directory with sample data
    stage4_dir = project_root / "stage_4_visuals"
    stage4_dir.mkdir(exist_ok=True)
    
    # Sample sankey data
    sankey_data = {
        "nodes": [
            {"name": "Government Revenue", "category": "source"},
            {"name": "Debt", "category": "source"},
            {"name": "Corruption Losses", "category": "flow"},
            {"name": "Debt Service", "category": "flow"},
            {"name": "Health", "category": "destination"},
            {"name": "Education", "category": "destination"}
        ],
        "links": [
            {"source": "Government Revenue", "target": "Corruption Losses", "value": 800},
            {"source": "Government Revenue", "target": "Debt Service", "value": 750},
            {"source": "Government Revenue", "target": "Health", "value": 150},
            {"source": "Government Revenue", "target": "Education", "value": 120},
            {"source": "Debt", "target": "Debt Service", "value": 750}
        ]
    }
    
    # Sample charts data
    charts_data = {
        "debt_timeline": {
            "title": "Kenya Public Debt Growth (2014-2025)",
            "type": "line",
            "data": {
                "years": ["2014", "2015", "2016", "2017", "2018", "2019", 
                         "2020", "2021", "2022", "2023", "2024", "2025"],
                "debt_amounts": [2.4, 3.1, 3.7, 4.4, 5.2, 6.0, 7.0, 8.1, 9.3, 10.5, 11.6, 12.05]
            }
        },
        "corruption_by_sector": {
            "title": "Corruption Losses by Sector",
            "type": "bar",
            "data": {
                "sectors": ["Health", "Education", "Agriculture", "Infrastructure", "Counties"],
                "amounts": [780, 1660, 200, 3800, 12000]
            }
        }
    }
    
    # Sample statistics summary
    stats_summary = {
        "total_debt": "12.05 trillion",
        "debt_service_ratio": "56%",
        "corruption_loss_annual": "800 billion",
        "food_insecure": "15.5 million",
        "youth_unemployed": "1.7 million"
    }
    
    # Write sample data files
    import json
    
    with open(stage4_dir / "sankey_data.json", "w") as f:
        json.dump(sankey_data, f, indent=2)
    
    with open(stage4_dir / "charts_data.json", "w") as f:
        json.dump(charts_data, f, indent=2)
    
    with open(stage4_dir / "statistics_summary.json", "w") as f:
        json.dump(stats_summary, f, indent=2)
    
    print(f"Created sample data files in {stage4_dir}")
    print("  - sankey_data.json")
    print("  - charts_data.json")
    print("  - statistics_summary.json")
    
    return True

if __name__ == "__main__":
    print("PEOPLE'S AUDIT MODULE INTEGRATION TEST")
    print("=" * 60)
    
    # Create sample data first
    create_sample_data_structure()
    
    # Run tests
    test_results = []
    
    test_results.append(("Constitution Extractor", test_constitution_extractor()))
    test_results.append(("Chart Generator", test_chart_generator()))
    test_results.append(("Module Integration", test_module_integration()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED! Modules are ready for integration.")
    else:
        print("SOME TESTS FAILED. Please check the errors above.")
    
    print("\nNext steps:")
    print("1. Ensure constitution_of_kenya_2010.pdf is in input/ directory")
    print("2. Run main.py to execute the complete pipeline")
    print("3. Check final_outputs/ for generated documents and charts")