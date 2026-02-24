#!/usr/bin/env python3

import numpy as np
from pathlib import Path

# -------------------------------------------------
# Core function (Notebook + CLI)
# -------------------------------------------------
def generate_and_write(
    rows_a,
    cols_a,
    cols_b,
    seed=None
):
    """
    Generates GEMM data and writes:
      - ../data/data_{rows_a}x{cols_a}x{cols_b}.h   (C header, int32_t, 1D arrays)
      - ../data/data_{rows_a}x{cols_a}x{cols_b}.npz (NumPy, 1D arrays)
      - ../data/data.npz                            (NumPy, 1D arrays)

    Matrices are stored row-major:
      A[i*COLS_A + j]
      B[i*COLS_B + j]
      C[i*COLS_B + j]
      D[i*COLS_B + j]

    D = A * B + C
    """

    if seed is not None:
        np.random.seed(seed)

    rows_a = int(rows_a)
    cols_a = int(cols_a)
    cols_b = int(cols_b)

    # -------------------------------------------------
    # Ensure output directory exists
    # -------------------------------------------------
    data_dir = Path("../data")
    data_dir.mkdir(parents=True, exist_ok=True)

    size_tag = f"{rows_a}x{cols_a}x{cols_b}"

    h_filename = data_dir / f"data_{size_tag}.h"
    npz_filename  = data_dir / f"data_{size_tag}.npz"
    latest_npz    = data_dir / "data.npz"

    # -------------------------
    # Generate matrices (2D)
    # -------------------------
    A_2d = np.random.randint(-10, 11, size=(rows_a, cols_a), dtype=np.int32)
    B_2d = np.random.randint(-10, 11, size=(cols_a, cols_b), dtype=np.int32)
    C_2d = np.random.randint(-10, 11, size=(rows_a, cols_b), dtype=np.int32)

    # GEMM
    D_2d = ((A_2d @ B_2d) + C_2d).astype(np.int32)

    # -------------------------
    # Flatten (row-major)
    # -------------------------
    A = A_2d.flatten()
    B = B_2d.flatten()
    C = C_2d.flatten()
    D = D_2d.flatten()

    # =================================================
    # Write C header (.h)
    # =================================================
    def write_array_c(f, name, arr):
        f.write(f"int32_t {name}[{len(arr)}] = {{\n    ")
        f.write(", ".join(str(int(v)) for v in arr))
        f.write("\n};\n\n")

    with open(h_filename, "w") as f:
        f.write("#ifndef DATA_H\n")
        f.write("#define DATA_H\n\n")
        f.write("#include <stdint.h>\n\n")

        f.write(f"#define ROWS_A {rows_a}\n")
        f.write(f"#define COLS_A {cols_a}\n")
        f.write(f"#define COLS_B {cols_b}\n\n")

        f.write(f"#define SIZE_A (ROWS_A * COLS_A)\n")
        f.write(f"#define SIZE_B (COLS_A * COLS_B)\n")
        f.write(f"#define SIZE_C (ROWS_A * COLS_B)\n\n")

        write_array_c(f, "A", A)
        write_array_c(f, "B", B)
        write_array_c(f, "C", C)
        write_array_c(f, "D", D)

        f.write("#endif // DATA_H\n")

    # =================================================
    # Write NumPy file (.npz)
    # =================================================
    np.savez(
        npz_filename,
        A=A,
        B=B,
        C=C,
        D=D,
        ROWS_A=rows_a,
        COLS_A=cols_a,
        COLS_B=cols_b
    )

    # =================================================
    # Write NumPy file (.npz) — latest alias
    # =================================================
    np.savez(
        latest_npz,
        A=A,
        B=B,
        C=C,
        D=D,
        ROWS_A=rows_a,
        COLS_A=cols_a,
        COLS_B=cols_b
    )

    print(f"Generated:")
    print(f"  {h_filename}")
    print(f"  {npz_filename}")
    print(f"  {latest_npz}")

    return A, B, C, D


# -------------------------------------------------
# Optional CLI
# -------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate MMUL data (1D arrays)")

    parser.add_argument("--rows_a", type=int, required=True)
    parser.add_argument("--cols_a", type=int, required=True)
    parser.add_argument("--cols_b", type=int, required=True)
    parser.add_argument("--seed", type=int, default=3)

    args = parser.parse_args()

    generate_and_write(
        rows_a=args.rows_a,
        cols_a=args.cols_a,
        cols_b=args.cols_b,
        seed=args.seed
    )


if __name__ == "__main__":
    main()
