def gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a or 1


def factor_sqrt(n: int) -> tuple[int, int]:
    """Return (coeff, radicand) such that √n = coeff * √radicand, radicand square-free."""
    coeff = 1
    i = 2
    while i * i <= n:
        while n % (i * i) == 0:
            coeff *= i
            n //= (i * i)
        i += 1
    return coeff, n