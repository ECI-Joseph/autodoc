# Calculator Module

## Summary
A simple utility module providing basic arithmetic operations and a calculator class to perform incremental calculations.

## Classes

- **Calculator**: A class that maintains a running value and provides methods to modify it. Initialized with an optional starting value (default: 0).

## Functions

- **add(a, b)**  
  Adds two numbers and returns the result.  
  - Args:  
    - `a` (int/float): First number.  
    - `b` (int/float): Second number.  
  - Returns:  
    - int/float: Sum of `a` and `b`.

- **subtract(a, b)**  
  Subtracts the second number from the first and returns the result.  
  - Args:  
    - `a` (int/float): Minuend.  
    - `b` (int/float): Subtrahend.  
  - Returns:  
    - int/float: Difference of `a` and `b`.

- **calculate_stats(numbers)**  
  Computes statistical summary for a list of numbers.  
  - Args:  
    - `numbers` (list of int/float): List of numeric values.  
  - Returns:  
    - dict: Dictionary containing:  
      - `"total"` (int/float): Sum of all numbers.  
      - `"count"` (int): Number of elements in the list.  
      - `"average"` (float): Mean value; 0 if list is empty.

## API Usage (If applicable)
This module does not contain any HTTP endpoints or web APIs. It is a standalone utility library for arithmetic and statistical operations.