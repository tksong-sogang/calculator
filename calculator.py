def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def main():
    operations = {
        '+': add,
        '-': subtract,
        '*': multiply,
        '/': divide,
    }

    print("Simple Calculator")
    print("Operations: +, -, *, /")
    print("Type 'q' to quit\n")

    while True:
        expr = input("Enter expression (e.g. 3 + 4): ").strip()
        if expr.lower() == 'q':
            break

        parts = expr.split()
        if len(parts) != 3:
            print("Invalid input. Use format: <number> <operator> <number>\n")
            continue

        num1_str, op, num2_str = parts
        if op not in operations:
            print(f"Unknown operator '{op}'. Use +, -, *, /\n")
            continue

        try:
            num1, num2 = float(num1_str), float(num2_str)
            result = operations[op](num1, num2)
            print(f"Result: {result}\n")
        except ValueError as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
