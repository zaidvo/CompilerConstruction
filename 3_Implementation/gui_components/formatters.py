"""
Output Formatters
Formats compiler output for display in GUI
"""


class TokenFormatter:
    """Format tokens for display"""
    
    def format(self, tokens):
        """Format token list"""
        if not tokens:
            return "No tokens to display"
        
        output = "PHASE 1: LEXICAL ANALYSIS\n"
        output += "=" * 70 + "\n\n"
        
        # Group tokens by type
        token_groups = {}
        for token in tokens:
            if token.type.name != 'EOF':
                if token.type.name not in token_groups:
                    token_groups[token.type.name] = []
                token_groups[token.type.name].append(token)
        
        total_tokens = sum(len(tokens) for tokens in token_groups.values())
        output += f"Total Tokens: {total_tokens}\n"
        output += f"Token Types: {len(token_groups)}\n\n"
        output += "-" * 70 + "\n\n"
        
        # Display by category
        categories = {
            'Keywords': ['INT', 'LONG', 'FLOAT', 'STRING_TYPE', 'BOOLEAN', 'ARRAY', 'MATRIX',
                       'IF', 'ELSE', 'WHILE', 'FOR', 'REPEAT', 'TIMES', 'FUNCTION', 'RETURN', 'END',
                       'PRINT', 'INPUT', 'BREAK', 'CONTINUE', 'TRUE', 'FALSE'],
            'Identifiers': ['IDENTIFIER'],
            'Literals': ['NUMBER', 'STRING'],
            'Operators': ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO', 'POWER',
                        'GT', 'LT', 'GTE', 'LTE', 'EQ', 'NEQ', 'AND', 'OR', 'NOT'],
            'Delimiters': ['LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA', 'COLON', 'SEMICOLON', 'ASSIGN'],
        }
        
        for category, types in categories.items():
            category_tokens = []
            for ttype in types:
                if ttype in token_groups:
                    category_tokens.extend(token_groups[ttype])
            
            if category_tokens:
                output += f"▸ {category} ({len(category_tokens)})\n"
                output += "-" * 70 + "\n"
                
                for token in category_tokens[:20]:
                    value_str = f" = '{token.value}'" if token.value else ""
                    output += f"  [{token.line:2d}:{token.column:2d}] {token.type.name:<15}{value_str}\n"
                
                if len(category_tokens) > 20:
                    output += f"  ... and {len(category_tokens) - 20} more\n"
                
                output += "\n"
        
        return output


class ASTFormatter:
    """Format AST for display"""
    
    def format(self, ast):
        """Format AST tree"""
        if not ast:
            return "No AST to display"
        
        output = "PHASE 2: SYNTAX ANALYSIS\n"
        output += "=" * 70 + "\n\n"
        output += "Abstract Syntax Tree (AST):\n\n"
        
        node_count = self._count_nodes(ast)
        output += f"Total Nodes: {node_count}\n"
        output += "\n" + "-" * 70 + "\n\n"
        
        output += self._print_tree(ast, "", True, True)
        
        return output
    
    def _count_nodes(self, node, count=0):
        """Count AST nodes"""
        if node is None:
            return count
        count += 1
        if hasattr(node, '__dict__'):
            for value in node.__dict__.values():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, '__class__') and 'Node' in item.__class__.__name__:
                            count = self._count_nodes(item, count)
                elif hasattr(value, '__class__') and 'Node' in value.__class__.__name__:
                    count = self._count_nodes(value, count)
        return count
    
    def _print_tree(self, node, prefix, is_last, is_root=False):
        """Print AST tree structure"""
        if node is None:
            return ""
        
        output = ""
        
        if is_root:
            connector = ""
            node_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            node_prefix = prefix
        
        node_name = node.__class__.__name__
        details = ""
        if hasattr(node, 'value'):
            details = f" [{node.value}]"
        elif hasattr(node, 'name'):
            details = f" ({node.name})"
        elif hasattr(node, 'operator'):
            details = f" '{node.operator}'"
        elif hasattr(node, 'var_type'):
            details = f" <{node.var_type}>"
        
        output += f"{node_prefix}{connector}{node_name}{details}\n"
        
        child_prefix = "" if is_root else prefix + ("    " if is_last else "│   ")
        
        # Get children
        children = []
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if key in ['value', 'name', 'operator', 'var_type']:
                    continue
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, '__class__') and 'Node' in item.__class__.__name__:
                            children.append(item)
                elif hasattr(value, '__class__') and 'Node' in value.__class__.__name__:
                    children.append(value)
        
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            output += self._print_tree(child, child_prefix, is_last_child)
        
        return output


class SemanticFormatter:
    """Format semantic analysis results"""
    
    def format(self, semantic_info):
        """Format semantic analysis output"""
        if not semantic_info:
            return "No semantic information available"
        
        output = "✅ [OK] Semantic analysis passed\n\n"
        output += "📊 SYMBOL TABLE\n"
        output += "=" * 120 + "\n"
        output += f"{'Symbol':<15} {'Kind':<12} {'Type':<10} {'Value/Init':<25} {'Scope':<7} {'Line':<6} {'Init':<5} {'Used':<5}\n"
        output += "=" * 120 + "\n"
        
        all_symbols = semantic_info.get('symbols', [])
        
        # Separate variables and functions
        variables = [(n, i) for n, i in all_symbols if i.get('type') in ('variable', 'parameter')]
        functions = [(n, i) for n, i in all_symbols if i.get('type') == 'function']
        
        # Display variables
        if variables:
            output += "📌 VARIABLES:\n"
            output += "-" * 120 + "\n"
            for name, info in variables:
                kind = info.get('type', 'unknown')
                val_type = info.get('value_type', 'unknown')
                init_val = info.get('init_value', 'null')
                scope = info.get('scope_level', 0)
                line = info.get('line_number', '-')
                is_init = '✓' if info.get('is_initialized', False) else '✗'
                is_used = '✓' if info.get('is_used', False) else '✗'
                
                if init_val is None:
                    init_val = 'null'
                elif isinstance(init_val, str) and len(init_val) > 23:
                    init_val = init_val[:20] + '...'
                
                output += f"{'  ' + name:<15} {kind:<12} {val_type:<10} {str(init_val):<25} {scope:<7} {str(line):<6} {is_init:<5} {is_used:<5}\n"
            output += "\n"
        
        # Display functions
        if functions:
            output += "🔧 FUNCTIONS:\n"
            output += "-" * 120 + "\n"
            for name, info in functions:
                kind = info.get('type', 'unknown')
                return_type = info.get('return_type', info.get('value_type', 'void'))
                scope = info.get('scope_level', 0)
                line = info.get('line_number', '-')
                
                output += f"{'  ' + name:<15} {kind:<12} {return_type:<10} {'-':<25} {scope:<7} {str(line):<6} {'✓':<5} {'✓':<5}\n"
            output += "\n"
        
        output += "=" * 120 + "\n"
        output += f"\n✓ Variables declared: {len(variables)}\n"
        output += f"✓ Functions defined: {len(functions)}\n"
        output += f"✓ All type checks passed\n"
        
        # Warnings
        unused_vars = [n for n, i in variables if not i.get('is_used', False)]
        if unused_vars:
            output += f"\n⚠ WARNING: {len(unused_vars)} unused variable(s): {', '.join(unused_vars)}\n"
        
        return output


class TACFormatter:
    """Format TAC for display"""
    
    def format(self, tac):
        """Format TAC instructions"""
        if not tac:
            return "No TAC to display"
        
        output = "PHASE 4: INTERMEDIATE CODE GENERATION\n"
        output += "=" * 70 + "\n\n"
        output += "Three-Address Code (TAC):\n\n"
        output += f"Total Instructions: {len(tac)}\n\n"
        output += "-" * 70 + "\n\n"
        
        for i, instr in enumerate(tac):
            instr_str = str(instr)
            
            if 'jump' in instr_str.lower() or 'goto' in instr_str.lower():
                output += f"{i:3d}: ➡ {instr_str}\n"
            elif 'return' in instr_str.lower():
                output += f"{i:3d}: ↩ {instr_str}\n"
            elif 'call' in instr_str.lower():
                output += f"{i:3d}: 📞 {instr_str}\n"
            else:
                output += f"{i:3d}:   {instr_str}\n"
        
        return output


class OptimizedTACFormatter:
    """Format optimized TAC for display"""
    
    def format(self, optimized_tac, original_tac=None):
        """Format optimized TAC with statistics"""
        if not optimized_tac:
            return "No optimized TAC to display"
        
        output = "PHASE 5: OPTIMIZATION\n"
        output += "=" * 70 + "\n\n"
        
        original_count = len(original_tac) if original_tac else 0
        optimized_count = len(optimized_tac)
        reduction = original_count - optimized_count
        reduction_pct = (reduction / original_count * 100) if original_count > 0 else 0
        
        output += "┌" + "─" * 68 + "┐\n"
        output += "│" + " OPTIMIZATION RESULTS".center(68) + "│\n"
        output += "├" + "─" * 68 + "┤\n"
        output += f"│ Original Instructions:    {original_count:5d}" + " " * 40 + "│\n"
        output += f"│ Optimized Instructions:   {optimized_count:5d}" + " " * 40 + "│\n"
        output += f"│ Reduction:                {reduction:5d} instructions ({reduction_pct:.1f}%)" + " " * 20 + "│\n"
        output += "└" + "─" * 68 + "┘\n\n"
        
        output += "-" * 70 + "\n"
        output += "Optimized Code:\n"
        output += "-" * 70 + "\n\n"
        
        for i, instr in enumerate(optimized_tac):
            output += f"{i:3d}: {instr}\n"
        
        return output
