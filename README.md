# Threat Detection in IIoT Networks

## To-do
**Run experiments**: the results became outdated after some minor modifications and were removed. They can be found in previous commits in the `main` branch history (see commit `f0ef100`).

## How to Run the Codebase

If the `datasense/dataset` path is empty, you must download the correct archive from the source detailed [here](/datasense/README.md). The scripts in `scripts/` (which will be run next) expect the archive corresponding to the **1-second time window**. The files must retain their original names.

After downloading the correct archive, run all the scripts in the `scripts/` folder in order.

> **PS:** I know... this is kind of manually dumb. The whole codebase isn't automated the way it should have been from the start. One day I might fix it but currently I don't have any plans to revisit this project other than making some minor fixes I'm working on right now (at the time of the commit containing this text). If you like, you can submit a PR with fixes and automation improvements. The automation should preferably include removing the experiments from the notebooks, which are kind of annoying, but were the fastest and most straightforward way of doing it given my knowledge at the time. Thanks!

After populating the `datasense/dataset/` folder, run the experiments (notebooks) in the `experiments/` folder and see the results in the generated folders (`experiments/results/` and `experiments/shap/`) and through the [evaluations notebook](/experiments/evaluations.ipynb).
