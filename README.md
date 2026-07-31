# computor-v2

Interactive math expression interpreter supporting rational numbers, complex numbers, matrices, functions, and polynomial equation solving up to degree 2.

---

## Features

- Math types: rational numbers (ℚ), complex numbers, matrices, single-variable functions
- Variable assignment and reassignment with type changes
- Expression evaluation: `expr = ?`
- Equation solving for degree ≤ 2: `f(x) = 0 ?` and `ax^2 + bx + c = 0 ?`
- Symbolic function composition: `f(g(x)) = ?`
- Function plotting: `plot f`
- Built-in functions: `sqrt`, `abs`, `sin`, `cos`, `tan`, `exp`
- Commands: `vars` (list variables), `exit`
- File mode: `uv run computor -f script.txt`
- Debug mode with logging: `-d`

---

## Architecture

```
user input
    |
    v
ImplicitMultiplyLexer   -- wraps the PLY lexer, injects implicit *
    |
    v
PLY yacc parser  ->  AST Node
    |
    v
Dispatcher
    |
    +-- variable assignment   ->  Interpreter -> Store -> Formatter
    |
    +-- function definition   ->  Normalizer  -> Store -> Formatter
    |
    +-- evaluation (= ?)      ->  Interpreter (or Normalizer when a free variable is present) -> Formatter
    |
    +-- equation solving      ->  Interpreter + Normalizer + PolynomialSolver -> Formatter
    |
    v
output string
```

### Modules

| Module | Purpose |
|--------|---------|
| `parsing/lexer.py` | PLY lexer + InjectMultiply for `2x` → `2 * x` |
| `parsing/parser.py` | PLY grammar → AST |
| `parsing/AST.py` | AST node hierarchy |
| `types.py` | `Rational`, `Complex`, `Irrational`, `Matrix`, `Function` |
| `interpreter.py` | Recursive AST evaluator |
| `normalizer.py` | Constant subexpression folding |
| `solver.py` | Polynomial solver (degree 0–2) |
| `formatter.py` | Formatting for all types |
| `dispatcher.py` | AST node routing |
| `store.py` | Variable store (case-insensitive) |
| `builtins/` | Built-in constants and functions |
| `plotter.py` | Function plotting via matplotlib |
| `computorv2.py` | Entry point: parsing + dispatch |
| `main.py` | CLI: REPL / file mode / debug |

### Data types

| Type | Example values |
|------|----------------|
| `Rational` | `2`, `-4.3`, `1/3 → 0.333333333` |
| `Complex` | `3 + 2i`, `-4 - 4i` |
| `Matrix` | `[[1, 2]; [3, 4]]` |
| `Function` | `f(x) = 2*x^2 - 5` |
| `Irrational` | `√2`, `(1 + √7 * i) / 2` |

---

## Installation and usage

### Local (uv)

```bash
# Install uv
pip install uv

# Clone and install dependencies
git clone https://github.com/kosyan62/computor_v2.git
cd computor_v2
uv sync

# Start the REPL
uv run computor

# File mode
uv run computor -f examples/showcase.txt

# Debug mode
uv run computor -d
```

### Docker

```bash
docker build -t computor-v2 .

# Interactive REPL
docker run -it computor-v2

# File mode
docker run -i computor-v2 -f - < examples/showcase.txt

# Debug mode
docker run -it computor-v2 -d
```

---

## Usage

```
> varA = 2
2
> varB = 4 * varA + 3
11
> f(x) = varA * x^2 - varB * x + 1
f(x) = 2 * x^2 - 11 * x + 1
> f(3) = ?
-14
> f(x) = 0 ?
2x^2 - 11x + 1 = 0
Two solutions in ℝ:
(11 - √113) / 4
(11 + √113) / 4
> g(x) = x + 1
g(x) = x + 1
> f(g(x)) = ?
2x^2 - 7x - 8
> m = [[1,2];[3,4]]
[ 1 , 2 ]
[ 3 , 4 ]
> m ** m = ?
[ 7 , 10 ]
[ 15 , 22 ]
> vars
f(x) = 2 * x^2 - 11 * x + 1
g(x) = x + 1
m = [ 1 , 2 ]\n[ 3 , 4 ]
varA = 2
varB = 11
> plot f
Plotting f(x) on [-10.0, 10.0]
> plot f -2 7
Plotting f(x) on [-2.0, 7.0]
```

### Plot gallery

Generated from [`examples/showcase.txt`](examples/showcase.txt):

```bash
COMPUTOR_PLOT_DIR=imgs uv run computor -f examples/showcase.txt
```

| `damp(x) = exp(-x/5) * cos(3x)` | `sinc(x) = sin(x) / x` |
|---|---|
| ![damp](imgs/damp.png) | ![sinc](imgs/sinc.png) |

| `chirp(x) = sin(x^2)` | `fourier(x) = Σ sin(kx)/k, k=1..4` |
|---|---|
| ![chirp](imgs/chirp.png) | ![fourier](imgs/fourier.png) |

| `circ(x) = sqrt(25 - x^2)` | `q(x) = 1 / (x^2 - 1)` |
|---|---|
| ![circ](imgs/circ.png) | ![q](imgs/q.png) |

The plotter breaks the curve at poles (`q`) and wherever the value is not
real (`circ` outside its domain). When the `COMPUTOR_PLOT_DIR` environment
variable is set, plots are saved as PNG files instead of opening a window.

### Supported operators

| Operator | Description |
|----------|-------------|
| `+`, `-`, `*`, `/` | Standard arithmetic |
| `%` | Modulo |
| `//` | Integer division |
| `^` | Power (scalar) |
| `**` | Matrix multiplication |
| `= ?` | Evaluate expression |
| `f(x) = val ?` | Solve equation |

---

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# With coverage report
uv run pytest tests/ --cov=computor_v2 --cov-report=term-missing
```

**Results:** 10 617 tests, 0 failures.

Test coverage:
- All data types and their operations (`test_types.py`)
- Lexer and parser (`test_parser.py`, `test_lexer.py`)
- Evaluator and normalizer (`test_interpreter.py`, `test_normalizer.py`)
- Dispatcher: assignment, queries, equation solving (`test_dispatcher.py`)
- Formatter and store (`test_formatter.py`, `test_store.py`)
- Built-in functions (`test_builtins.py`)
- Functional tests via `-f` and stdin (`test_functional.py`)
- All examples from the subject (`test_subject_examples.py`)

---

## CI/CD

GitHub Actions runs on every push and pull request to `master`:

```
.github/workflows/ci.yml
  ├── test (ubuntu-latest, python 3.13)
  │     ├── uv sync
  │     ├── pytest tests/ -v
  │     └── ruff check .
  └── build (needs: test)
        ├── uv build          # wheel + sdist
        └── upload-artifact   # computor-v2-dist
```

CI status: [![CI](https://github.com/kosyan62/computor_v2/actions/workflows/ci.yml/badge.svg)](https://github.com/kosyan62/computor_v2/actions/workflows/ci.yml)

---

## Debug mode

```bash
uv run computor -d
```

In debug mode (`-d`) every event is logged to stdout via the `logging` module:

```
[DEBUG] computor_v2: Debug mode enabled. Args: Namespace(debug=True, file=None)
> x = 2 * 4 + 1
[DEBUG] computor_v2: Input: 'x = 2 * 4 + 1'
[DEBUG] computor_v2: AST: Equality
[DEBUG] computor_v2: Result: '9'
9
```

---

## Tech stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.13 |
| Parser | PLY (Python Lex-Yacc) |
| Plotting | matplotlib + PyQt5 |
| Tests | pytest |
| Linter | ruff |
| Package manager | uv |
| CI/CD | GitHub Actions |
| Containerization | Docker |
