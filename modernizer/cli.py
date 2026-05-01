"""
CLI Module
Command-line interface for the Legacy Code Modernization Tool
"""

import argparse
import os
import sys
from modernizer.analyzer import LegacyCodeAnalyzer
from modernizer.refactorer import CodeRefactorer
from modernizer.test_generator import TestGenerator
from modernizer.doc_generator import DocumentationGenerator


class ModernizationCLI:
    """Command-line interface for code modernization"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description='Legacy Code Modernization Workflow Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  modernize ./legacy_code
  modernize ./legacy_code --output ./modernized
  modernize ./legacy_code --skip-tests
            """
        )
        
        parser.add_argument(
            'input_dir',
            help='Path to legacy code directory'
        )
        
        parser.add_argument(
            '--output',
            '-o',
            default='output',
            help='Output directory for modernized code (default: output)'
        )
        
        parser.add_argument(
            '--skip-tests',
            action='store_true',
            help='Skip test generation'
        )
        
        parser.add_argument(
            '--skip-docs',
            action='store_true',
            help='Skip documentation generation'
        )
        
        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='Verbose output'
        )
        
        return parser
    
    def run(self, args=None):
        """Run the CLI"""
        args = self.parser.parse_args(args)
        
        # Validate input directory
        if not os.path.exists(args.input_dir):
            print(f"❌ Error: Input directory '{args.input_dir}' does not exist")
            sys.exit(1)
        
        print("🚀 Legacy Code Modernization Tool")
        print("=" * 60)
        
        # Step 1: Analyze legacy code
        print("\n📊 Step 1: Analyzing legacy code...")
        analyzer = LegacyCodeAnalyzer()
        analysis_result = analyzer.analyze_directory(args.input_dir)
        
        if args.verbose:
            print(f"   Found {len(analysis_result.modules)} modules:")
            for module_name in analysis_result.modules.keys():
                print(f"   - {module_name}")
            print(f"   Global state variables: {len(analysis_result.global_state)}")
            print(f"   Issues found: {len(analysis_result.issues)}")
        
        print("   ✅ Analysis complete")
        
        # Step 2: Generate modernization roadmap
        print("\n🗺️  Step 2: Generating modernization roadmap...")
        roadmap = analyzer.generate_modernization_roadmap()
        print(f"   ✅ Roadmap created with {len(roadmap)} steps")
        
        # Step 3: Generate dependency map
        print("\n🔗 Step 3: Mapping dependencies...")
        dependencies = analyzer.identify_dependencies()
        print(f"   ✅ Mapped {len(dependencies)} service dependencies")
        
        # Step 4: Refactor code into microservices
        print("\n🔧 Step 4: Refactoring code into microservices...")
        refactorer = CodeRefactorer(analysis_result)
        refactorer.output_dir = args.output
        refactorer.generate_microservices()
        print("   ✅ Microservices generated:")
        for module_name in analysis_result.modules.keys():
            print(f"      - {module_name}")
        print("   ✅ API Gateway created")
        
        # Step 5: Generate tests
        if not args.skip_tests:
            print("\n🧪 Step 5: Generating unit tests...")
            test_generator = TestGenerator(args.output)
            test_generator.generate_all_tests()
            test_generator.generate_pytest_config()
            print("   ✅ Unit tests generated")
        else:
            print("\n⏭️  Step 5: Skipping test generation")
        
        # Step 6: Generate documentation
        if not args.skip_docs:
            print("\n📚 Step 6: Generating documentation...")
            doc_generator = DocumentationGenerator(analysis_result, args.output)
            doc_generator.generate_all_docs()
            print("   ✅ Documentation generated:")
            print("      - README.md")
            print("      - modernization_roadmap.md")
            print("      - dependency_map.md")
            print("      - architecture.md")
            print("      - api_documentation.md")
        else:
            print("\n⏭️  Step 6: Skipping documentation generation")
        
        # Summary
        print("\n" + "=" * 60)
        print("✨ Modernization Complete!")
        print("=" * 60)
        print(f"\n📁 Output directory: {args.output}/")
        print("\n📋 Next Steps:")
        print("   1. Review the generated code in the output directory")
        print("   2. Read the documentation in output/docs/")
        print("   3. Install dependencies for each service")
        print("   4. Run the services (see README.md)")
        print("\n💡 Quick Start:")
        print(f"   cd {args.output}")
        print("   cat README.md")
        print("\n🎉 Happy coding!")


def main():
    """Main entry point"""
    cli = ModernizationCLI()
    cli.run()


if __name__ == '__main__':
    main()

# Made with Bob
