import sys
from pathlib import Path

def parse_input_file(filename):
    """Return (grid:list[str], target_cols:list[int], target_rows:list[int], n:int)."""
    with open(filename, "r") as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]
    target_cols = list(map(int, lines[-2].split()))
    target_rows = list(map(int, lines[-1].split()))
    grid = lines[:-2]
    n = len(grid)
    return grid, target_cols, target_rows, n

def find_thermometers(grid, n):
    thermometers = {}
    thermometer_id = 1
    visited = [[False]*n for _ in range(n)]

    def in_bounds(r,c): return 0<=r<n and 0<=c<n

    def trace(r,c,dr,dc):
        cells = [(r,c)]
        rr, cc = r+dr, c+dc
        while in_bounds(rr,cc):
            ch = grid[rr][cc]
            if (dr,dc) in [(1,0),(-1,0)] and ch in ['^','v']:
                cells.append((rr,cc))
            elif (dr,dc) in [(0,1),(0,-1)] and ch in ['>','<']:
                cells.append((rr,cc))
            else:
                break
            rr += dr
            cc += dc
        return cells

    for r in range(n):
        for c in range(n):
            if visited[r][c]:
                continue
            ch = grid[r][c]
            if ch in "UDRL":
                dr, dc = {"U":(-1,0),"D":(1,0),"R":(0,1),"L":(0,-1)}[ch]
                cells = trace(r,c,dr,dc)
                tname = f"t{thermometer_id}"
                thermometer_id += 1
                thermometers[tname] = cells
                for rr,cc in cells:
                    visited[rr][cc] = True
    return thermometers

def write_facts(outfile, n, thermometers, target_cols, target_rows):
    """Write 0-based LP file compatible with decode.py"""
    with open(outfile, "w") as f:
        f.write(f"dim({n}).\n")
        f.write(f"rows(0..{n-1}).\n")
        f.write(f"col(0..{n-1}).\n")
        f.write(f"index(0..{n}).\n\n")

        tnames = ";".join(thermometers.keys())
        f.write(f"thermometer({tnames}).\n\n")

        for t,cells in thermometers.items():
            f.write(f"len({t},{len(cells)}).\n")
        f.write("\n")

        for t,cells in thermometers.items():
            for i,(r,c) in enumerate(cells, start=1):
                f.write(f"pos({t},{i},{r},{c}).\n")  # 0-based

        f.write("\n")
        for r,val in enumerate(target_rows):
            f.write(f"target_row({r},{val}).\n")
        f.write("\n")
        for c,val in enumerate(target_cols):
            f.write(f"target_col({c},{val}).\n")
        # ensure uniqueness model
        f.write("#minimize { (R*100 + C) : fill(R,C) }.\n\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 encode.py domXX.txt domainXX.lp")
        sys.exit(1) # Exit with an error code

    txt_file = sys.argv[1]
    out_file = sys.argv[2]

    grid, target_cols, target_rows, n = parse_input_file(txt_file)
    thermometers = find_thermometers(grid, n)
    write_facts(out_file, n, thermometers, target_cols, target_rows)
    print(f"Encoded {txt_file} --->> {out_file}")

if __name__ == "__main__":
    main()