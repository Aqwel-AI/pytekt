import time
import numpy as np
from aion.maths.linear_algebra import dot_product, matrix_multiply

def benchmark_vectors():
    print("=== Vector Dot Product Benchmark ===")
    size = 1000000
    u = [1.0] * size
    v = [2.0] * size
    
    np_u = np.array(u)
    np_v = np.array(v)
    
    # Vanilla Python
    start = time.perf_counter()
    res_py = dot_product(u, v)
    py_time = time.perf_counter() - start
    print(f"Vanilla Python: {py_time:.6f} seconds (result: {res_py})")
    
    # NumPy
    start = time.perf_counter()
    res_np = np.dot(np_u, np_v)
    np_time = time.perf_counter() - start
    print(f"NumPy:          {np_time:.6f} seconds (result: {res_np})")
    print(f"Speedup:        {py_time / np_time:.2f}x\n")

def benchmark_matrices():
    print("=== Matrix Multiplication Benchmark ===")
    size = 200
    A = [[1.0] * size for _ in range(size)]
    B = [[2.0] * size for _ in range(size)]
    
    np_A = np.array(A)
    np_B = np.array(B)
    
    # Vanilla Python
    start = time.perf_counter()
    res_py = matrix_multiply(A, B)
    py_time = time.perf_counter() - start
    print(f"Vanilla Python (O(N^3) standard): {py_time:.6f} seconds")
    
    # NumPy
    start = time.perf_counter()
    res_np = np.matmul(np_A, np_B)
    np_time = time.perf_counter() - start
    print(f"NumPy:                             {np_time:.6f} seconds")
    print(f"Speedup:                           {py_time / np_time:.2f}x\n")

if __name__ == "__main__":
    benchmark_vectors()
    benchmark_matrices()
