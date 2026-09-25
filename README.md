# TL_generative_design

**Cross-Property Transfer Learning and Generative Crystal Design for Accelerated Discovery of Low-Thermal-Conductivity Materials**

Harpriya Minhas, Rahul Kumar Sharma, Biswarup Pathak<br>
*ACS Applied Materials & Interfaces* **2026**, 18 (37), 50758–50771<br>
DOI: [10.1021/acsami.6c10770](https://doi.org/10.1021/acsami.6c10770)

This repository contains the data, trained-model predictions, and generative-design workflow for the paper above.

---

## Overview

Low lattice thermal conductivity (κ<sub>L</sub>) is a key target for thermoelectrics and thermal barrier materials, but labelled κ<sub>L</sub> data are scarce. We address this with a unified framework that combines:

1. **Graph neural networks (GNNs)** — CGCNN, DeeperGATGNN, and ALIGNN benchmarked on 3,925 materials. ALIGNN performs best, as its line-graph (bond-angle) representation captures local bonding and many-body interactions that govern phonon transport.
2. **Cross-property transfer learning (TL)** — models pretrained on six auxiliary properties are fine-tuned for κ<sub>L</sub>. Energy-based source tasks (e.g. formation energy, energy above hull) give the most transferable latent representations for κ<sub>L</sub> prediction.
3. **Transformer-based generative crystal modelling** — CrystaLLM generates 10,000 unique candidate crystal structures, which are screened with the TL models for κ<sub>L</sub> and thermodynamic stability, followed by phonon calculations for dynamical stability.

The pipeline identifies **17 dynamically stable compounds with κ<sub>L</sub> ≤ 0.50 W m⁻¹ K⁻¹**.

```
Curated κL dataset ──► GNN benchmark (CGCNN / DeeperGATGNN / ALIGNN)
                                   │
Auxiliary properties ──► pretrain ─┴─► fine-tune on κL (cross-property TL)
                                                   │
CrystaLLM ──► 10,000 generated structures ──► predict κL, E_f, E_hull
                                                   │
                                   phonon stability screening
                                                   │
                           17 stable candidates, κL ≤ 0.50 W m⁻¹ K⁻¹
```

---

## Repository structure

```
TL_generative_design/
├── Input_data/
│   ├── 3929 selected materials.xlsx   # curated κL training set
│   ├── id_prop_new.xlsx               # id–property table for GNN training
│   └── crystal_llm_input.xlsx         # inputs/prompts for CrystaLLM generation
├── Crystallm/
│   ├── cifs_v1_{train,val,test}.pkl.gz      # CIF datasets for CrystaLLM
│   ├── tokens_v1_*.pkl.gz / .tar.gz         # tokenised CIF corpora
│   ├── custom_cifs.*, prompts.tar.gz, gen_prompts.tar.gz
│   ├── gen_v1_small_raw.tar.gz              # raw generated output
│   ├── generated_cifs.*, generated_processed_cifs.tar.gz
│   ├── clean_raw.py                         # parse generated CIFs → cleaned CIFs (pymatgen)
│   ├── 3novel_unique_05_26.py               # cumulative unique-structure statistics plot
│   ├── unique_structure_statistics.png
│   ├── violin_deviation_plots_final.png
│   └── Generated_poscars/
│       ├── POSCAR_relax1_*                  # relaxed generated structures
│       └── 2IFC.py                          # phonon workflow + stability summary (atomate2/jobflow)
├── Results/
│   ├── kappa_pred.xlsx                # predicted κL for generated structures
│   ├── FE_pred.xlsx                   # predicted formation energies
│   └── ehull_pred.xlsx                # predicted energy above hull
└── requirements.txt
```

---

## Installation

```bash
git clone https://github.com/Harpriyaminhas/TL_generative_design.git
cd TL_generative_design
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

The GNN models and CrystaLLM are external codes; install them from their own repositories:

- ALIGNN — https://github.com/usnistgov/alignn
- CGCNN — https://github.com/txie-93/cgcnn
- DeeperGATGNN — https://github.com/usccolumbia/deeperGATGNN
- CrystaLLM — https://github.com/lantunes/CrystaLLM

The phonon script (`2IFC.py`) additionally requires `atomate2` and `jobflow`.

---

## Usage

**1. Clean generated structures**

```bash
cd Crystallm
python clean_raw.py      # reads ./generated_processed_cif/sample_*.cif → ./cleaned_cifs/
```

**2. Unique-structure statistics**

```bash
python 3novel_unique_05_26.py   # edit the input Excel path in the script first
```

**3. Phonon stability screening**

```bash
cd Generated_poscars
python 2IFC.py   # runs phonons for POSCAR_relax1_*, writes Results/ and stability_summary.xlsx
```

Paths in the scripts are hardcoded; adjust them to your local layout.

---

## Citation

If you use this code or data, please cite:

```bibtex
@article{Minhas2026,
  author  = {Minhas, Harpriya and Sharma, Rahul Kumar and Pathak, Biswarup},
  title   = {Cross-Property Transfer Learning and Generative Crystal Design for
             Accelerated Discovery of Low-Thermal-Conductivity Materials},
  journal = {ACS Appl. Mater. Interfaces},
  year    = {2026},
  volume  = {18},
  number  = {37},
  pages   = {50758--50771},
  doi     = {10.1021/acsami.6c10770}
}
```

Please also cite the underlying models (ALIGNN, CGCNN, DeeperGATGNN, CrystaLLM) as appropriate.

---

## Contact

Harpriya Minhas — [GitHub](https://github.com/Harpriyaminhas) · [Google Scholar](https://scholar.google.com/citations?user=nlvWVQUAAAAJ&hl=en)
