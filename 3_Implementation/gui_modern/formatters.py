"""
Output Formatters for Each Compiler Phase
Formats phase results for display in the GUI
"""


class TokensFormatter:
    """Format tokens for display"""
    
    @staticmethod
    def format(tokens):
        """Format token list as a table"""
        if not tokens:
            return "No tokens generated."
        
        # Filter out EOF
        tokens = [t for t in tokens if t.type.name != 'EOF']
        
        output = f"Total Tokens: {len(tokens)}\n"
        output += "=" * 80 + "\n\n"
        output += f"{'Index':<8} {'Type':<20} {'Value':<25} {'Line':<6} {'Column':<6}\n"
        output += "-" * 80 + "\n"
        
        for i, token in enumerate(tokens):
            value = str(token.value) if token.value is not None else ""
            if len(value) > 22:
                value = value[:19] + "..."
            output += f"{i:<8} {token.type.name:<20} {value:<25} {token.line:<6} {token.column:<6}\n"
        
        return output


class ASTFormatter:
    """Format AST for tree view"""
    
    @staticmethod
    def format(ast):
        """Format AST as tree structure"""
        if not ast:
            return "No AST generated."
        
        output = "Abstract Syntax Tree\n"
        output += "=" * 80 + "\n\n"
        output += ASTFormatter._print_tree(ast, "", True)
        return output
    
    @staticmethod
    def _print_tree(node, prefix="", is_last=True, is_root=False):
        """Recursively print AST tree"""
        if node is None:
            return ""
        
        output = ""
        
        # Node connector
        if not is_root:
            connector = "└── " if is_last else "├── "
            output += prefix + connector
        
        # Node type
        node_type = type(node).__name__
        output += node_type
        
        # Node details
        if hasattr(node, 'value'):
            output += f" [{node.value}]"
        elif hasattr(node, 'name'):
            output += f" [{node.name}]"
        elif hasattr(node, 'op'):
            output += f" [{node.op}]"
        
        output += "\n"
        
        # Get children
        children = []
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if key.startswith('_'):
                    continue
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, '__class__') and 'Node' in item.__class__.__name__:
                            children.append(item)
                elif hasattr(value, '__class__') and 'Node' in value.__class__.__name__:
                    children.append(value)
        
        # Print children
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            extension = "    " if is_last else "│   "
            child_prefix = prefix + extension if not is_root else ""
            output += ASTFormatter._print_tree(child, child_prefix, is_last_child)
        
        return output


class SemanticFormatter:
    """Format semantic analysis results"""
    
    @staticmethod
    def format(semantic_info):
        """Format semantic analysis information"""
        if not semantic_info:
            return "No semantic analysis performed."
        
        output = "Semantic Analysis Results\n"
        output += "=" * 80 + "\n\n"
        
        # Symbol table
        symbols = semantic_info.get('symbols', [])
        output += f"Symbol Table ({len(symbols)} symbols):\n"
        output += "-" * 80 + "\n"
        
        if symbols:
            output += f"{'Name':<20} {'Type':<15} {'Scope':<15} {'Initialized':<12}\n"
            output += "-" * 80 + "\n"
            for symbol in symbols:
                if isinstance(symbol, dict):
                    name = symbol.get('name', '?')
                    sym_type = symbol.get('type', '?')
                    scope = symbol.get('scope', '?')
                    init = symbol.get('initialized', '?')
                    output += f"{name:<20} {sym_type:<15} {scope:<15} {str(init):<12}\n"
                else:
                    output += f"{str(symbol)}\n"
        else:
            output += "No symbols found.\n"
        
        # Errors
        errors = semantic_info.get('errors', [])
        if errors:
            output += "\n\nSemantic Errors:\n"
            output += "-" * 80 + "\n"
            for error in errors:
                output += f"• {error}\n"
        
        return output


class IRFormatter:
    """Format intermediate representation (TAC)"""
    
    @staticmethod
    def format(tac):
        """Format TAC instructions"""
        if not tac:
            return "No IR code generated."
        
        output = "Three-Address Code (TAC)\n"
        output += "=" * 80 + "\n\n"
        output += f"Total Instructions: {len(tac)}\n\n"
        output += f"{'#':<6} {'Instruction':<70}\n"
        output += "-" * 80 + "\n"
        
        for i, instruction in enumerate(tac):
            inst_str = str(instruction)
            if len(inst_str) > 67:
                inst_str = inst_str[:64] + "..."
            output += f"{i:<6} {inst_str:<70}\n"
        
        return output


class OptimizerFormatter:
    """Format optimizer results"""
    
    @staticmethod
    def format(optimized_tac, original_tac):
        """Format optimization log"""
        if not optimized_tac:
            return "No optimization performed."
        
        original_count = len(original_tac) if original_tac else 0
        optimized_count = len(optimized_tac) if optimized_tac else 0
        saved = original_count - optimized_count
        
        output = "Optimization Results\n"
        output += "=" * 80 + "\n\n"
        output += f"Original Instructions:  {original_count}\n"
        output += f"Optimized Instructions: {optimized_count}\n"
        output += f"Instructions Saved:     {saved} ({(saved/original_count*100) if original_count > 0 else 0:.1f}%)\n\n"
        
        output += "Optimizations Applied:\n"
        output += "-" * 80 + "\n"
        output += "• Constant folding\n"
        output += "• Dead code elimination\n"
        output += "• Copy propagation\n"
        output += "• Algebraic simplification\n"
        
        return output


class BytecodeFormatter:
    """Format bytecode/optimized TAC"""
    
    @staticmethod
    def format(bytecode):
        """Format bytecode instructions"""
        if not bytecode:
            return "No bytecode generated."
        
        output = "Bytecode (Optimized TAC)\n"
        output += "=" * 80 + "\n\n"
        output += f"Total Instructions: {len(bytecode)}\n\n"
        output += f"{'#':<6} {'Label':<15} {'Instruction':<55}\n"
        output += "-" * 80 + "\n"
        
        for i, instruction in enumerate(bytecode):
            inst_str = str(instruction)
            
            # Extract label if present
            label = ""
            if ':' in inst_str and not any(op in inst_str for op in ['<', '>', '=']):
                parts = inst_str.split(':', 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    inst_str = parts[1].strip()
            
            if len(inst_str) > 52:
                inst_str = inst_str[:49] + "..."
            
            output += f"{i:<6} {label:<15} {inst_str:<55}\n"
        
        return output


class ErrorsFormatter:
    """Format compilation errors"""
    
    @staticmethod
    def format(errors):
        """Format error list with full details"""
        if not errors:
            return "No errors detected. ✓"
        
        output = "Compilation Errors\n"
        output += "=" * 100 + "\n\n"
        output += f"Total Errors: {len(errors)}\n\n"
        
        for i, error in enumerate(errors, 1):
            if isinstance(error, dict):
                phase = error.get('phase', '?')
                err_type = error.get('type', '?')
                message = error.get('message', '?')
                line = error.get('line', 0)
                column = error.get('column', 0)
                
                output += f"Error #{i}:\n"
                output += "-" * 100 + "\n"
                output += f"  Phase:    {phase}\n"
                output += f"  Type:     {err_type}\n"
                output += f"  Location: "
                if line > 0:
                    output += f"Line {line}"
                    if column > 0:
                        output += f", Column {column}"
                else:
                    output += "Unknown"
                output += "\n"
                output += f"  Message:  {message}\n"
                
                # Add suggestion if present in message
                if "Suggestion:" in message or "Did you mean" in message:
                    output += f"  💡 {message.split('(')[-1].strip(')')}\n"
                
                output += "\n"
            else:
                output += f"Error #{i}:\n"
                output += "-" * 100 + "\n"
                output += f"  {str(error)}\n\n"
        
        return output
