# CalcScript++ Test Cases

This directory contains all test programs for the CalcScript++ compiler.

## 📁 Directory Structure

```
test_cases/
├── COMPLIANCE_TEST.calc          # Comprehensive compliance verification
├── example.calc                   # Simple demo program
├── test_simple_typed.calc         # Basic typed syntax examples
├── test_manual_math.calc          # Manual math function tests
├── test_matrix_operations.calc    # Matrix operations with operators
├── test_matrix_operators.calc     # Advanced matrix operations
├── run_all_tests.py              # Test runner script
└── tests/                         # Core feature tests
    ├── test1_arithmetic.calc      # Arithmetic operations
    ├── test2_loops_conditionals.calc  # Control structures
    ├── test4_arrays.calc          # Array operations
    └── test5_while_loop.calc      # While loops with break/continue
```

## ✅ All Tests Use Typed Syntax

All test files have been updated to use **explicit static typing** as required by `instructions.md`:

### Old Syntax (REMOVED):

```calcscript
let x = 10
function add(a, b):
    return a + b
end
```

### New Syntax (REQUIRED):

```calcscript
int x = 10
function int add(int a, int b):
    return a + b
end
```

## 🚀 Running Tests

### Run All Tests:

```bash
cd d:\University\CC\PROJECT\4_Submission\test_cases
python run_all_tests.py
```

### Run Individual Test:

```bash
cd d:\University\CC\PROJECT
python 3_Implementation\main.py 4_Submission\test_cases\example.calc
```

### Run Compliance Test:

```bash
python 3_Implementation\main.py 4_Submission\test_cases\COMPLIANCE_TEST.calc
```

## 📝 Test Descriptions

### Core Tests (tests/ folder):

1. **test1_arithmetic.calc**

   - Variable declarations with types
   - Basic arithmetic operations
   - Operator precedence
   - Exponentiation

2. **test2_loops_conditionals.calc**

   - Repeat loops
   - If-else statements
   - Nested conditionals
   - Loop counters

3. **test4_arrays.calc**

   - Array declarations
   - Array indexing
   - Array modification
   - Built-in functions: sum(), max(), min()

4. **test5_while_loop.calc**
   - While loops
   - Break and continue statements
   - Boolean variables
   - Loop conditions

### Feature Tests:

- **COMPLIANCE_TEST.calc**: Comprehensive test demonstrating full compliance
- **example.calc**: Simple demo program
- **test_simple_typed.calc**: Basic typed variable declarations
- **test_manual_math.calc**: Manual math implementations (no Python built-ins)
- **test_matrix_operations.calc**: Matrix addition, subtraction, multiplication, transpose
- **test_matrix_operators.calc**: Advanced matrix operations including inverse

## ✅ Compliance Features Tested

All tests verify:

- ✓ Static typing with explicit types (int, float, string, boolean, array, matrix)
- ✓ Typed function parameters and return types
- ✓ No Python built-ins (print/input replaced with VM output)
- ✓ Manual math implementations (30+ functions from scratch)
- ✓ Matrix operations implemented manually
- ✓ No 'let' keyword usage

## 🎯 Expected Output

All tests should execute successfully and produce correct output without errors.

---

**Last Updated:** November 26, 2025  
**Compiler Version:** CalcScript++ v2.0 (Fully Compliant)
