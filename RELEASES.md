# Releases

## 1.0.0
*July 2024*

This release contains the first version of idr_bench. This version only supports Slurm because Slurm is great! You can submit your template enriched by many arguments, which are swept through in grid search manner, following CLI arguments.
Constraints can be used to tie up multiple arguments, and reduce the research space.

You may have noticed, that Hydra does cover the purpose of this package. However this one is designed to be a very lightweight version, as Hydra can be quite invasive and overcomplicated.
