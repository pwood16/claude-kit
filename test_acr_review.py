#!/usr/bin/env python3
"""Test file for ACR review with intentional issues"""

def calculate_total(items):
    # Missing type hints
    total = 0
    for item in items:
        total = total + item
    return total

def process_data(data):
    # Unused variable
    result = []
    temp = "unused"
    for i in range(len(data)):
        result.append(data[i] * 2)
    return result

class DataProcessor:
    def __init__(self):
        pass

    def process(self, value):
        # Magic number without explanation
        return value * 42

# Missing docstrings
def helper_function(x, y):
    return x + y

if __name__ == "__main__":
    items = [1, 2, 3]
    print(calculate_total(items))
