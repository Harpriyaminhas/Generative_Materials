import os
import re
import numpy as np
import pandas as pd
from pymatgen.core import Structure
from atomate2.forcefields.flows.phonons import PhononMaker
from pymatgen.phonon.bandstructure import PhononBandStructureSymmLine
from pymatgen.phonon.dos import PhononDos
from pymatgen.phonon.plotter import PhononBSPlotter, PhononDosPlotter
from jobflow import run_locally, SETTINGS

# Define root paths
jobs_root_dir = "./Jobs"
results_root_dir = "./Results"
os.makedirs(jobs_root_dir, exist_ok=True)
os.makedirs(results_root_dir, exist_ok=True)

# Find all POSCAR_relax1_* files with proper number
all_files = os.listdir(".")
poscar_files = sorted(
    [f for f in all_files if re.fullmatch(r'POSCAR_relax1_\d+', f)]
)

# To store stability status
stability_data = []

# Loop through all POSCAR files
for poscar_file in poscar_files:
    try:
        # Read structure
        structure = Structure.from_file(poscar_file)
        formula = structure.composition.reduced_formula

        # Job & results subdirectory
        material_id = poscar_file  # use filename as id
        material_jobs_dir = os.path.join(jobs_root_dir, material_id)
        os.makedirs(material_jobs_dir, exist_ok=True)
        os.chdir(material_jobs_dir)

        # Run phonon maker
        phonon_flow = PhononMaker(min_length=15.0, store_force_constants=True).make(structure=structure)
        run_locally(phonon_flow, create_folders=True, store=SETTINGS.JOB_STORE)

        # Retrieve results
        store = SETTINGS.JOB_STORE
        store.connect()
        result = store.query_one(
            {"name": "generate_frequencies_eigenvectors"},
            properties=["output.phonon_dos", "output.phonon_bandstructure", "output.force_constants"],
            load=True,
            sort={"completed_at": -1}
        )

        if result:
            # Parse outputs
            ph_bs = PhononBandStructureSymmLine.from_dict(result['output']['phonon_bandstructure'])
            ph_dos = PhononDos.from_dict(result['output']['phonon_dos'])
            force_constants = result['output']['force_constants']

            bs_plot = PhononBSPlotter(bs=ph_bs)
            dos_plot = PhononDosPlotter()
            dos_plot.add_dos("Phonon DOS", ph_dos)

            material_results_dir = os.path.join(results_root_dir, f"{material_id}_{formula}")
            os.makedirs(material_results_dir, exist_ok=True)

            # Save plots
            bs_plot.get_plot().figure.savefig(os.path.join(material_results_dir, f"{material_id}_BandStructure.png"), dpi=300)
            dos_plot.get_plot().figure.savefig(os.path.join(material_results_dir, f"{material_id}_DOS.png"), dpi=300)

            # Save BandStructure data
            band_structure_dat_path = os.path.join(material_results_dir, f"{material_id}_BandStructure.dat")
            with open(band_structure_dat_path, 'w') as f:
                f.write("# Path (q-point distance)  Frequency\n")
                distances = ph_bs.distance
                for band in ph_bs.bands:
                    for q_idx, frequency in enumerate(band):
                        f.write(f"{distances[q_idx]:20.8f} {frequency:20.8f}\n")

            # Save force constants
            fc_path = os.path.join(material_results_dir, f"{material_id}_ForceConstants.txt")
            with open(fc_path, 'w') as f:
                f.write(f"# Force Constants for {material_id}\n{'='*50}\n")
                if isinstance(force_constants, dict):
                    for key, value in force_constants.items():
                        if isinstance(key, tuple) and len(key) == 2:
                            f.write(f"\n# Atom pair: {key[0]} {key[1]}\n")
                            for row in value:
                                f.write("    " + "    ".join(f"{float(val):20.12f}" for val in row) + "\n")
                        else:
                            f.write(f"\n# Unrecognized key format: {key}\n{value}\n")
                elif isinstance(force_constants, np.ndarray):
                    n_atoms = force_constants.shape[0]
                    for i in range(n_atoms):
                        for j in range(n_atoms):
                            f.write(f"\n# Atom pair: {i+1} {j+1}\n")
                            for x in range(3):
                                f.write("    " + "    ".join(f"{force_constants[i,j,x,y]:20.12f}" for y in range(3)) + "\n")
                else:
                    f.write("\nUnsupported force_constants format.\n")
                    f.write(str(force_constants))

            # Append success
            stability_data.append({"POSCAR": poscar_file, "Formula": formula, "Status": "Stable ✅"})
            print(f"✅ Processed {poscar_file}")

        else:
            raise ValueError("No result found in job store.")

    except Exception as e:
        # Append failure
        stability_data.append({"POSCAR": poscar_file, "Formula": "-", "Status": f"Unstable ❌: {e}"})
        print(f"❌ Error processing {poscar_file}: {e}")

    finally:
        os.chdir("..")  # return to parent dir to keep loop working

# Save stability summary
summary_df = pd.DataFrame(stability_data)
summary_df.to_excel("stability_summary.xlsx", index=False)
print("📄 Summary saved to: stability_summary.xlsx")
