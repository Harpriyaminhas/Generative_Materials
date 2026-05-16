import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# 1. Read Excel file
# ============================================================

excel_file = "/home/psi/Harpriya/ML/generate/CrystaLLM/prject_2300_data/generated_processed_poscars/AGAIN/relax_str/structure_uniqueness_novelty_duplicates.xlsx"

df = pd.read_excel(excel_file)

# ============================================================
# 2. Extract generated structure index
# ============================================================

df["Generated_Index"] = (
    df["File"]
    .astype(str)
    .apply(lambda x: int(os.path.basename(x).split("_")[-1]))
)

# Sort according to generation order
df = df.sort_values("Generated_Index").reset_index(drop=True)

# Ensure boolean format
df["Unique"] = df["Unique"].astype(bool)

# ============================================================
# 3. Compute cumulative unique structures
# ============================================================

batch_size = 1000
max_structures = 10000

batches = np.arange(batch_size, max_structures + batch_size, batch_size)

unique_counts = []

for end in batches:

    sub = df[df["Generated_Index"] <= end]

    n_unique = sub["Unique"].sum()

    unique_counts.append(n_unique)

# ============================================================
# 4. Plot settings
# ============================================================

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 18,
    "axes.linewidth": 2.2
})

# Figure size: 15 × 9
fig, ax = plt.subplots(figsize=(15, 9))

x = np.arange(1, len(batches) + 1)

# ============================================================
# 5. Colors
# ============================================================

bar_color = "#4F81BD"   # publication-quality academic blue

# ============================================================
# 6. Bar plot
# ============================================================

bar_width = 0.65

bars = ax.bar(
    x,
    unique_counts,
    width=bar_width,
    color=bar_color,
    edgecolor="black",
    linewidth=1.5
)

# ============================================================
# 7. Axis formatting
# ============================================================

ax.set_ylabel(
    "# of unique structures",
    fontsize=24,
    fontweight="bold"
)

ax.set_xlabel(
    "# of generated structures (×1000)",
    fontsize=24,
    fontweight="bold"
)

ax.set_xticks(x)
ax.set_xticklabels([str(i) for i in range(1, 11)])

ax.set_ylim(0, 9000)

ax.tick_params(
    axis="both",
    labelsize=20,
    width=2,
    length=8
)

# ============================================================
# 8. Grid
# ============================================================

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

# ============================================================
# 9. Final formatting
# ============================================================

plt.tight_layout()

plt.savefig(
    "unique_structure_statistics.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
