# Phase 3: Semantic Analysis - CalcScript++ Compiler

## Overview

This document describes the comprehensive semantic analysis implementation for the CalcScript++ compiler. The semantic analyzer performs type checking, scope management, and builds a detailed symbol table that tracks all identifiers with their properties.

---

## Features Implemented

### 1. **Comprehensive Symbol Table**

The symbol table tracks the following information for each identifier:

| Property       | Description                 | Example                                      |
| -------------- | --------------------------- | -------------------------------------------- |
| **Name**       | Identifier name             | `x`, `total`, `calculateSum`                 |
| **Kind**       | Symbol category             | `variable`, `function`                       |
| **Type**       | Data type                   | `int`, `float`, `string`, `boolean`, `array` |
| **Value/Init** | Initial value or expression | `10`, `"hello"`, `(x + y)`                   |
| **Scope**      | Nested scope depth          | `0` (global), `1` (nested)                   |
| **Line**       | Line number where declared  | `19`, `25`                                   |
| **Init**       | Initialization status       | `✓` (initialized), `✗` (not initialized)     |
| **Used**       | Usage tracking              | `✓` (used), `✗` (unused)                     |

### 2. **Type Checking**

#### **Arithmetic Operations** (`+`, `-`, `*`, `/`, `%`, `^`)

- ✅ Verifies operands are numeric types
- ✅ Handles string concatenation with `+`
- ✅ Supports matrix operations (`+`, `-`, `*`)
- ✅ Result type: `int` if both operands are `int`, otherwise `float`

**Example Error:**

```
"hello" + 5  // Error: Invalid operands for +: string and number
```

#### **Comparison Operations** (`>`, `<`, `>=`, `<=`, `==`, `!=`)

- ✅ Verifies operands are compatible types
- ✅ Result type: always `boolean`

**Example Error:**

```
5 > "hello"  // Error: Invalid operands for >: number and string
```

#### **Logical Operations** (`and`, `or`, `not`)

- ✅ Verifies operands are boolean type
- ✅ Result type: `boolean`

**Example Error:**

```
5 and true  // Error: Invalid operands for and: number and boolean
```

#### **Assignment Operations** (`=`)

- ✅ Verifies right-hand side type matches variable declaration type
- ✅ Tracks initialization of variables

**Example Error:**

```
int x = "hello"  // Error: Type mismatch: variable 'x' declared as int but assigned string
```

### 3. **Scope Management**

- **Global Scope (Level 0)**: Variables accessible everywhere
- **Local Scopes (Level 1+)**: Variables in functions, loops, conditionals
- ✅ Variables in inner scope can shadow outer scope variables
- ✅ Variables go out of scope when exiting a block
- ✅ Variables must be declared before use

**Example:**

```calcscript
int x = 10       // Global scope (level 0)

int myFunc():
    int x = 20   // Local scope (level 1) - shadows global x
    return x
end

print x          // Prints 10 (global x)
```

### 4. **Declaration Checking**

- ✅ No duplicate declarations in same scope
- ✅ Variables declared before use
- ✅ Functions declared before being called
- ✅ No redeclaration of variables in same scope

**Error Examples:**

```calcscript
int x = 5
int x = 10       // Error: Variable 'x' already declared in current scope

print z          // Error: Variable 'z' not declared
```

### 5. **Control Flow Analysis**

- ✅ `if` conditions must evaluate to boolean
- ✅ `while`/`repeat` conditions must evaluate to boolean
- ✅ `return` statements checked in function context
- ✅ Break/continue statements checked in loop context

**Error Examples:**

```calcscript
if (5):          // Error: If condition must be boolean, got number
    print "yes"
end

return 10        // Error: Return statement outside function
```

### 6. **Function Validation**

- ✅ Function existence verification
- ✅ Parameter count validation
- ✅ Parameter type checking (when implemented)
- ✅ Return type tracking

**Example:**

```calcscript
int add(int a, int b):
    return a + b
end

int result = add(10, 20)  // ✓ Valid
int bad = add(10)         // Error: Wrong argument count
```

---

## Output Format

### **Success Case:**

```
✅ [OK] Semantic analysis passed

📊 SYMBOL TABLE
================================================================================
Symbol          Kind         Type       Value/Init                Scope   Line   Init  Used
================================================================================
📌 VARIABLES:
--------------------------------------------------------------------------------
  x             variable     number     10                        0       1      ✓     ✓
  y             variable     number     20                        0       2      ✓     ✓
  total         variable     number     (x + y)                   0       3      ✓     ✓
  name          variable     string     "CalcScript++"            0       4      ✓     ✗

🔧 FUNCTIONS:
--------------------------------------------------------------------------------
  add           function     int        -                         0       8      ✓     ✓

================================================================================

📋 TYPE CHECKING SUMMARY:
--------------------------------------------------------------------------------
✓ Variables declared: 4
✓ Functions defined: 1
✓ All type checks passed
✓ All scope validations passed

⚠ WARNING: 1 unused variable(s): name

✅ No semantic errors found.
```

### **Error Case:**

```
[ERROR] Semantic analysis failed

Semantic error: Type mismatch: variable 'total' declared as int but assigned string
Semantic error: Variable 'z' not declared
Semantic error: Return statement outside function

Compilation stopped due to semantic errors.
```

---

## Implementation Details

### **SymbolTable Class**

```python
class SymbolTable:
    def define(self, name, symbol_type, value_type, init_value, line_number):
        """Define a new symbol with comprehensive tracking"""
        self.symbols[name] = {
            'type': symbol_type,              # 'variable' or 'function'
            'value_type': value_type,         # 'number', 'string', 'boolean', 'array'
            'scope_level': self.scope_level,  # Nesting depth
            'init_value': init_value,         # Initial value or expression
            'line_number': line_number,       # Line where declared
            'is_initialized': init_value is not None,
            'is_used': False
        }

    def mark_used(self, name):
        """Mark a symbol as used"""
        # Marks variable as referenced in code
```

### **Expression String Conversion**

The `get_expr_string()` method converts AST nodes to readable strings:

```python
NumberNode(10)               → "10"
StringNode("hello")          → '"hello"'
BinaryOpNode(x, +, y)        → "(x + y)"
ArrayLiteralNode([1, 2, 3])  → "[1, 2, 3]"
FunctionCallNode(add, [5,3]) → "add(5, 3)"
```

### **Visitor Pattern**

The semantic analyzer uses the visitor pattern to traverse the AST:

```python
def visit_VarDeclNode(self, node):
    # Get initialization expression as string
    init_expr = self.get_expr_string(node.value)

    # Get line number if available
    line_num = getattr(node, 'line', None)

    # Define variable with comprehensive info
    self.current_scope.define(
        node.name,
        'variable',
        declared_type,
        init_expr,
        line_num
    )
```

---

## Semantic Errors Detected

### **Critical Errors (Stop Compilation):**

1. ❌ **Type mismatch** in operations
2. ❌ **Undeclared** variable/function usage
3. ❌ **Duplicate declarations** in same scope
4. ❌ **Invalid function calls** (wrong argument count/types)
5. ❌ **Return type mismatch**
6. ❌ **Control flow violations** (return outside function, break outside loop)

### **Warnings (Allow Compilation):**

1. ⚠️ **Unused variables**
2. ⚠️ **Variables declared but never initialized before use**
3. ⚠️ **Dead code** (unreachable statements)
4. ⚠️ **Implicit type conversions**

---

## Test Cases

### **Test 1: Valid Program**

**Code:**

```calcscript
int x = 10
int y = 20
int total = x + y

if total > 25:
    print "Greater than 25!"
else:
    print "Not greater"
end
```

**Expected:** ✅ Pass semantic analysis with 3 variables tracked

---

### **Test 2: Type Mismatch Error**

**Code:**

```calcscript
int x = 10
string name = "Alice"
int result = x + name
```

**Expected:** ❌ Error: Invalid operands for +: number and string

---

### **Test 3: Undeclared Variable**

**Code:**

```calcscript
int x = 10
print y
```

**Expected:** ❌ Error: Variable 'y' not declared

---

### **Test 4: Scope Error**

**Code:**

```calcscript
if true:
    int temp = 100
end
print temp
```

**Expected:** ❌ Error: Variable 'temp' not in scope

---

### **Test 5: Unused Variable Warning**

**Code:**

```calcscript
int x = 10
int y = 20
int unused = 5
print x + y
```

**Expected:** ✅ Pass with warning: "unused variable: unused"

---

## GUI Display Features

The GUI displays semantic analysis results with:

- **📊 Symbol Table Header** with column names
- **📌 Variables Section** with all variable details
- **🔧 Functions Section** with function signatures
- **📋 Type Checking Summary** with statistics
- **⚠️ Warnings** for unused variables
- **✅ Success indicator** or error messages

### **Column Format:**

```
Symbol          Kind         Type       Value/Init                Scope   Line   Init  Used
  x             variable     number     10                        0       19     ✓     ✓
  calculateSum  function     int        -                         0       25     ✓     ✓
```

---

## Usage in Compiler Pipeline

```
Source Code
    ↓
[Phase 1] Lexical Analysis → Tokens
    ↓
[Phase 2] Syntax Analysis → AST
    ↓
[Phase 3] Semantic Analysis → Symbol Table + Type Checking  ← YOU ARE HERE
    ↓
[Phase 4] IR Generation → Three-Address Code
    ↓
[Phase 5] Optimization → Optimized TAC
    ↓
[Phase 6] Execution → Program Output
```

---

## Success Criteria

Your semantic analyzer is correct when it:

- ✅ Builds complete and accurate symbol table
- ✅ Catches all type mismatches
- ✅ Detects all undeclared identifiers
- ✅ Enforces scope rules correctly
- ✅ Validates function calls properly
- ✅ Produces clear, actionable error messages
- ✅ Only passes programs that are semantically valid
- ✅ Tracks initialization values and usage
- ✅ Reports line numbers for errors
- ✅ Warns about unused variables

---

## Files Modified

1. **`semantic_analyzer.py`**

   - Enhanced `SymbolTable.define()` with comprehensive tracking
   - Added `SymbolTable.mark_used()` for usage tracking
   - Added `get_expr_string()` for expression-to-string conversion
   - Updated `visit_VarDeclNode()` to capture initialization expressions
   - Updated `visit_IdentifierNode()` to mark variables as used

2. **`gui.py`**
   - Enhanced semantic analysis display with 120-character wide table
   - Added icons (📊, 📌, 🔧, 📋, ⚠️, ✅)
   - Separated variables and functions sections
   - Added type checking summary
   - Added unused variable warnings
   - Updated both `compile_and_run()` and `compile_only()` methods

---

## Demo File

Run `test_semantic_demo.calc` to see:

- Variable declarations with various types
- Initialization tracking
- Expression evaluation
- Function definitions
- Usage tracking
- Comprehensive symbol table output

---

## Conclusion

The semantic analysis phase is now fully implemented with comprehensive symbol tracking, detailed type checking, scope management, and clear visual output. The system provides developers with complete visibility into their program's semantic structure and catches errors early in the compilation process.

**Try it out:** Load the GUI and compile `test_semantic_demo.calc` to see the enhanced semantic analysis in action!
