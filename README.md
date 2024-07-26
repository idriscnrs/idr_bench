# idr_bench

## Launch Benchmark

To launch a benchmark, do this

```bash
idr_bench <benchmark_launcher_cli> <benchmark_parameters>
```

Benchmark launcher CLI include:
* a config file (`-c` or `--config`). Optional.
* the slurm job template (`--template`). Required.
* the output directory (`--out-dir`). Defaults to `out_log/`.
* contraints (`--constraint` or `--constraints`). Defaults to no contraint.

Benchmark parameters can be anything. They just need to be given with two dashes, the name, and an optional value. The value can cover multiple possibilities which are separated by a comma. If the value are integers, then using an hyphen as a separator will allow to sweep through every integers between the two provided (including bounds). If no value is provided, then it is assumed that we want to sweep through `True` and `False`.

Example:
```bash
idr_bench --fsdp --batch_size 64,128 --ngpus 1,2,4
```

You can provide constraints to reduce the space of possibilities:

Example:
```bash
idr_bench --constraint "encoder_attention == decoder_attention" --encoder_attention base,flash --decoder_attention base,flash
```

## Get result from logfile
Save the results and informations of benchmark runs in a csv. If the csv exists, it will update it.
`python benchmark/result.py --logdir_path ./benchmark/out_log --csv_path ./bench_result.csv`
