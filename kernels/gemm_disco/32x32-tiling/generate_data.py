#!/usr/bin/env python3

import numpy as np

# -------------------------------------------------
# Core function (Notebook + CLI)
# -------------------------------------------------
def generate_and_write(
    rows_a,
    cols_a,
    cols_b,
    alpha,
    beta,
    seed=None,
    basename="data"
):
    """
    Generates GEMM data and writes:
      - basename.h   (C header, int32_t, 1D arrays)
      - basename.npz (NumPy, 1D arrays)

    Matrices are stored row-major:
      A[i*COLS_A + j]
      B[i*COLS_B + j]
      C[i*COLS_B + j]
      D[i*COLS_B + j]

    D = alpha * A * B + beta * C
    """

    if seed is not None:
        np.random.seed(seed)

    rows_a = int(rows_a)
    cols_a = int(cols_a)
    cols_b = int(cols_b)
    alpha  = np.int32(alpha)
    beta   = np.int32(beta)

    # -------------------------
    # Generate matrices (2D)
    # -------------------------
    A_2d = np.random.randint(-10, 11, size=(rows_a, cols_a), dtype=np.int32)
    B_2d = np.random.randint(-10, 11, size=(cols_a, cols_b), dtype=np.int32)
    C_2d = np.random.randint(-10, 11, size=(rows_a, cols_b), dtype=np.int32)

    # GEMM
    D_2d = (alpha * (A_2d @ B_2d) + beta * C_2d).astype(np.int32)

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

    h_filename = f"{basename}.h"
    with open(h_filename, "w") as f:
        f.write("#ifndef DATA_H\n")
        f.write("#define DATA_H\n\n")
        f.write("#include <stdint.h>\n\n")

        f.write(f"#define ROWS_A {rows_a}\n")
        f.write(f"#define COLS_A {cols_a}\n")
        f.write(f"#define COLS_B {cols_b}\n\n")

        f.write(f"#define ALPHA {alpha}\n")
        f.write(f"#define BETA {beta}\n\n")

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
    npz_filename = f"{basename}.npz"
    np.savez(
        npz_filename,
        A=A,
        B=B,
        C=C,
        D=D,
        ROWS_A=rows_a,
        COLS_A=cols_a,
        COLS_B=cols_b,
        ALPHA=alpha,
        BETA=beta
    )

    return A, B, C, D


# -------------------------------------------------
# Optional CLI
# -------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate GEMM data (1D arrays)")

    parser.add_argument("--rows_a", type=int, required=True)
    parser.add_argument("--cols_a", type=int, required=True)
    parser.add_argument("--cols_b", type=int, required=True)
    parser.add_argument("--alpha", type=int, required=True)
    parser.add_argument("--beta", type=int, required=True)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--basename", type=str, default="data")

    args = parser.parse_args()

    generate_and_write(
        rows_a=args.rows_a,
        cols_a=args.cols_a,
        cols_b=args.cols_b,
        alpha=args.alpha,
        beta=args.beta,
        seed=args.seed,
        basename=args.basename
    )

    print(f"Generated {args.basename}.h and {args.basename}.npz")


if __name__ == "__main__":
    main()
