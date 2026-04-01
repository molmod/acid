// SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
// SPDX-License-Identifier: CC-BY-SA-4.0

#set page("a4", margin: 2cm, numbering: "1 / 1")
#show link: set text(blue)
#show table.cell.where(y: 0): set text(weight: "bold")
#let frame(stroke) = (x, y) => (
  top: if y < 2 { stroke } else { 0pt },
  bottom: stroke,
)
#set table(
  stroke: frame(rgb("222222")),
)
#set figure(placement: auto)
#show figure: set place(clearance: 2em)
#show figure.caption: it => [
    *#it.supplement #context(it.counter.display(it.numbering))#it.separator*#it.body
]

#align(center)[
  #text(size: 24pt)[
    *The AutoCorrelation Integral Drill (ACID) 2*
  ]

  Robbe Bohy,#super[†¶] Gözdenur Toraman,#super[†] Dieter Fauconnier,#super[†⁰] and Toon Verstraelen#super[✶¶]

  † Soete Laboratory, Ghent University, Technologiepark-Zwijnaarde 46, B-9052 Ghent, Belgium\
  ⁰ FlandersMake\@UGent, Core Lab MIRO, B-3001 Leuven, Belgium\
  ¶ Center for Molecular Modeling (CMM), Ghent University, Technologiepark-Zwijnaarde
  46, B-9052, Ghent, Belgium

  ✶E-mail: #link("mailto:toon.verstraelen@ugent.be", "toon.verstraelen@ugent.be")

  Version #read("git-version.txt").trim() #read("git-date.txt").trim()
]

= Summary

The ACID data set consists of synthetic time-correlated sequences with different lengths and covariance kernels.

The purpose of the data set is to validate algorithms for estimating the integral of an autocorrelation function, which is relevant for uncertainty quantification and the estimation of transport properties.
The first application was to validate the algorithm implemented in #link("https://molmod.github.io/stacie", [STACIE]).

The set contains in total 15360 test cases, and each case consists of one or more time series.
They are organized such that one can systematically study the convergence of the statistical estimate of the autocorrelation integral (and its uncertainty)
with increasing sequence length ($N$) and increasing number of sequences used as input ($M$).

= License

All files in this dataset are distributed under a choice of license:
either the Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0)
or the GNU Lesser General Public License, version 3 or later (LGPL-v3+).
The SPDX License Expression for the documentation is `CC-BY-SA-4.0 OR LGPL-3.0-or-later`.

You should have received a copy of the CC BY-SA 4.0 and LGPL-v3+ licenses along with the data set.
If not, see:

- https://creativecommons.org/licenses/by-sa/4.0/
- https://www.gnu.org/licenses/lgpl-3.0.html

= Overview of the data

Covariance kernels are constructed with one or two of the following three models.
In all models, the parameter $A_0$ corresponds to the integral of the autocorrelation function for that specific contribution.
This value is equal to the zero-frequency limit of the power spectral density.
The three kernel models in continuous time and frequency domains are described by their autocorrelation function (ACF):

$
  c(Delta_t) = upright("COV")[ hat(x)(t), hat(x)(t + Delta_t)]
$

or equivalently their power spectral density (PSD):

$
  C(f) = integral_(-infinity)^infinity c(Delta_t) e^(-2 pi i f Delta_t) dif Delta_t
$

1. The *white noise* model consists of uncorrelated data and has the following ACF:

   $
       c(Delta_t) = A_0 delta(Delta_t)
   $

   The PSD is constant:

   $
       C(f) = A_0
   $

   This model will be denoted as $upright(W)(A_0)$.

2. The *exponential model* has an exponentially decaying ACF:

   $
       c(Delta_t) = A_0/(2 tau) exp (-abs(Delta_t)/tau)
   $

   where $tau$ is the exponential autocorrelation time.
   The PSD is:

   $
       C(f) = A_0/(1 + (2 pi f tau)^2)
   $

   This model will be denoted as $upright(E)(A_0, tau)$.

3. The *stochastic harmonic oscillator* was adapted from #link("https://doi.org/10.3847/1538-3881/aa9332", [the work of Foreman-Mackey et al.])
   Its ACF (with modified normalization conventions) is:

   $
      c(Delta_t) = A_0 pi f_0 Q exp(-(pi f_0 Delta_t)/Q) cases(
         cosh(eta 2 pi f_0 Delta_t) + 1/(2 eta Q) sinh(eta 2 pi f_0 Delta_t)
         & quad "if" quad 0 < Q < 1/2,
         1 + 2 pi f_0 Delta_t
         & quad "if" quad Q = 1/2,
         cos(eta 2 pi f_0 Delta_t) + 1/(2 eta Q) sin(eta 2 pi f_0 Delta_t)
         &quad "if" quad Q > 1/2
       )
   $

   with

   $
       eta = abs(1/(4 Q^2) - 1)^(1/2)
   $

   The PSD is:

   $
       C(f) = (A_0 f_0^4)/((f^2 - f_0^2)^2 + (f f_0\/Q)^2)
   $

   where $Q$ represents the quality of the oscillator and $f_0$ is the resonant frequency.
   (Note that Foreman-Mackey et al. use a parameter $S_0=A_0/2$, a unitary normalization convention for the Fourier transform, and an angular frequency. These differences are only a matter of notation.)

   This model will be denoted as $upright(S)(A_0, f_0, Q)$.

Using these three models, 12 covariance kernels are defined in @tab-summary and were used to generated time-correlated sequences.

#let kernels = csv(sys.inputs.kernels)
#figure(
  table(
      columns: 3,
      align: left,
      table.header[Kernel][Definition][$tau_"int"$],
      ..for(label,typeq,_,cti) in kernels{
          (label, eval("$" + typeq + "$"), cti)
      },
  ),
  caption: [Summary of kernels used in the ACID test set.]
) <tab-summary>

For each kernel, sequences with $N =$ 1024, 4096, 16384, and 65536 steps are generated, using a dimensionless time step $h=1$.
For each kernel and each number of steps, independent test cases are created comprising $M =$ 1, 4, 16, 64, and 256 independent sequences.
To ensure statistical robustness, 64 repetitions with unique random seeds are included for every combination of kernel, number of steps and number of sequences.

Example sequences, ACFs and PSDs for all kernels are shown in @fig-seqs, @fig-acs, and @fig-psds, respectively.

#figure(
  image("output/plot_seqs.svg"),
  caption: [
    Example sequences obtained with each kernel.
    (First 150 steps of the first sequence in the first out of 64 test cases for $N=1024$ and $M=256$.)
  ]
) <fig-seqs>

#figure(
  image("output/plot_acs.svg"),
  caption: [
    Autocorrelation functions of the kernels.
    The analytical model is plotted as a dotted black line.
    The empirical ACF derived from the first out of 64 test cases
    for $N=1024$ and $M=256$ is plotted as a solid red line.
  ]
) <fig-acs>

#figure(
  image("output/plot_psds.svg"),
  caption: [
    Power spectral densities of the kernels.
    The analytical model is plotted as a dotted black line.
    The empirical PSD (periodogram) derived from the first out of 64 test cases
    for $N=1024$ and $M=256$ is plotted as a solid red line.
  ]
) <fig-psds>

All kernels have an autocorrelation integral of 1.
This is achieved by choosing the $A_0$ parameters of the models used in each kernel such that the sum of their autocorrelation integrals equals one.
The kernels are parametrized to have an almost quadratic PSD close to zero frequency, with deviations less than 2.5% RMS for the first 20 grid points of the spectrum and less than 10% for the first 40 points.
This has two important implications on the data:

- It guarantees that also the shortest synthetic sequences (1024 steps) are just long enough
  to capture the slowest time correlations.
  (For longer sequences, the deviation from the quadratic fit are much smaller.)
- For the spectra averaged over 256 sequences, the relative error is about $1/sqrt(256)$, which corresponds to 6.25%.
  This is larger than the systematic deviation between the quadratic model and the real PSD
  for the first 20 points.

For each combination of kernel, sequence length, and number of sequences, data are stored in uncompressed ZIP archives, using the pattern `{kernel_name}_nstep{nstep:05d}_nseq{nseq:04d}.zip`.
(Due to the efficient encoding discussed below, compression saves less than 1%.)
The data and metadata stored in each ZIP file are described in @tab-zip and @tab-meta, respectively.

#figure(
  table(
    columns: 2,
    align: left,
    table.header([filename], [Description]),
    `meta.json`, [Metadata described in @tab-meta],
    `times.npy`, [The time axis of the sequences],
    `freqs.npy`, [The frequency axis of the power spectrum],
    `psd.npy`, [The reference power spectrum with normalization conventions given above],
    `acf.npy`, [The reference autocorrelation function],
    `sequences_00.npy`, [The stochastic time-dependent sequences, first seed],
    [...],[],
    `sequences_63.npy`, [The stochastic time-dependent sequences, last seed],
  ),
  caption: [Overview of data stored in each ZIP file.]
) <tab-zip>


#figure(
  table(
    columns: 2,
    align: left,
    table.header([key], [Description]),
    `kernel`, [The name of the kernel, e.g. `exp1w`],
    `nseed`, [The number of random seeds used for repetitions of the same test],
    `acint`, [The autocorrelation integral],
    `var`, [The variance of the sequences],
    `corrtime_int`, [The integrated autocorrelation time],
    `corrtime_exp`, [The exponential autocorrelation time, or None if not defined],
    `typst`, [A typst equation describing the kernel],
    `latex`, [A latex equation describing the kernel],
  ),
  caption: [Metadata stored in `meta.json` in each ZIP file.]
) <tab-meta>

All arrays, except `sequences_??` are 1D arrays.
The sequences are stored in a 2D array with shape `(nseq, nstep)`, where `nseq` is the number of sequences ($M$) and `nstep` is the number of steps ($N$).
The ground truth of the autocorrelation integral is stored in the metadata as `acint`
and is also equal to `psd[0]`.

The sequences are encoded as unsigned integers.
They can be converted back to floating-point numbers as shown in @code-decode.
The ZIP file is also a valid NPZ file, and arrays (not metadata) can be accessed with `numpy.load`,
as shown in @code-numpy.

#figure(
  box(
    stroke: black,
    inset: 1em,
    ```python
    import json
    import zipfile

    import numpy as np

    with zipfile.ZipFile("exp1w_nstep01024_nseq0256.zip") as zf:
        with zf.open("meta.json") as f:
            meta = json.load(f)
        with zf.open("sequences_00.npy") as f:
            cdfi = np.load(f)
    lookup_table = np.load("output/codec.zip")["midpoint"]
    std = np.sqrt(meta["var"])
    sequences = lookup_table[cdfi] * std
    ```
  ),
  caption: [
    Example Python implementation decoding the integer representation of the sequences back to floating-point numbers.
  ],
  kind: "code",
  supplement: "Code",
) <code-decode>

#figure(
  box(
    stroke: black,
    inset: 1em,
    ```python
    import numpy as np

    freqs = np.load("exp1w.zip")["nstep_1024/freqs.npy"]
    traj = np.load("exp1w.zip")["nstep_1024/nseq_64/sequences_00.npy"]
    ```
  ),
  caption: [
    Example Python code showing how to access arrays in the ZIP files with `numpy.load`.
  ],
  kind: "code",
  supplement: "Code",
) <code-numpy>

= Data generation

All Python scripts required for data generation and analysis are included in the archive.
These scripts make use of open-source software libraries (see below).

The script `plan.py` defines the workflow to reconstruct the entire dataset from scratch.
It can be executed with #link("https://reproducible-reporting.github.io/stepup-core/stable/", [StepUp]) as follows on the command line:

```bash
stepup boot -n 8
```

where `8` is the number of parallel workers.

= Remark on determinism

The data generation scripts are fully deterministic,
meaning that running them multiple times on the same hardware and software environment will yield identical results.
However, differences in floating-point arithmetic across hardware architectures and software versions can cause the
StepUp workflow to produce different time series on different systems.
Even when the numerical results are identical,
the hashes of the ZIP files may differ because of operating system details and software versions.
These differences do not affect the overall validity of the dataset, but they may impact the exact numerical values derived from an analysis.

= Software used

The following software is required to use the dataset:

- Python >= 3.11
- NumPy >= 2
- SciPy >= 1.16

To fully reconstruct the dataset, the following additional Python packages are required:

- StepUp >= 3.2.2
- StepUp RepRep >= 3.1.8
