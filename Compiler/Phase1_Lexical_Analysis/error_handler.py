"""
Enhanced Error Handler with Multiple Error Collection and Smart Suggestions
"""
from typing import List, Tuple, Optional
from difflib import get_close_matches


class CompilerError:
    """Base class for all compiler errors"""
    
    def __init__(self, message: str, line: int, column: int, 
                 source_line: str = "", phase: str = "Unknown"):
        self.message = message
        self.line = line
        self.column = column
        self.source_line = source_line
        self.phase = phase
        self.suggestions = []
    
    def add_suggestion(self, suggestion: str):
        """Add a 'Did you mean...?' suggestion"""
        self.suggestions.append(suggestion)
    
    def __str__(self):
        error_str = f"\n{'='*70}\n"
        error_str += f"[{self.phase} ERROR] Line {self.line}, Column {self.column}\n"
        error_str += f"{'='*70}\n"
        error_str += f"{self.message}\n\n"
        
        # Show source code context
        if self.source_line:
            error_str += "Context:\n"
            error_str += f"  {self.line:4d} | {self.source_line}\n"
            error_str += f"       | {' ' * (self.column - 1)}^\n"
        
        # Show suggestions
        if self.suggestions:
            error_str += f"\n💡 Did you mean?\n"
            for sug in self.suggestions:
                error_str += f"   • {sug}\n"
        
        return error_str


class ErrorHandler:
    """Collects and manages multiple compilation errors"""
    
    def __init__(self, source_code: str = ""):
        self.errors: List[CompilerError] = []
        self.warnings: List[str] = []
        self.source_lines = source_code.split('\n') if source_code else []
        self.known_identifiers = set()
        self.known_keywords = {
            'int', 'long', 'float', 'string', 'boolean', 'array', 'matrix',
            'if', 'else', 'while', 'for', 'repeat', 'times', 'function',
            'return', 'end', 'print', 'input', 'break', 'continue',
            'true', 'false', 'and', 'or', 'not'
        }
    
    def add_identifier(self, name: str):
        """Register a known identifier for suggestion matching"""
        self.known_identifiers.add(name)
    
    def get_source_line(self, line: int) -> str:
        """Get source line at given line number (1-indexed)"""
        if 0 < line <= len(self.source_lines):
            return self.source_lines[line - 1]
        return ""
    
    def find_suggestions(self, wrong_name: str, search_in: set = None) -> List[str]:
        """Find similar identifiers using fuzzy matching"""
        if search_in is None:
            search_in = self.known_identifiers | self.known_keywords
        
        matches = get_close_matches(wrong_name, search_in, n=3, cutoff=0.6)
        return matches
    
    def add_error(self, message: str, line: int, column: int = 1, 
                  phase: str = "Compilation", wrong_name: str = None):
        """Add a new error with optional suggestions"""
        source_line = self.get_source_line(line)
        error = CompilerError(message, line, column, source_line, phase)
        
        # Add suggestions if we have a wrong identifier
        if wrong_name:
            suggestions = self.find_suggestions(wrong_name)
            for sug in suggestions:
                error.add_suggestion(sug)
        
        self.errors.append(error)
    
    def add_warning(self, message: str, line: int = 0):
        """Add a warning message"""
        if line > 0:
            self.warnings.append(f"Line {line}: {message}")
        else:
            self.warnings.append(message)
    
    def has_errors(self) -> bool:
        """Check if any errors were collected"""
        return len(self.errors) > 0
    
    def get_error_summary(self) -> str:
        """Generate a comprehensive error report"""
        if not self.errors and not self.warnings:
            return "✅ No errors or warnings\n"
        
        report = "\n"
        
        if self.errors:
            report += f"{'='*70}\n"
            report += f"  ❌ COMPILATION FAILED - {len(self.errors)} ERROR(S) FOUND\n"
            report += f"{'='*70}\n"
            
            for i, error in enumerate(self.errors, 1):
                report += f"\n[Error {i}/{len(self.errors)}]\n"
                report += str(error)
        
        if self.warnings:
            report += f"\n{'='*70}\n"
            report += f"  ⚠️  WARNINGS ({len(self.warnings)})\n"
            report += f"{'='*70}\n"
            for warning in self.warnings:
                report += f"  • {warning}\n"
        
        return report
    
    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()


# Global error handler instance
_global_error_handler = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_error_handler(handler: ErrorHandler):
    """Set a new global error handler"""
    global _global_error_handler
    _global_error_handler = handler


def reset_error_handler(source_code: str = ""):
    """Reset the global error handler with new source code"""
    global _global_error_handler
    _global_error_handler = ErrorHandler(source_code)
    return _global_error_handler
