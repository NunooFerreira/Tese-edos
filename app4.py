from fastapi import FastAPI
import time

app = FastAPI()

def calculate_fibonacci(n: int):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

@app.get("/fib")
async def fibonacci():
    start_time = time.time()
    number = 10
    result = calculate_fibonacci(number)
    duration = time.time() - start_time
    
    return {
        "input_number": number,
        "fibonacci_result": result,
        "computation_time_sec": duration
    }
