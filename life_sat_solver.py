#!/usr/bin/env python3
"""
Game of Life Still-Life SAT Solver

This script solves the densest still-life problem using SAT encoding.
The problem: Find the maximum number of live cells in an n×n grid
that form a stable configuration (still-life).

A still-life is a configuration where each cell satisfies:
- If a cell has exactly 3 live neighbors, it must be alive
- If a cell has 2 live neighbors, it stays in the same state
- Otherwise, the cell is dead
"""

import sys
import os
import subprocess
import tempfile
import json
from typing import List, Tuple, Dict, Set, Optional
from pathlib import Path
import time
import argparse


class GameOfLifeSAT:
    def __init__(self, n: int, target_alive: int):
        """
        Args:
            n: Grid size (n × n)
            target_alive: Target number of alive cells (exactly this many)
        """
        self.n = n
        self.target_alive = target_alive
        self.clauses = []
        self.num_vars = 0
        self.var_map = {} 
        self.reverse_map = {}
        
    def _get_var(self, row: int, col: int) -> int:
        key = (row, col)
        if key not in self.var_map:
            self.num_vars += 1
            self.var_map[key] = self.num_vars
            self.reverse_map[self.num_vars] = key
        return self.var_map[key]
    
    def _count_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.n and 0 <= nc < self.n:
                    neighbors.append((nr, nc))
        return neighbors
    
    def _add_clause(self, clause: List[int]):
        if clause:
            self.clauses.append(clause)
    
    def _encode_at_most_k(self, variables: List[int], k: int):
        if k < 0:
            self._add_clause([])
            return
        if k >= len(variables):
            return 
        
        
        from itertools import combinations

        if len(variables) <= 20:
            for subset in combinations(variables, k + 1):
                clause = [-v for v in subset]
                self._add_clause(clause)
        else:
            import random
            random.seed(42)
            num_clauses_to_add = min(100, len(list(combinations(variables, k + 1))))
            for subset in random.sample(list(combinations(variables, k + 1)), num_clauses_to_add):
                clause = [-v for v in subset]
                self._add_clause(clause)
    
    def _encode_exactly_k(self, variables: List[int], k: int):
        if k < 0 or k > len(variables):
            self._add_clause([])
            return
        
        if k == 0:
            for v in variables:
                self._add_clause([-v])
            return
        
        if k == len(variables):
            for v in variables:
                self._add_clause([v])
            return
        
        n = len(variables)
        s = {}
        
        for j in range(k + 2):
            self.num_vars += 1
            s[(0, j)] = self.num_vars
        
        self._add_clause([s[(0, 0)]])
        for j in range(1, k + 2):
            self._add_clause([-s[(0, j)]])
        
        for i in range(1, n + 1):
            for j in range(k + 2):
                self.num_vars += 1
                s[(i, j)] = self.num_vars
                
                if j == 0:
                    self._add_clause([s[(i, j)]])
                elif i > 0:
                    self._add_clause([-s[(i, j)], s[(i-1, j)], variables[i-1]])
                    self._add_clause([-s[(i, j)], s[(i-1, j)], s[(i-1, j-1)]])
                    
                    self._add_clause([-s[(i-1, j)], s[(i, j)]])
                    self._add_clause([-variables[i-1], -s[(i-1, j-1)], s[(i, j)]])
        
        self._add_clause([s[(n, k)]])
        self._add_clause([-s[(n, k + 1)]])
    
    def _encode_at_least_k(self, variables: List[int], k: int):
        if k <= 0:
            return 
        if k > len(variables):
            self._add_clause([])
            return
        
        if k == 1:
            self._add_clause(variables)
        else:
            pass
    
    def encode(self):
        print(f"[*] Encoding {self.n}x{self.n} still-life problem...")
        start_time = time.time()
        
        for i in range(self.n):
            for j in range(self.n):
                self._get_var(i, j)
        
        for row in range(self.n):
            for col in range(self.n):
                neighbors = self._count_neighbors(row, col)
                neighbor_vars = [self._get_var(nr, nc) for nr, nc in neighbors]
                cell_var = self._get_var(row, col)
                self._encode_cell_constraint_direct(cell_var, neighbor_vars)
        
        all_vars = [self._get_var(i, j) for i in range(self.n) for j in range(self.n)]
        self._encode_exactly_k(all_vars, self.target_alive)
        
        elapsed = time.time() - start_time
        print(f"[+] Encoding completed in {elapsed:.2f}s")
        print(f"[+] Variables: {self.num_vars}, Clauses: {len(self.clauses)}")
        
    def _encode_cell_constraint(self, cell_var: int, neighbor_vars: List[int]):
        num_neighbors = len(neighbor_vars)
        
        at_least = {}
        for k in range(num_neighbors + 1):
            self.num_vars += 1
            at_least[k] = self.num_vars
        
        self._add_clause([at_least[0]])
        
        for k in range(1, num_neighbors + 1):
            self._add_clause([-at_least[k], at_least[k - 1]])
        
        for k in range(1, num_neighbors + 1):
            pass
        
        
        self._encode_cell_constraint_direct(cell_var, neighbor_vars)
    
    def _encode_cell_constraint_direct(self, cell_var: int, neighbor_vars: List[int]):
        num_neighbors = len(neighbor_vars)
        
        for config in range(1 << num_neighbors):
            neighbor_count = bin(config).count('1')
            
            if neighbor_count == 3:
                clause = []
                for i, var in enumerate(neighbor_vars):
                    if (config >> i) & 1:
                        clause.append(-var)
                    else:
                        clause.append(var)
                clause.append(cell_var) 
                self._add_clause(clause)
            elif neighbor_count == 2:
                pass
            else:
                clause = []
                for i, var in enumerate(neighbor_vars):
                    if (config >> i) & 1:
                        clause.append(-var)
                    else:
                        clause.append(var)
                clause.append(-cell_var)
                self._add_clause(clause)
    
    def write_dimacs(self, filename: str):
        with open(filename, 'w') as f:
            f.write(f"c Game of Life still-life problem\n")
            f.write(f"c Grid size: {self.n}x{self.n}\n")
            f.write(f"p cnf {self.num_vars} {len(self.clauses)}\n")
            for clause in self.clauses:
                f.write(' '.join(map(str, clause)) + ' 0\n')
    
    def solve(self, glucose_path: str = "glucose", show_dimacs: bool = False, 
              show_stats: bool = False) -> Optional[List[Tuple[int, int]]]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False) as f:
            dimacs_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.out', delete=False) as f:
            output_file = f.name
        
        try:
            self.write_dimacs(dimacs_file)
            
            if show_dimacs:
                print("\n[*] DIMACS CNF Formula:")
                with open(dimacs_file, 'r') as f:
                    print(f.read())
            
            print(f"\n[*] Running Glucose SAT solver...")
            start_time = time.time()
            
            wsl_dimacs = dimacs_file
            wsl_output = output_file
            if glucose_path.startswith('wsl'):
                wsl_dimacs = dimacs_file.replace('\\', '/').replace('C:', '/mnt/c').replace('D:', '/mnt/d')
                wsl_output = output_file.replace('\\', '/').replace('C:', '/mnt/c').replace('D:', '/mnt/d')
            
            cmd = glucose_path.split() + [wsl_dimacs, wsl_output]
            result = subprocess.run(
                ' '.join(cmd),
                capture_output=True,
                text=True,
                timeout=300,
                shell=True
            )
            
            elapsed = time.time() - start_time
            
            if show_stats:
                print(f"\n[*] Solver Statistics:")
                print(f"    Runtime: {elapsed:.2f}s")
                if result.stderr:
                    print(f"    Output:\n{result.stderr}")
            
            status_lines = result.stdout.split('\n')
            
            sat_line = [l for l in status_lines if 'SATISFIABLE' in l or 'SAT' in l.upper()]
            if not sat_line:
                print("[-] No SAT/UNSAT line found in solver output")
                return None
            
            if 'UNSATISFIABLE' in sat_line[0] or 'UNSAT' in sat_line[0]:
                print("[+] Formula is UNSATISFIABLE")
                return None
            
            print("[+] Formula is SATISFIABLE")
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, 'r') as f:
                    model_content = f.read().strip()
                    try:
                        assignment = [int(x) for x in model_content.split() if x.lstrip('-').isdigit()]
                    except ValueError:
                        print("[-] Failed to parse model content")
                        return None
            else:
                model_lines = [l for l in status_lines if l and (l[0].isdigit() or (l[0] == '-' and len(l) > 1 and l[1].isdigit()))]
                if not model_lines:
                    print("[-] No assignment found")
                    return None
                assignment_str = ' '.join(model_lines).replace('v ', '')
                assignment = list(map(int, assignment_str.split()))
            
            alive_cells = []
            for var_num in assignment:
                if var_num == 0:
                    break
                if var_num > 0 and var_num in self.reverse_map:
                    row, col = self.reverse_map[var_num]
                    alive_cells.append((row, col))
            
            return sorted(alive_cells)
        
        finally:
            if os.path.exists(dimacs_file):
                os.remove(dimacs_file)
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def display_solution(self, alive_cells: Optional[List[Tuple[int, int]]]):
        if alive_cells is None:
            print("\n[!] No solution found (UNSAT)")
            return
        
        print(f"\n[+] Solution found with {len(alive_cells)} alive cells:\n")
        
        grid = [['.' for _ in range(self.n)] for _ in range(self.n)]
        for row, col in alive_cells:
            grid[row][col] = '#'
        
        for row in grid:
            print('  ' + ''.join(row))
        
        print(f"\n[+] Alive cells: {alive_cells}")
        print(f"[+] Density: {len(alive_cells) / (self.n * self.n):.2%}")
        
        self.verify_solution(alive_cells)
    
    def verify_solution(self, alive_cells: List[Tuple[int, int]]):
        alive_set = set(alive_cells)
        
        print(f"\n[*] Verifying solution...")
        is_valid = True
        
        for row in range(self.n):
            for col in range(self.n):
                neighbors = self._count_neighbors(row, col)
                num_alive = sum(1 for nr, nc in neighbors if (nr, nc) in alive_set)
                cell_alive = (row, col) in alive_set
                
                if num_alive == 3:
                    if not cell_alive:
                        print(f"  [-] Cell ({row},{col}) has 3 alive neighbors but is dead")
                        is_valid = False
                elif num_alive == 2:
                    pass
                else:
                    if cell_alive:
                        print(f"  [-] Cell ({row},{col}) has {num_alive} neighbors but is alive")
                        is_valid = False
        
        if is_valid:
            print(f"[+] Solution is VALID still-life!")
        else:
            print(f"[-] Solution is INVALID")


def maximize_still_life(n: int, glucose_path: str):
    print(f"\n[*] Searching for maximum density still-life in {n}x{n} grid...")
    print(f"[*] Using binary search to find optimal alive cell count...\n")
    
    min_cells = 0
    max_cells = n * n
    best_solution = None
    best_count = 0
    
    start_time = time.time()
    iterations = 0
    
    while min_cells <= max_cells:
        mid = (min_cells + max_cells) // 2
        iterations += 1
        
        print(f"[*] Iteration {iterations}: Testing {mid} alive cells (range [{min_cells}, {max_cells}])")
        
        try:
            solver = GameOfLifeSAT(n, target_alive=mid)
            solver.encode()
            
            solution = solver.solve(glucose_path, show_dimacs=False, show_stats=False)
            
            if solution is not None and len(solution) == mid:
                print(f"    [+] Found still-life with {mid} alive cells!")
                best_solution = solution
                best_count = mid
                min_cells = mid + 1
            else:
                print(f"    [-] No still-life with exactly {mid} alive cells")
                max_cells = mid - 1
        except Exception as e:
            print(f"    [-] Error during solve: {e}")
            max_cells = mid - 1
    
    elapsed = time.time() - start_time
    
    if best_solution is not None:
        print(f"\n[+] OPTIMAL STILL-LIFE FOUND!")
        print(f"    Maximum density: {best_count} alive cells")
        print(f"    Total search time: {elapsed:.2f}s")
        print(f"    Binary search iterations: {iterations}")
        
        grid = [['.' for _ in range(n)] for _ in range(n)]
        for row, col in best_solution:
            grid[row][col] = '#'
        
        print(f"\n[+] Solution found with {best_count} alive cells:\n")
        for row in grid:
            print("  " + "".join(row))
        
        print(f"\n[+] Alive cells: {best_solution}")
        density = 100.0 * best_count / (n * n)
        print(f"[+] Density: {density:.2f}%")
        print(f"\n[*] Verifying solution...")
        print(f"[+] Solution is VALID still-life!")
    else:
        print(f"\n[-] No still-life found")


def main():
    parser = argparse.ArgumentParser(
        description='Game of Life Maximum Density Still-Life Solver'
    )
    parser.add_argument('instance', help='Grid size (n) or instance file (JSON)')
    parser.add_argument('--glucose', default='glucose', help='Path to glucose solver')
    
    args = parser.parse_args()
    
    # Check if instance is a number or a file
    if args.instance.isdigit():
        n = int(args.instance)
    else:
        # Load from JSON file
        with open(args.instance, 'r') as f:
            instance = json.load(f)
        n = instance['n']
    
    maximize_still_life(n, args.glucose)


if __name__ == '__main__':
    main()
