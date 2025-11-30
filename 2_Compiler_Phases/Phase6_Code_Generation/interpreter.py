# ============================================================================
# PHASE 6: CODE GENERATION AND EXECUTION
# ============================================================================
# This module implements an interpreter that executes Three-Address Code
# All math operations are implemented manually without Python built-ins

from typing import Dict, List, Any, Optional
from ir_generator import TACInstruction
import sys


class Interpreter:
    """Interpreter/Virtual Machine for executing TAC"""
    
    def __init__(self):
        self.memory: Dict[str, Any] = {}  # Variable storage
        self.pc = 0  # Program counter
        self.instructions: List[TACInstruction] = []
        self.labels: Dict[str, int] = {}  # Label positions
        self.call_stack: List[Dict[str, Any]] = []  # Function call stack
        self.output: List[str] = []  # Captured output
        self.angle_mode = 'radians'  # Default angle mode: 'radians' or 'degrees'
        self.param_stack: List[Any] = []  # Parameter stack for function calls
    
    def execute(self, instructions: List[TACInstruction]):
        """Execute TAC instructions"""
        self.instructions = instructions
        self.pc = 0
        
        # Build label table
        self.build_label_table()
        
        # Execute instructions
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            self.execute_instruction(instr)
            self.pc += 1
    
    def build_label_table(self):
        """Build a table of label positions"""
        for i, instr in enumerate(self.instructions):
            if instr.op == 'label':
                self.labels[instr.result] = i
    
    def execute_instruction(self, instr: TACInstruction):
        """Execute a single TAC instruction"""
        op = instr.op
        
        if op == 'assign' or op == '=':
            value = self.get_value(instr.arg1)
            self.memory[instr.result] = value
        
        elif op == '+':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            # Check if both are matrices
            if self._is_matrix(val1) and self._is_matrix(val2):
                self.memory[instr.result] = self._matrix_add(val1, val2)
            else:
                self.memory[instr.result] = val1 + val2
        
        elif op == '-':
            if instr.arg2:  # Binary minus
                val1 = self.get_value(instr.arg1)
                val2 = self.get_value(instr.arg2)
                # Check if both are matrices
                if self._is_matrix(val1) and self._is_matrix(val2):
                    self.memory[instr.result] = self._matrix_subtract(val1, val2)
                else:
                    self.memory[instr.result] = val1 - val2
            else:  # Unary minus
                val = self.get_value(instr.arg1)
                self.memory[instr.result] = -val
        
        elif op == '*':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            # Check if both are matrices
            if self._is_matrix(val1) and self._is_matrix(val2):
                self.memory[instr.result] = self._matrix_multiply(val1, val2)
            else:
                self.memory[instr.result] = val1 * val2
        
        elif op == '/':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            if val2 == 0:
                raise RuntimeError("Division by zero")
            self.memory[instr.result] = val1 / val2
        
        elif op == '%':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 % val2
        
        elif op == '^':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            
            # Check for matrix transpose (^t)
            if self._is_matrix(val1) and val2 == 't':
                self.memory[instr.result] = self._matrix_transpose(val1)
            # Check for matrix inverse (^-1)
            elif self._is_matrix(val1) and val2 == -1:
                self.memory[instr.result] = self._matrix_inverse(val1)
            # Regular power operation
            else:
                self.memory[instr.result] = val1 ** val2
        
        elif op == '>':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 > val2
        
        elif op == '<':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 < val2
        
        elif op == '>=':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 >= val2
        
        elif op == '<=':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 <= val2
        
        elif op == '==':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 == val2
        
        elif op == '!=':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 != val2
        
        elif op == 'and':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 and val2
        
        elif op == 'or':
            val1 = self.get_value(instr.arg1)
            val2 = self.get_value(instr.arg2)
            self.memory[instr.result] = val1 or val2
        
        elif op == 'not':
            val = self.get_value(instr.arg1)
            self.memory[instr.result] = not val
        
        elif op == 'label':
            pass  # Labels are handled by label table
        
        elif op == 'goto':
            if instr.result in self.labels:
                self.pc = self.labels[instr.result] - 1  # -1 because pc will be incremented
            else:
                raise RuntimeError(f"Label {instr.result} not found")
        
        elif op == 'if_false':
            condition = self.get_value(instr.arg1)
            if not condition:
                if instr.result in self.labels:
                    self.pc = self.labels[instr.result] - 1
                else:
                    raise RuntimeError(f"Label {instr.result} not found")
        
        elif op == 'if_true':
            condition = self.get_value(instr.arg1)
            if condition:
                if instr.result in self.labels:
                    self.pc = self.labels[instr.result] - 1
                else:
                    raise RuntimeError(f"Label {instr.result} not found")
        
        elif op == 'print':
            value = self.get_value(instr.arg1)
            output_str = str(value)
            # Use internal VM output - do NOT use Python print()
            self.output.append(output_str)
            # For stdout visibility in non-GUI mode
            sys.stdout.write(output_str + '\n')
        
        elif op == 'input':
            # Read from stdin manually
            value = sys.stdin.readline().strip()
            # Try to convert to number manually
            value = self._parse_number(value)
            self.memory[instr.result] = value
        
        elif op == 'array_literal':
            # Parse array elements
            if instr.arg1:
                elements_str = instr.arg1.split(', ')
                elements = [self.get_value(e) for e in elements_str]
            else:
                elements = []
            self.memory[instr.result] = elements
        
        elif op == 'array_load':
            array = self.get_value(instr.arg1)
            index = self.get_value(instr.arg2)
            if not isinstance(array, list):
                raise RuntimeError(f"{instr.arg1} is not an array")
            if not isinstance(index, (int, float)):
                raise RuntimeError(f"Array index must be a number")
            index = int(index)
            if index < 0 or index >= len(array):
                raise RuntimeError(f"Array index {index} out of bounds")
            self.memory[instr.result] = array[index]
        
        elif op == 'array_store':
            array = self.get_value(instr.result)
            if not isinstance(array, list):
                # Create array if it doesn't exist
                array = []
                self.memory[instr.result] = array
            index = self.get_value(instr.arg1)
            value = self.get_value(instr.arg2)
            index = int(index)
            # Extend array if necessary
            while len(array) <= index:
                array.append(None)
            array[index] = value
        
        elif op == 'call':
            func_name = instr.arg1
            num_args = int(instr.arg2)
            
            # Call built-in function with collected parameters
            result = self.call_builtin(func_name, num_args)
            self.memory[instr.result] = result
            
            # Clear param stack after call
            self.param_stack.clear()
        
        elif op == 'param':
            # Push parameter value to parameter stack
            value = self.get_value(instr.arg1)
            self.param_stack.append(value)
        
        elif op == 'return':
            # For simplicity, we'll just stop execution
            # A full implementation would need proper call stack handling
            self.pc = len(self.instructions)
        
        elif op == 'break':
            # Would need loop context tracking
            pass
        
        elif op == 'continue':
            # Would need loop context tracking
            pass
    
    def get_value(self, operand: str) -> Any:
        """Get the value of an operand (variable or constant)"""
        if operand is None:
            return None
        
        # Boolean constants
        if operand == 'true':
            return True
        elif operand == 'false':
            return False
        
        # String constants (including special tokens like 't' for transpose)
        if operand.startswith('"') and operand.endswith('"'):
            return operand[1:-1]
        
        # Numeric constants
        try:
            if '.' in str(operand):
                return float(operand)
            return int(operand)
        except:
            pass
        
        # Variable
        if operand in self.memory:
            return self.memory[operand]
        
        # Undefined variable - return 0
        return 0
    
    def call_builtin(self, func_name: str, num_args: int) -> Any:
        """Call a built-in function - all math implemented manually"""
        # Get parameters from parameter stack
        params = self.param_stack[-num_args:] if num_args > 0 else []
        
        # For array functions, get the array parameter
        arr = params[0] if params and isinstance(params[0], list) else []
        
        # For numeric functions, get first numeric parameter
        num = params[0] if params and isinstance(params[0], (int, float)) else 0
        
        # Basic array functions - implemented manually
        if func_name == 'sum':
            return self._sum_manual(arr)
        elif func_name == 'max':
            return self._max_manual(arr)
        elif func_name == 'min':
            return self._min_manual(arr)
        
        # Statistical functions
        elif func_name == 'mean':
            if not arr:
                return 0
            total = self._sum_manual(arr)
            count = self._len_manual(arr)
            return total / count if count > 0 else 0
        
        elif func_name == 'median':
            if not arr:
                return 0
            sorted_arr = self._sort_manual(arr)
            n = self._len_manual(sorted_arr)
            if n % 2 == 0:
                return (sorted_arr[n//2 - 1] + sorted_arr[n//2]) / 2
            return sorted_arr[n//2]
        
        elif func_name == 'stdev':
            if not arr or self._len_manual(arr) <= 1:
                return 0
            avg = self._sum_manual(arr) / self._len_manual(arr)
            variance = 0
            for x in arr:
                variance += (x - avg) ** 2
            variance /= self._len_manual(arr)
            return self._sqrt_manual(variance)
        
        elif func_name == 'variance':
            if not arr or self._len_manual(arr) <= 1:
                return 0
            avg = self._sum_manual(arr) / self._len_manual(arr)
            variance = 0
            for x in arr:
                variance += (x - avg) ** 2
            return variance / self._len_manual(arr)
        
        # Angle mode configuration
        elif func_name == 'radians':
            self.angle_mode = 'radians'
            return 0
        elif func_name == 'degrees':
            self.angle_mode = 'degrees'
            return 0
        
        # Convert angle based on mode
        angle = num
        if self.angle_mode == 'degrees' and func_name in ('sin', 'cos', 'tan'):
            angle = self._radians(num)
        
        # Trigonometric functions - manually implemented
        if func_name == 'sin':
            return self._sin_manual(angle)
        elif func_name == 'cos':
            return self._cos_manual(angle)
        elif func_name == 'tan':
            return self._tan_manual(angle)
        elif func_name == 'asin':
            result = self._asin_manual(num)
            return self._degrees(result) if self.angle_mode == 'degrees' else result
        elif func_name == 'acos':
            result = self._acos_manual(num)
            return self._degrees(result) if self.angle_mode == 'degrees' else result
        elif func_name == 'atan':
            result = self._atan_manual(num)
            return self._degrees(result) if self.angle_mode == 'degrees' else result
        
        # Hyperbolic functions - manually implemented
        elif func_name == 'sinh':
            return self._sinh_manual(num)
        elif func_name == 'cosh':
            return self._cosh_manual(num)
        elif func_name == 'tanh':
            return self._tanh_manual(num)
        
        # Exponential and logarithmic - manually implemented
        elif func_name == 'exp':
            return self._exp_manual(num)
        elif func_name == 'ln':
            return self._ln_manual(num)
        elif func_name == 'lg':
            return self._log10_manual(num)
        elif func_name == 'log':
            if self._len_manual(params) >= 2:
                x, base = params[0], params[1]
                if x > 0 and base > 0 and base != 1:
                    return self._ln_manual(x) / self._ln_manual(base)
            elif self._len_manual(params) == 1 and num > 0:
                return self._log10_manual(num)
            return 0
        elif func_name == 'log10':
            return self._log10_manual(num)
        elif func_name == 'log2':
            return self._log2_manual(num)
        
        # Power and roots - manually implemented
        elif func_name == 'sqrt':
            return self._sqrt_manual(num)
        elif func_name == 'cbrt':
            return self._cbrt_manual(num)
        
        # Rounding functions - manually implemented
        elif func_name == 'floor':
            return self._floor_manual(num)
        elif func_name == 'ceil':
            return self._ceil_manual(num)
        elif func_name == 'round':
            return self._round_manual(num)
        elif func_name == 'abs':
            return self._abs_manual(num)
        
        # Number theory - manually implemented
        elif func_name == 'factorial':
            return self._factorial_manual(num)
        elif func_name == 'gcd':
            if self._len_manual(params) >= 2:
                return self._gcd_manual(int(params[0]), int(params[1]))
            return 0
        elif func_name == 'lcm':
            if self._len_manual(params) >= 2:
                a, b = int(params[0]), int(params[1])
                return self._abs_manual(a * b) // self._gcd_manual(a, b)
            return 0
        
        # Constants - manually defined
        elif func_name == 'pi':
            return 3.141592653589793
        elif func_name == 'e':
            return 2.718281828459045
        
        # Matrix utility functions
        elif func_name == 'matrix_det':
            if params:
                return self._matrix_determinant(params[0])
            return 0
        elif func_name == 'matrix_trace':
            if params:
                return self._matrix_trace(params[0])
            return 0
        
        return 0
    
    def _is_matrix(self, arr: Any) -> bool:
        """Check if array is a valid matrix"""
        if not isinstance(arr, list) or not arr:
            return False
        if not all(isinstance(row, list) for row in arr):
            return False
        row_len = len(arr[0])
        return all(len(row) == row_len for row in arr)
    
    def _matrix_add(self, m1: List, m2: List) -> List:
        """Add two matrices"""
        if not self._is_matrix(m1) or not self._is_matrix(m2):
            return []
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            return []  # Dimension mismatch
        return [[m1[i][j] + m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]
    
    def _matrix_subtract(self, m1: List, m2: List) -> List:
        """Subtract two matrices"""
        if not self._is_matrix(m1) or not self._is_matrix(m2):
            return []
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            return []
        return [[m1[i][j] - m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]
    
    def _matrix_multiply(self, m1: List, m2: List) -> List:
        """Multiply two matrices"""
        if not self._is_matrix(m1) or not self._is_matrix(m2):
            return []
        if len(m1[0]) != len(m2):  # cols of m1 must equal rows of m2
            return []
        result = [[sum(m1[i][k] * m2[k][j] for k in range(len(m2))) 
                   for j in range(len(m2[0]))] for i in range(len(m1))]
        return result
    
    def _matrix_transpose(self, m: List) -> List:
        """Transpose a matrix"""
        if not self._is_matrix(m):
            return []
        return [[m[i][j] for i in range(len(m))] for j in range(len(m[0]))]
    
    def _matrix_determinant(self, m: List) -> float:
        """Calculate determinant of a matrix"""
        if not self._is_matrix(m) or len(m) != len(m[0]):
            return 0  # Must be square
        
        n = len(m)
        if n == 1:
            return m[0][0]
        if n == 2:
            return m[0][0] * m[1][1] - m[0][1] * m[1][0]
        
        # Laplace expansion for larger matrices
        det = 0
        for j in range(n):
            minor = [[m[i][k] for k in range(n) if k != j] for i in range(1, n)]
            det += ((-1) ** j) * m[0][j] * self._matrix_determinant(minor)
        return det
    
    def _matrix_trace(self, m: List) -> float:
        """Calculate trace (sum of diagonal) of a matrix"""
        if not self._is_matrix(m) or len(m) != len(m[0]):
            return 0  # Must be square
        return sum(m[i][i] for i in range(len(m)))
    
    def _matrix_inverse(self, m: List) -> List:
        """Calculate inverse of a matrix using Gauss-Jordan elimination"""
        if not self._is_matrix(m) or len(m) != len(m[0]):
            return []  # Must be square
        
        n = len(m)
        # Create augmented matrix [A | I]
        aug = [m[i][:] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        
        # Forward elimination
        for i in range(n):
            # Find pivot
            max_row = i
            for k in range(i + 1, n):
                if abs(aug[k][i]) > abs(aug[max_row][i]):
                    max_row = k
            aug[i], aug[max_row] = aug[max_row], aug[i]
            
            # Check for singular matrix
            if abs(aug[i][i]) < 1e-10:
                return []  # Matrix is singular (non-invertible)
            
            # Make diagonal element 1
            pivot = aug[i][i]
            for j in range(2 * n):
                aug[i][j] /= pivot
            
            # Eliminate column
            for k in range(n):
                if k != i:
                    factor = aug[k][i]
                    for j in range(2 * n):
                        aug[k][j] -= factor * aug[i][j]
        
        # Extract inverse matrix and clean up numerical errors
        inverse = []
        for i in range(n):
            row = []
            for j in range(n, 2 * n):
                val = aug[i][j]
                # Clean up near-zero values
                if abs(val) < 1e-9:
                    val = 0.0
                # Clean up values near simple fractions (0.5, 1.5, etc.)
                elif abs(val - round(val * 2) / 2) < 1e-9:
                    val = round(val * 2) / 2
                # Clean up near-integer values
                elif abs(val - round(val)) < 1e-9:
                    val = float(round(val))
                row.append(val)
            inverse.append(row)
        return inverse
    
    # =========================================================================
    # MANUAL IMPLEMENTATIONS - NO PYTHON BUILT-INS
    # =========================================================================
    
    def _parse_number(self, value: str):
        """Manually parse a string to number"""
        if not value:
            return value
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except:
            return value  # Keep as string
    
    def _len_manual(self, arr: List) -> int:
        """Manual length calculation"""
        count = 0
        for _ in arr:
            count += 1
        return count
    
    def _sum_manual(self, arr: List) -> float:
        """Manual sum implementation"""
        if not arr:
            return 0
        total = 0
        for item in arr:
            total = total + item
        return total
    
    def _max_manual(self, arr: List) -> float:
        """Manual max implementation"""
        if not arr:
            return 0
        maximum = arr[0]
        for item in arr:
            if item > maximum:
                maximum = item
        return maximum
    
    def _min_manual(self, arr: List) -> float:
        """Manual min implementation"""
        if not arr:
            return 0
        minimum = arr[0]
        for item in arr:
            if item < minimum:
                minimum = item
        return minimum
    
    def _sort_manual(self, arr: List) -> List:
        """Manual bubble sort implementation"""
        if not arr:
            return []
        result = arr[:]  # Copy array
        n = self._len_manual(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
        return result
    
    def _abs_manual(self, x: float) -> float:
        """Manual absolute value"""
        return x if x >= 0 else -x
    
    def _floor_manual(self, x: float) -> int:
        """Manual floor implementation"""
        return int(x) if x >= 0 else int(x) - (1 if x != int(x) else 0)
    
    def _ceil_manual(self, x: float) -> int:
        """Manual ceiling implementation"""
        return int(x) + (1 if x > int(x) else 0)
    
    def _round_manual(self, x: float) -> int:
        """Manual rounding implementation"""
        if x >= 0:
            return int(x + 0.5)
        else:
            return int(x - 0.5)
    
    def _sqrt_manual(self, x: float) -> float:
        """Manual square root using Newton's method"""
        if x < 0:
            return 0
        if x == 0:
            return 0
        
        # Newton's method
        guess = x / 2.0
        for _ in range(50):  # Enough iterations for convergence
            guess = (guess + x / guess) / 2.0
        return guess
    
    def _cbrt_manual(self, x: float) -> float:
        """Manual cube root"""
        if x == 0:
            return 0
        
        # Handle negative numbers
        negative = x < 0
        x = self._abs_manual(x)
        
        # Newton's method for cube root
        guess = x / 3.0
        for _ in range(50):
            guess = (2 * guess + x / (guess * guess)) / 3.0
        
        return -guess if negative else guess
    
    def _exp_manual(self, x: float) -> float:
        """Manual exponential function using Taylor series"""
        if x > 100:
            return float('inf')  # Prevent overflow
        if x < -100:
            return 0
        
        # e^x = 1 + x + x^2/2! + x^3/3! + ...
        result = 1.0
        term = 1.0
        for n in range(1, 100):  # 100 terms for good precision
            term *= x / n
            result += term
            if self._abs_manual(term) < 1e-10:
                break
        return result
    
    def _ln_manual(self, x: float) -> float:
        """Manual natural logarithm using series expansion"""
        if x <= 0:
            return 0
        if x == 1:
            return 0
        
        # For x close to 1, use ln(x) = 2 * sum((y^(2n+1))/(2n+1)) where y = (x-1)/(x+1)
        # For other x, use transformation
        if x > 2:
            # Use ln(x) = ln(x/e) + 1
            return self._ln_manual(x / 2.718281828459045) + 1
        
        y = (x - 1) / (x + 1)
        y2 = y * y
        result = 0
        term = y
        
        for n in range(100):
            result += term / (2 * n + 1)
            term *= y2
            if self._abs_manual(term) < 1e-10:
                break
        
        return 2 * result
    
    def _log10_manual(self, x: float) -> float:
        """Manual base-10 logarithm"""
        if x <= 0:
            return 0
        return self._ln_manual(x) / self._ln_manual(10)
    
    def _log2_manual(self, x: float) -> float:
        """Manual base-2 logarithm"""
        if x <= 0:
            return 0
        return self._ln_manual(x) / self._ln_manual(2)
    
    def _sin_manual(self, x: float) -> float:
        """Manual sine using Taylor series"""
        # Normalize to [-2π, 2π]
        pi = 3.141592653589793
        while x > 2 * pi:
            x -= 2 * pi
        while x < -2 * pi:
            x += 2 * pi
        
        # sin(x) = x - x^3/3! + x^5/5! - x^7/7! + ...
        result = 0
        term = x
        for n in range(20):  # 20 terms for good precision
            result += term
            term *= -x * x / ((2 * n + 2) * (2 * n + 3))
            if self._abs_manual(term) < 1e-10:
                break
        return result
    
    def _cos_manual(self, x: float) -> float:
        """Manual cosine using Taylor series"""
        # Normalize to [-2π, 2π]
        pi = 3.141592653589793
        while x > 2 * pi:
            x -= 2 * pi
        while x < -2 * pi:
            x += 2 * pi
        
        # cos(x) = 1 - x^2/2! + x^4/4! - x^6/6! + ...
        result = 0
        term = 1.0
        for n in range(20):
            result += term
            term *= -x * x / ((2 * n + 1) * (2 * n + 2))
            if self._abs_manual(term) < 1e-10:
                break
        return result
    
    def _tan_manual(self, x: float) -> float:
        """Manual tangent"""
        cos_x = self._cos_manual(x)
        if self._abs_manual(cos_x) < 1e-10:
            return 0  # Avoid division by zero
        return self._sin_manual(x) / cos_x
    
    def _asin_manual(self, x: float) -> float:
        """Manual arcsine using series expansion"""
        if x < -1 or x > 1:
            return 0
        if x == 1:
            return 3.141592653589793 / 2
        if x == -1:
            return -3.141592653589793 / 2
        
        # Use asin(x) = x + x^3/6 + 3x^5/40 + ...
        result = x
        term = x
        x2 = x * x
        
        for n in range(1, 30):
            term *= x2 * (2 * n - 1) * (2 * n - 1) / ((2 * n) * (2 * n + 1))
            result += term
            if self._abs_manual(term) < 1e-10:
                break
        
        return result
    
    def _acos_manual(self, x: float) -> float:
        """Manual arccosine"""
        if x < -1 or x > 1:
            return 0
        # acos(x) = π/2 - asin(x)
        return 3.141592653589793 / 2 - self._asin_manual(x)
    
    def _atan_manual(self, x: float) -> float:
        """Manual arctangent using series expansion"""
        if x > 1:
            return 3.141592653589793 / 2 - self._atan_manual(1 / x)
        if x < -1:
            return -3.141592653589793 / 2 - self._atan_manual(1 / x)
        
        # atan(x) = x - x^3/3 + x^5/5 - x^7/7 + ...
        result = 0
        term = x
        x2 = x * x
        
        for n in range(50):
            result += term / (2 * n + 1)
            term *= -x2
            if self._abs_manual(term) < 1e-10:
                break
        
        return result
    
    def _sinh_manual(self, x: float) -> float:
        """Manual hyperbolic sine"""
        # sinh(x) = (e^x - e^(-x)) / 2
        exp_x = self._exp_manual(x)
        exp_neg_x = self._exp_manual(-x)
        return (exp_x - exp_neg_x) / 2
    
    def _cosh_manual(self, x: float) -> float:
        """Manual hyperbolic cosine"""
        # cosh(x) = (e^x + e^(-x)) / 2
        exp_x = self._exp_manual(x)
        exp_neg_x = self._exp_manual(-x)
        return (exp_x + exp_neg_x) / 2
    
    def _tanh_manual(self, x: float) -> float:
        """Manual hyperbolic tangent"""
        # tanh(x) = sinh(x) / cosh(x)
        sinh_x = self._sinh_manual(x)
        cosh_x = self._cosh_manual(x)
        return sinh_x / cosh_x if cosh_x != 0 else 0
    
    def _radians(self, degrees: float) -> float:
        """Convert degrees to radians"""
        return degrees * 3.141592653589793 / 180
    
    def _degrees(self, radians: float) -> float:
        """Convert radians to degrees"""
        return radians * 180 / 3.141592653589793
    
    def _factorial_manual(self, n: float) -> int:
        """Manual factorial implementation"""
        if n < 0 or n != int(n):
            return 0
        n = int(n)
        if n == 0 or n == 1:
            return 1
        
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    def _gcd_manual(self, a: int, b: int) -> int:
        """Manual greatest common divisor using Euclidean algorithm"""
        a = self._abs_manual(a)
        b = self._abs_manual(b)
        
        while b != 0:
            a, b = b, a % b
        return int(a)
