# evolution-lifespan

Code for a project on **phylogenetics-based methodologies to study lifespan in animals**.

The pipeline combines life-history traits from [AnAge](https://genomics.senescence.info/species/) (the Animal Ageing and Longevity Database) with comparative-genomics data from the [Zoonomia](https://zoonomiaproject.org/) 240-mammal alignment to investigate the evolution of maximum lifespan (`t_max`), developmental time (`t_dev`) and adult body mass.

## Layout

```
.
├── Dockerfile              # Python 3.11 + scientific stack
├── requirements.txt
├── data_preparation.py     # entry point: download + parse + merge
└── data/
    ├── raw/                # gitignored — downloaded sources
    └── processed/          # gitignored — merged tables
```

## Quickstart

```bash
docker build -t evolution-lifespan .
docker run --rm -it -v "$PWD":/workspace evolution-lifespan \
    python data_preparation.py
```

The script writes `data/processed/lifespan_traits.tsv` with one row per Zoonomia species matched to AnAge.

## Zoonomia / TOGA data download

- **Cactus HAL alignment:** `447-mammalian-2022v1.hal`  
  https://cgl.gi.ucsc.edu/data/cactus/447-mammalian-2022v1.hal

- **Cactus tree:** `447-mammalian-2022v1.nh`  
  https://cgl.gi.ucsc.edu/data/cactus/

- **TOGA human hg38 reference:** `human_hg38_reference`  
  https://genome.senckenberg.de/download/TOGA/human_hg38_reference/

- **TOGA codon alignments:** `human_hg38_reference/MultipleCodonAlignments/`  
  https://genome.senckenberg.de/download/TOGA/human_hg38_reference/MultipleCodonAlignments/
