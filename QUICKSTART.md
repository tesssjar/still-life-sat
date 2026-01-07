# Quick Start Guide

## Installation

### Prerequisites
- Python 3.7+
- Glucose 4.2 SAT solver

### Install Glucose (Windows with WSL)

```bash
# In WSL:
wget http://www.labri.fr/perso/lsimon/glucose/Glucose-4.2.tar.gz
tar xzf Glucose-4.2.tar.gz
cd glucose-4.2
make -C simp
```

The executable will be at `~/glucose/simp/glucose`

## Basic Usage

### Find Maximum Density Still-Life

```bash
# For a 5x5 grid
python life_sat_solver.py 5 --glucose "wsl ~/glucose/simp/glucose"

# For a 3x3 grid
python life_sat_solver.py 3 --glucose "wsl ~/glucose/simp/glucose"
```

### Use Pre-made Instance Files

```bash
# Test 4x4 grid
python life_sat_solver.py instances/4x4.json --glucose "wsl ~/glucose/simp/glucose"

# Test 8x8 grid
python life_sat_solver.py instances/8x8.json --glucose "wsl ~/glucose/simp/glucose"
```

## Output Interpretation

The solver outputs:

1. **Search Progress**: Binary search iterations testing different alive cell counts
2. **Encoding Stats**: Variables and clauses in the SAT formula
3. **Solution Grid**: Visual representation with `#` for alive cells, `.` for dead
4. **Statistics**: 
   - Maximum alive cells found
   - Density percentage
   - Total search time
   - Number of iterations

Example output:
```
[+] OPTIMAL STILL-LIFE FOUND!
    Maximum density: 12 alive cells
    Total search time: 0.34s
    Binary search iterations: 4

[+] Solution found with 12 alive cells:

  ####
  #..#
  #..#
  ####

[+] Alive cells: [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 3), (2, 0), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
[+] Density: 75.00%
```

## Performance Guide

| Grid | Time | Max Cells |
|------|------|-----------|
| 2×2 | <0.1s | 4 |
| 3×3 | 0.3s | 6 |
| 4×4 | 0.4s | 12 |
| 5×5 | 0.5s | 14 |
| 6×6 | 1-2s | 18-20 |
| 7×7 | 2-5s | 22-25 |
| 8×8 | 5-15s | 26-30 |

## Command-Line Options

```bash
python life_sat_solver.py INSTANCE [--glucose PATH]
```

**Arguments:**
- `INSTANCE`: Grid size (2-9) or path to JSON instance file
- `--glucose PATH`: Path to glucose solver executable (default: `glucose`)

**Examples:**
```bash
# Direct grid size
python life_sat_solver.py 5

# Instance file
python life_sat_solver.py instances/5x5.json

# Specify glucose path
python life_sat_solver.py 6 --glucose "wsl ~/glucose/simp/glucose"
```

## Instance Files

Instance files are simple JSON files containing just the grid size:

```json
{
  "description": "5x5 grid - find densest still-life",
  "n": 5
}
```

Ready-made instances are in `instances/`:
- `2x2.json` through `9x9.json` - One for each grid size
- `3x3_alt.json` - Alternative 3×3 instance

## What is a Still-Life?

A **still-life** is a configuration in Conway's Game of Life that remains unchanged over time.

For a configuration to be stable:
- Every alive cell must have exactly 2 or 3 living neighbors
- Every dead cell must NOT have exactly 3 living neighbors

The solver finds the maximum number of alive cells that satisfy these rules on an n×n grid.

## Example Still-Lifes

**2×2 Block (4 cells, 100% density):**
```
##
##
```

**3×3 Pattern (6 cells, 66.67% density):**
```
.##
#.#
##.
```

**4×4 Pattern (12 cells, 75% density):**
```
####
#..#
#..#
####
```

## Troubleshooting

**"glucose" not found**
- Install Glucose 4.2
- Use `--glucose` flag to specify the path:
  ```bash
  python life_sat_solver.py 5 --glucose "/path/to/glucose"
  ```

**Very slow on large grids (7×7+)**
- This is expected with Glucose and SAT solving
- Use smaller grids for quick testing
- 8×8 typically takes 5-15 seconds

**No solution found**
- This means the solver couldn't find a still-life with the exact number of alive cells tested
- The solver searches in binary, so it will find the maximum possible
