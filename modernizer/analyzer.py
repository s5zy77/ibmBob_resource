"""
Code Analyzer Module
Analyzes legacy code to identify modules, dependencies, and structure
"""

import ast
import os
import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class CodeModule:
    """Represents a logical module identified in the code"""
    name: str
    responsibilities: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    global_vars: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis result of legacy codebase"""
    modules: Dict[str, CodeModule] = field(default_factory=dict)
    entry_points: List[str] = field(default_factory=list)
    global_state: List[str] = field(default_factory=list)
    database_operations: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


class LegacyCodeAnalyzer:
    """Analyzes legacy Python code to identify modernization opportunities"""
    
    def __init__(self):
        self.analysis_result = AnalysisResult()
    
    def analyze_directory(self, directory_path: str) -> AnalysisResult:
        """Analyze all Python files in a directory"""
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)
        
        return self.analysis_result
    
    def analyze_file(self, file_path: str) -> None:
        """Analyze a single Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            self._analyze_ast(tree, file_path)
        except SyntaxError as e:
            self.analysis_result.issues.append(f"Syntax error in {file_path}: {e}")
    
    def _analyze_ast(self, tree: ast.AST, file_path: str) -> None:
        """Analyze the AST of a Python file"""
        
        # Identify classes and their methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class(node)
            elif isinstance(node, ast.FunctionDef):
                self._analyze_function(node)
            elif isinstance(node, ast.Global):
                for name in node.names:
                    self.analysis_result.global_state.append(name)
            elif isinstance(node, ast.Assign):
                self._analyze_assignment(node)
    
    def _analyze_class(self, node: ast.ClassDef) -> None:
        """Analyze a class definition"""
        class_name = node.name
        
        # Categorize methods by responsibility
        user_methods = []
        product_methods = []
        order_methods = []
        payment_methods = []
        report_methods = []
        db_methods = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name
                
                # Categorize based on naming patterns
                if any(keyword in method_name.lower() for keyword in ['user', 'login', 'register', 'auth']):
                    user_methods.append(method_name)
                elif any(keyword in method_name.lower() for keyword in ['product', 'stock', 'inventory']):
                    product_methods.append(method_name)
                elif any(keyword in method_name.lower() for keyword in ['order', 'purchase']):
                    order_methods.append(method_name)
                elif any(keyword in method_name.lower() for keyword in ['payment', 'pay']):
                    payment_methods.append(method_name)
                elif any(keyword in method_name.lower() for keyword in ['report', 'analytics', 'sales']):
                    report_methods.append(method_name)
                elif any(keyword in method_name.lower() for keyword in ['database', 'db', 'setup']):
                    db_methods.append(method_name)
        
        # Create modules based on identified responsibilities
        if user_methods:
            self._add_or_update_module('UserService', user_methods, 'User management and authentication')
        
        if product_methods:
            self._add_or_update_module('ProductService', product_methods, 'Product catalog and inventory')
        
        if order_methods:
            self._add_or_update_module('OrderService', order_methods, 'Order processing and management')
        
        if payment_methods:
            self._add_or_update_module('PaymentService', payment_methods, 'Payment processing')
        
        if report_methods:
            self._add_or_update_module('ReportingService', report_methods, 'Analytics and reporting')
        
        if db_methods:
            self.analysis_result.database_operations.extend(db_methods)
    
    def _analyze_function(self, node: ast.FunctionDef) -> None:
        """Analyze a function definition"""
        # Check if it's a potential entry point
        if node.name == 'main' or any(dec.id == 'app.route' for dec in node.decorator_list if isinstance(dec, ast.Name)):
            self.analysis_result.entry_points.append(node.name)
    
    def _analyze_assignment(self, node: ast.Assign) -> None:
        """Analyze variable assignments for global state"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check if it's a global variable (module-level)
                if target.id.isupper() or target.id in ['db_connection', 'current_user']:
                    if target.id not in self.analysis_result.global_state:
                        self.analysis_result.global_state.append(target.id)
    
    def _add_or_update_module(self, module_name: str, functions: List[str], responsibility: str) -> None:
        """Add or update a module in the analysis result"""
        if module_name not in self.analysis_result.modules:
            self.analysis_result.modules[module_name] = CodeModule(
                name=module_name,
                responsibilities=[responsibility],
                functions=functions
            )
        else:
            module = self.analysis_result.modules[module_name]
            module.functions.extend(functions)
            if responsibility not in module.responsibilities:
                module.responsibilities.append(responsibility)
    
    def identify_dependencies(self) -> Dict[str, Set[str]]:
        """Identify dependencies between modules"""
        dependencies = {}
        
        # Order service depends on Product and User services
        if 'OrderService' in self.analysis_result.modules:
            dependencies['OrderService'] = {'ProductService', 'UserService'}
        
        # Payment service depends on Order service
        if 'PaymentService' in self.analysis_result.modules:
            dependencies['PaymentService'] = {'OrderService'}
        
        # Reporting service depends on all others
        if 'ReportingService' in self.analysis_result.modules:
            dependencies['ReportingService'] = set(self.analysis_result.modules.keys()) - {'ReportingService'}
        
        return dependencies
    
    def generate_modernization_roadmap(self) -> List[Dict[str, str]]:
        """Generate a step-by-step modernization roadmap"""
        roadmap = [
            {
                "step": "1",
                "title": "Database Layer Separation",
                "description": "Extract database operations into a separate data access layer",
                "priority": "High",
                "effort": "Medium"
            },
            {
                "step": "2",
                "title": "Remove Global State",
                "description": f"Eliminate global variables: {', '.join(self.analysis_result.global_state)}",
                "priority": "High",
                "effort": "Medium"
            },
            {
                "step": "3",
                "title": "Extract User Service",
                "description": "Create independent UserService microservice with authentication",
                "priority": "High",
                "effort": "High"
            },
            {
                "step": "4",
                "title": "Extract Product Service",
                "description": "Create ProductService microservice for catalog and inventory",
                "priority": "High",
                "effort": "Medium"
            },
            {
                "step": "5",
                "title": "Extract Order Service",
                "description": "Create OrderService microservice with proper dependencies",
                "priority": "Medium",
                "effort": "High"
            },
            {
                "step": "6",
                "title": "Extract Payment Service",
                "description": "Create PaymentService microservice for payment processing",
                "priority": "Medium",
                "effort": "Medium"
            },
            {
                "step": "7",
                "title": "Extract Reporting Service",
                "description": "Create ReportingService for analytics and reports",
                "priority": "Low",
                "effort": "Low"
            },
            {
                "step": "8",
                "title": "API Gateway Setup",
                "description": "Create API gateway to route requests to microservices",
                "priority": "High",
                "effort": "Medium"
            },
            {
                "step": "9",
                "title": "Add API Documentation",
                "description": "Generate OpenAPI/Swagger documentation for all services",
                "priority": "Medium",
                "effort": "Low"
            },
            {
                "step": "10",
                "title": "Testing & Validation",
                "description": "Create unit and integration tests for all services",
                "priority": "High",
                "effort": "High"
            }
        ]
        
        return roadmap

# Made with Bob
