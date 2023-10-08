# 计算在不同的储蓄率和投资回报率下，需要多少年才能实现财务自由

from scipy.optimize import newton

# Testing the function for some example values
A = 30  # 30 periods annuity
r_values = [0.3, 0.5, 0.65] # savings rate
i_values = [0.03, 0.05, 0.07, 0.1, 0.15] # investment rate
def compute_M_safe(A, r, i, initial_guess=20):
    B = r / (1-r)
    
    def equation(M):
        return A - B * ((1+i)**M - 1)/i
    
    try:
        # Use Newton's method to find the root (i.e., the value of M)
        M = newton(equation, initial_guess)
        return M
    except RuntimeError:
        return None

# Testing the function with different initial guesses
results = {}
initial_guesses = [10, 20, 30, 40]
for r in r_values:
    for i in i_values:
        M_values = [compute_M_safe(A, r, i, guess) for guess in initial_guesses]
        M_values = [m for m in M_values if m is not None]
        results[(r, i)] = min(M_values, default=None) if M_values else None

for (r, i), M in results.items():
    print(f"r={r}, i={i}, M={M}")
