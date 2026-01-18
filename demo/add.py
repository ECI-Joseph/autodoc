def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def calculate_stats(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count if count > 0 else 0
    return {
        "total": total,
        "count": count,
        "average": average
    }

class Calculator:
    def __init__(self, initial_value=0):
        self.value = initial_value
    
    def add(self, amount):
        self.value += amount
        return self.value
# updated
