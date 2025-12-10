# ============================================================================
# PHASE 5: OPTIMIZATION
# ============================================================================
# This module optimizes Three-Address Code

from typing import List, Dict, Set
from ir_generator import TACInstruction
import copy


class Optimizer:
    """Optimizes Three-Address Code"""
    
    def __init__(self):
        self.optimizations_applied = []
    
    def optimize(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Apply all optimization passes"""
        optimized = copy.deepcopy(instructions)
        
        # Multiple passes for better optimization
        for pass_num in range(3):
            old_count = len(optimized)
            
            optimized = self.constant_folding(optimized)
            optimized = self.constant_propagation(optimized)
            optimized = self.algebraic_simplification(optimized)
            optimized = self.dead_code_elimination(optimized)
            
            # Stop if no changes
            if len(optimized) == old_count:
                break
        
        return optimized
    
    def constant_folding(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Evaluate constant expressions at compile time"""
        optimized = []
        
        for instr in instructions:
            # Check if both operands are constants
            if instr.op in ('+', '-', '*', '/', '%', '^', '>', '<', '>=', '<=', '==', '!='):
                if self.is_constant(instr.arg1) and self.is_constant(instr.arg2):
                    try:
                        val1 = self.get_constant_value(instr.arg1)
                        val2 = self.get_constant_value(instr.arg2)
                        
                        # Compute result
                        if instr.op == '+':
                            result_val = val1 + val2
                        elif instr.op == '-':
                            result_val = val1 - val2
                        elif instr.op == '*':
                            result_val = val1 * val2
                        elif instr.op == '/':
                            result_val = val1 / val2
                        elif instr.op == '%':
                            result_val = val1 % val2
                        elif instr.op == '^':
                            result_val = val1 ** val2
                        elif instr.op == '>':
                            result_val = val1 > val2
                        elif instr.op == '<':
                            result_val = val1 < val2
                        elif instr.op == '>=':
                            result_val = val1 >= val2
                        elif instr.op == '<=':
                            result_val = val1 <= val2
                        elif instr.op == '==':
                            result_val = val1 == val2
                        elif instr.op == '!=':
                            result_val = val1 != val2
                        
                        # Create assignment with constant result
                        new_instr = TACInstruction('assign', str(result_val), None, instr.result)
                        optimized.append(new_instr)
                        self.optimizations_applied.append(f"Constant folding: {instr} -> {new_instr}")
                        continue
                    except:
                        pass
            
            optimized.append(instr)
        
        return optimized
    
    def constant_propagation(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Replace variables with their constant values"""
        constants: Dict[str, str] = {}
        optimized = []
        
        for instr in instructions:
            # Track constant assignments to temporaries only (not user variables)
            if instr.op == 'assign' and self.is_constant(instr.arg1) and instr.result.startswith('t'):
                constants[instr.result] = instr.arg1
                optimized.append(instr)
                continue
            
            # Replace variables with constants
            new_instr = copy.copy(instr)
            
            if instr.arg1 and instr.arg1 in constants:
                new_instr.arg1 = constants[instr.arg1]
                self.optimizations_applied.append(f"Constant propagation: {instr.arg1} -> {constants[instr.arg1]}")
            
            if instr.arg2 and instr.arg2 in constants:
                new_instr.arg2 = constants[instr.arg2]
                self.optimizations_applied.append(f"Constant propagation: {instr.arg2} -> {constants[instr.arg2]}")
            
            # If variable is reassigned, remove from constants
            if instr.result and instr.result in constants:
                del constants[instr.result]
            
            # Clear constants after labels (new basic block)
            if instr.op == 'label':
                constants.clear()
            
            optimized.append(new_instr)
        
        return optimized
    
    def algebraic_simplification(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Apply algebraic identities"""
        optimized = []
        
        for instr in instructions:
            simplified = False
            
            # x + 0 = x or 0 + x = x
            if instr.op == '+':
                if instr.arg1 == '0':
                    new_instr = TACInstruction('assign', instr.arg2, None, instr.result)
                    optimized.append(new_instr)
                    self.optimizations_applied.append(f"Algebraic: 0 + x = x")
                    simplified = True
                elif instr.arg2 == '0':
                    new_instr = TACInstruction('assign', instr.arg1, None, instr.result)
                    optimized.append(new_instr)
                    self.optimizations_applied.append(f"Algebraic: x + 0 = x")
                    simplified = True
            
            # x - 0 = x
            elif instr.op == '-' and instr.arg2 == '0':
                new_instr = TACInstruction('assign', instr.arg1, None, instr.result)
                optimized.append(new_instr)
                self.optimizations_applied.append(f"Algebraic: x - 0 = x")
                simplified = True
            
            # x * 0 = 0 or 0 * x = 0
            elif instr.op == '*':
                if instr.arg1 == '0' or instr.arg2 == '0':
                    new_instr = TACInstruction('assign', '0', None, instr.result)
                    optimized.append(new_instr)
                    self.optimizations_applied.append(f"Algebraic: x * 0 = 0")
                    simplified = True
                # x * 1 = x or 1 * x = x
                elif instr.arg1 == '1':
                    new_instr = TACInstruction('assign', instr.arg2, None, instr.result)
                    optimized.append(new_instr)
                    self.optimizations_applied.append(f"Algebraic: 1 * x = x")
                    simplified = True
                elif instr.arg2 == '1':
                    new_instr = TACInstruction('assign', instr.arg1, None, instr.result)
                    optimized.append(new_instr)
                    self.optimizations_applied.append(f"Algebraic: x * 1 = x")
                    simplified = True
            
            # x / 1 = x
            elif instr.op == '/' and instr.arg2 == '1':
                new_instr = TACInstruction('assign', instr.arg1, None, instr.result)
                optimized.append(new_instr)
                self.optimizations_applied.append(f"Algebraic: x / 1 = x")
                simplified = True
            
            if not simplified:
                optimized.append(instr)
        
        return optimized
    
    def dead_code_elimination(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Remove unreachable code and unused assignments"""
        # Find used variables
        used_vars: Set[str] = set()
        
        for instr in instructions:
            # Variables used in operations
            if instr.arg1 and not self.is_constant(instr.arg1):
                used_vars.add(instr.arg1)
            if instr.arg2 and not self.is_constant(instr.arg2):
                used_vars.add(instr.arg2)
            
            # Variables used in control flow
            if instr.op in ('if_false', 'if_true', 'return', 'print', 'param'):
                if instr.arg1 and not self.is_constant(instr.arg1):
                    used_vars.add(instr.arg1)
        
        # Remove unused assignments to temporaries
        optimized = []
        for instr in instructions:
            # Keep non-assignment instructions
            if instr.op != 'assign':
                optimized.append(instr)
                continue
            
            # Keep assignments to non-temporary variables
            if not instr.result.startswith('t'):
                optimized.append(instr)
                continue
            
            # Keep assignments to used temporaries
            if instr.result in used_vars:
                optimized.append(instr)
                continue
            
            # Remove unused assignment
            self.optimizations_applied.append(f"Dead code: removed {instr}")
        
        # Remove unreachable code after unconditional jumps
        final_optimized = []
        skip_until_label = False
        
        for instr in optimized:
            if skip_until_label:
                if instr.op == 'label':
                    skip_until_label = False
                    final_optimized.append(instr)
                else:
                    self.optimizations_applied.append(f"Unreachable code: removed {instr}")
                continue
            
            final_optimized.append(instr)
            
            if instr.op in ('goto', 'return'):
                skip_until_label = True
        
        return final_optimized
    
    def is_constant(self, value: str) -> bool:
        """Check if a value is a constant"""
        if not value:
            return False
        
        # Check for boolean constants
        if value in ('true', 'false'):
            return True
        
        # Check for string constants
        if value.startswith('"') and value.endswith('"'):
            return True
        
        # Check for numeric constants
        try:
            float(value)
            return True
        except:
            return False
    
    def get_constant_value(self, value: str):
        """Get the actual value of a constant"""
        if value == 'true':
            return True
        elif value == 'false':
            return False
        elif value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        else:
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except:
                return value
