# User Input Guide for CalcScript++

## How to Use Input

### Basic Syntax

```calc
type variable_name = initial_value
input variable_name
```

### Examples

**1. Simple Input**

```calc
int age = 0
print "Enter your age:"
input age
print age
```

**2. Multiple Inputs**

```calc
string name = ""
int age = 0
float salary = 0.0

print "Enter name:"
input name
print "Enter age:"
input age
print "Enter salary:"
input salary

print name
print age
print salary
```

**3. Using Input in Calculations**

```calc
int x = 0
int y = 0

print "Enter first number:"
input x
print "Enter second number:"
input y

int sum = x + y
print "Sum is:"
print sum
```

**4. Input in Loops**

```calc
int total = 0

for int i = 0; i < 3; i = i + 1:
    int num = 0
    print "Enter a number:"
    input num
    total = total + num
end

print "Total:"
print total
```

## Running Programs with Input

### Method 1: Interactive (Command Line)

```bash
python main.py your_program.calc
# Then type inputs when prompted
```

### Method 2: Piped Input (PowerShell)

```powershell
@("value1", "value2", "value3") | python main.py your_program.calc
```

### Method 3: From File

```powershell
Get-Content inputs.txt | python main.py your_program.calc
```

### Method 4: Using the GUI

1. Launch the modern GUI
2. Load or write your program
3. Click "▶ RUN ALL PHASES"
4. A dialog will appear for each input statement
5. Type your value and press OK

## Important Notes

1. **Must Declare First**: Variables must be declared with an initial value before using `input`

   ```calc
   int x = 0    # Correct
   input x

   # int x       # Error - missing initial value
   # input x
   ```

2. **Type Conversion**: Input is automatically converted to the variable's type

   - `int` variables: Converts to integer
   - `float` variables: Converts to floating-point
   - `string` variables: Keeps as string

3. **One Variable Per Input**: Each `input` statement reads one value

   ```calc
   int a = 0
   int b = 0
   input a    # Reads first value
   input b    # Reads second value
   ```

4. **Prompts**: Always print a message before input so users know what to enter
   ```calc
   print "Enter your name:"  # Good practice
   string name = ""
   input name
   ```

## Complete Example

```calc
# Simple calculator with user input

print "=== Simple Calculator ==="
print "Enter first number:"
int num1 = 0
input num1

print "Enter second number:"
int num2 = 0
input num2

int sum = num1 + num2
int diff = num1 - num2
int prod = num1 * num2
int quot = num1 / num2

print "Results:"
print "Sum:"
print sum
print "Difference:"
print diff
print "Product:"
print prod
print "Quotient:"
print quot
```

## Test File

See `test_input.calc` in the test_cases folder for a working example.
