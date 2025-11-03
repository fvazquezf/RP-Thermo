# Lab Assignment #1
## Thermometers puzzle

- Francisco Manuel Vazquez Fernandez ([franciscomanuel.vazquez.fernandez@rai.usc.es])
- Gian Paolo Bulleddu ([gianpaolo.bulleddu@rai.usc.es])

# Thermometer Puzzle Solver

This project contains a set of Python and Clingo scripts to solve the "Thermometers" logic puzzle. The solution is based on the assignment from the University of A Coruña's RP (Declarative Reasoning) course.

The puzzle consists of a grid containing empty thermometers. The goal is to "fill" each thermometer with mercury, starting from its bulb, such that the total number of filled cells in each row and column matches the target numbers specified for that row/column.

The workflow is divided into three main parts:

1.  **Encoding:** A Python script (`encode.py`) reads a text-based puzzle domain and converts it into a set of logic programming facts.
2.  **Solving:** A static Clingo file (`thermo.lp`) defines the universal rules of the puzzle. An ASP solver (like Clingo) uses these rules along with the generated facts to find a solution.
3.  **Generation:** A helper script (`generate.py`) automates the entire process from encoding to solving and visualization.

## File Explanations

Here is a detailed explanation of the three key files as requested.

### `encode.py` (The Domain Encoder)

This script is the first step in the solving pipeline. Its sole purpose is to parse a human-readable ASCII art puzzle file and translate it into a machine-readable logic program.

**How it works:**

1.  **Parsing (`parse_input_file`):** It reads the input `.txt` file, separating the grid layout from the last two lines, which it parses as the target counts for columns and rows.
2.  **Tracing Thermometers (`find_thermometers`, `trace`):** It iterates through every cell of the grid. When it finds a thermometer "bulb" (represented by `U`, `D`, `L`, or `R`), it follows the thermometer's path (cells marked with `^`, `v`, `<`, `>`) until it ends. It records all cells belonging to this single thermometer in order, starting from the bulb.
3.  **Writing Facts (`write_facts`):** Once all thermometers are identified, it writes the following facts to the output `.lp` file:
      * `dim(n).`: The size of the n x n grid.
      * `thermometer(t1;...;tn).`: A list of all unique thermometer IDs it found.
      * `len(t, l).`: The total length (number of cells) `l` for each thermometer `t`.
      * `pos(t, i, r, c).`: States that the `i`-th cell of thermometer `t` is at grid position `(r, c)`. The index `i` is 1-based, starting from the bulb.
      * `target_row(r, n).`: The target number `n` of filled cells for row `r`.
      * `target_col(c, n).`: The target number `n` of filled cells for column `c`.

-----

### `thermo.lp` (The Static Solver)

This is the core logic program for the Thermometer puzzle. It defines the general rules and constraints of *any* thermometer puzzle, independent of a specific instance.

**How it works:**

1.  **Choice Rule:**

    ```prolog
    1 { fill_len(T,I) : allowed_length(T,I) } 1 :- thermometer(T).
    ```

    This is the "engine" of the solver. For every `thermometer(T)`, it *must* choose exactly one (`1 { ... } 1`) fill length `I`. The possible lengths `I` range from 0 (empty) to the thermometer's maximum length `L`.

2.  **Fill Logic:**

    ```prolog
    fill(R,C) :- pos(T,I,R,C), fill_len(T,K), I <= K.
    ```

    This rule defines what it means for a cell `(R,C)` to be filled. A cell is filled if it belongs to thermometer `T` at position `I`, and the chosen fill length `K` for that thermometer is greater than or equal to the cell's position `I`. This ensures mercury fills contiguously from the bulb.

3.  **Constraints:**

    ```prolog
    :- rows(R), target_row(R,N), not N = #count { C : fill(R,C) }.
    :- col(C), target_col(C,N), not N = #count { R : fill(R,C) }.
    ```

    These are integrity constraints that enforce the puzzle's main rules.

      * The first line states: "A solution is invalid (`:-`) if for any row `R` with target `N`, the computed count of filled cells in that row (`#count { ... }`) is *not* equal to `N`."
      * The second line applies the exact same logic for every column `C`.

-----

### `generate.py` (The Workflow Manager)

This script fully automates the assignment's workflow. It calls the other scripts in the correct sequence.

**How it works:**

It requires a single command-line argument: the number of the domain to solve (e.g., `05`).

1.  **Step 1: Encode**
    It calls `encode.py` to process the specified domain file.

      * `python3 encode.py examplesthermo/dom05.txt domain05.lp`

2.  **Step 2: Decode (Solve)**
    It calls `decode.py`, which in turn runs the Clingo solver using both the static rules and the newly generated facts.

      * `python3 decode.py thermo.lp domain05.lp`

3.  **Step 3: Draw**
    Finally, it calls the visualization script `drawThermo.py`, feeding it the original domain file (for the layout) and the new result file (for the fill data).

      * `python3 drawThermo.py examplesthermo/dom05.txt result05.txt`

## How to Run

To run the full workflow for a specific puzzle (e.g., `./examplesthermo/dom01.txt`):
Open a terminal on your working directory and hit the command :
```bash
python3 generate.py 01
```

This will:
1.  Create `./doma01.lp` (facts).
2.  Create `./result01.txt` (solution grid).
3.  Primpt the text:
```bash
Running workflow for number: 05
--------------------
STEP: Encoding
Executing: python3 encode.py examplesthermo/dom05.txt domain05.lp
--------------------
Encoded examplesthermo/dom05.txt --->> domain05.lp
--------------------
STEP: Decoding
Executing: python3 decode.py thermo.lp domain05.lp (output will be printed and saved)
--------------------
xxxx...xx.xxx..
.xx..x.xx...xxx
.xxxxxxx....x..
.xx..x..x...xx.
.xx..x.xx...xxx
.xxxxx..xxx.xxx
.xxxx.....xxx.x
.xxxxxxxxx.xx.x
.x.............
.x..........xx.
.x.....xxxxxx..
..xxxxxxxx..xxx
.xx..x......x.x
..xx.x.x....x.x
..x..x.xxxxxxx.
--------------------
STEP: Drawing
Executing: python3 drawThermo.py examplesthermo/dom05.txt result05.txt
--------------------
pygame 2.6.1 (SDL 2.28.4, Python 3.12.3)
Hello from the pygame community. https://www.pygame.org/contribute.html
```
4.  Open a Pygame window displaying the graphical solution.

![Solution05](./Solution05.png)



## How to generate a single domXX.lp file
Open a terminal on your working directory and hit the command :
```bash
$> python3 encode.py .\examplesthermo\dom01.txt dom01.lp
```
This will:
1.  Create `./doma01.lp` (facts).
2. Prompt the following text:
```bash
Encoded .\examplesthermo\dom01.txt --->> dom01.lp
```
