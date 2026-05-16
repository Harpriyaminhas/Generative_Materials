import os
import glob
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter

# Input and output directories
input_dir = "./generated_processed_cif"
output_dir = "./cleaned_cifs"
os.makedirs(output_dir, exist_ok=True)

# Placeholder lattice (cubic, 6.0 Å)
lattice = Lattice.cubic(6.0)

# Find all CIF files matching sample_*.cif
cif_files = glob.glob(os.path.join(input_dir, "sample_*.cif"))

def parse_atoms_from_cif(filepath):
    elements = []
    coords = []
    inside_atom_loop = False

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # Check if we're inside the atom site loop
            if line.startswith("loop_"):
                inside_atom_loop = False  # Reset
            elif "_atom_site_type_symbol" in line:
                inside_atom_loop = True
                continue
            elif inside_atom_loop and line:
                tokens = line.split()
                if len(tokens) >= 6:
                    try:
                        element = tokens[0]
                        x, y, z = float(tokens[3]), float(tokens[4]), float(tokens[5])
                        elements.append(element)
                        coords.append([x, y, z])
                    except ValueError:
                        continue
    return elements, coords

# Process all matched CIF files
for file_path in cif_files:
    filename = os.path.basename(file_path)
    try:
        elements, coords = parse_atoms_from_cif(file_path)

        if not elements or not coords:
            print(f"[!] Skipping {filename} — no valid atoms found.")
            continue

        structure = Structure(lattice, elements, coords)
        cleaned_path = os.path.join(output_dir, filename)
        CifWriter(structure).write_file(cleaned_path)
        print(f"[✓] Converted {filename} → cleaned_cifs/")
    except Exception as e:
        print(f"[✗] Error processing {filename}: {e}")
