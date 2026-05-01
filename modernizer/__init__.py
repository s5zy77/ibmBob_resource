"""
Legacy Code Modernization Workflow Tool
Automates the process of converting legacy monolithic code into modern microservices
"""

__version__ = "1.0.0"
__author__ = "Legacy Code Modernization Team"

from modernizer.analyzer import LegacyCodeAnalyzer, AnalysisResult, CodeModule
from modernizer.refactorer import CodeRefactorer
from modernizer.test_generator import TestGenerator
from modernizer.doc_generator import DocumentationGenerator
from modernizer.cli import ModernizationCLI

__all__ = [
    'LegacyCodeAnalyzer',
    'AnalysisResult',
    'CodeModule',
    'CodeRefactorer',
    'TestGenerator',
    'DocumentationGenerator',
    'ModernizationCLI'
]

# Made with Bob
