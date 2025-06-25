#show link: set text(blue)
#show table.cell.where(y: 0): set text(weight: "bold")
#let frame(stroke) = (x, y) => (
  top: if y < 2 { stroke } else { 0pt },
  bottom: stroke,
)

#set table(
  stroke: frame(rgb("21222C")),
)


#align(center)[
  #text(size: 24pt)[
    *The AutoCorrelation Integral Drill (ACID) Test Set*
  ]

  Gözdenur Toraman,#super[†] Dieter Fauconnier,#super[†‡] and Toon Verstraelen#super[✶¶]

  † Soete Laboratory, Ghent University, Technologiepark-Zwijnaarde 46, 9052 Ghent, Belgium\
  ‡ FlandersMake\@UGent, Core Lab EEDT-MP, 3001 Leuven, Belgium\
  ¶ Center for Molecular Modeling (CMM), Ghent University, Technologiepark-Zwijnaarde
  46, B-9052, Ghent, Belgium

  ✶E-mail: #link("mailto:toon.verstraelen@ugent.be", "toon.verstraelen@ugent.be")

  Version #read("gitline.txt")
]

= Summary

The data set consists of synthetic time-correlated sequences of varying lengths, generated using different covariance kernels.

The purpose of the data set is to validate algorithms for estimating the integral of an autocorrelation function, which is relevant for uncertainty quantification and the estimation of transport properties.
The first application was to validate the algorithm implemented in #link("https://molmod.github.io/stacie", [STACIE]) 1.0.

The set contains in total 15360 test cases, and each case consists of one or more time series.
They are organized such that one can systematically study the convergence of the statistical estimate of the autocorrelation integral (and its uncertainty)
with increasing sequence length ($N$) and increasing number of sequences used as input ($M$).

= License

All files in this dataset are licensed under a #link("http://creativecommons.org/licenses/by-nc/4.0/", [Creative Commons Attribution-NonCommercial 4.0 International License]).

= Overview of the data

Covariance kernels are constructed with one or two of the following three models.
In all models, the parameter $C_0$ corresponds to the integral of the autocorrelation function for that specific contribution.
The three kernel models in continuous time and frequency domains are described by their autocorrelation function (ACF):

$
  c(Delta_t) = upright("COV")[ hat(x)(t), hat(x)(t + Delta_t)]
$

or equivalently their power spectral distribution (PSD):

$
  C(f) = integral_(-infinity)^infinity c(Delta_t) e^(-2 pi i f Delta_t) dif Delta_t
$

1. The *white noise* model consists of uncorrelated data and has the following ACF:

   $
       c(Delta_t) = C_0 delta(Delta_t)
   $

   The PSD is constant:

   $
       C(f) = C_0
   $

   This model will be denoted as $upright(W)(C_0)$.

2. The *exponential model* has an exponentially decaying ACF:

   $
       c(Delta_t) = C_0/(2 tau) exp (-abs(Delta_t)/tau)
   $

   where $tau$ is the exponential autocorrelation time and $C_0$ is the integral of the autocorrelation function.
   The PSD is:

   $
       C(f) = C_0/(1 + (2 pi f tau)^2)
   $

   This model will be denoted as $upright(E)(C_0, tau)$.

3. The *stochastic harmonic oscillator* was adapted from #link("https://doi.org/10.3847/1538-3881/aa9332", [the work of Foreman-Mackey et al.]).
   It's ACF (with modified normalization conventions) is:

   $
      c(Delta_t) = C_0 pi f_0 Q exp(-(pi f_0 Delta_t)/Q) cases(
         cosh(eta 2 pi f_0 Delta_t) + 1/(2 eta Q) sinh(eta 2 pi f_0 Delta_t)
         & quad "if" quad 0 < Q < 1/2,
         1 + 2 pi f_0 tau
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
       C(f) = (C_0 f_0^4)/((f^2 - f_0^2)^2 + (f f_0\/Q)^2)
   $

   where $Q$ represents the quality of the oscillator, $f_0$ is the angular resonant frequency, and $C_0$ is the zero-frequency limit of the spectrum.
   (Note that Foreman-Mackeyet al. use a parameter $S_0=2C_0$, a unitary normalization convention for the Fourier transform and an angular frequency. These differences are only a matter of notation.)

   This model will be denoted as $upright(S)(C_0, f_0, Q)$

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

For each kernel, sequences with $N =$ 1024, 4096, 16384 and 65536 steps are generated, using a dimensionless time step $h=1$.
(In fact, sequences of double this length are generated with a discrete Fourier transform and the second half is discarded to obtain aperiodic sequences.)
For each kernel and each number of steps, independent test cases are created comprising $M =$ 1, 4, 16, 64, and 256 independent sequences.
To ensure statistical robustness, 64 repetitions with unique random seeds are included for every combination of kernel, number of steps and number of sequences.

Example sequences, ACFs and PSDs for all kernels are shown in Figures @fig-seqs, @fig-acs and @fig-psds, respectively.

#figure(
  image("plot_seqs.svg"),
  caption: [
    Example sequences obtained with each kernel.
    (First 150 steps of the first sequence in the first out of 64 test cases for $N=1024$ and $M=256$.)
  ]
) <fig-seqs>

#figure(
  image("plot_acs.svg"),
  caption: [
    Autocorrelation functions of the kernels.
    The analytical model is plotted as a dotted black line.
    The empirical ACF derived from the first out of 64 test cases
    for $N=1024$ and $M=256$ is plotted as a red solid line.
  ]
) <fig-acs>

#figure(
  image("plot_psds.svg"),
  caption: [
    Power spectral distributions (PSDs) of the kernels.
    The analytical model is plotted as a dotted black line.
    The empirical PSD (periodogram) derived from the first out of 64 test cases
    for $N=1024$ and $M=256$ is plotted as a red solid line.
  ]
) <fig-psds>

All kernels have an autocorrelation integral of 1.
They are all parametrized to have an almost quadratic PSD close to zero frequency, with deviations less than 2.5% RMS for the first 20 grid points of the spectrum and less than 10% for the first 40 points.
This has two important implications on the data:

- It guarantees that also the shortest synthetic sequences (1024 steps) are just long enough
  to capture the slowest time correlations.
  (For longer sequences, the deviation from the quadratic fit are much smaller.)
- For the spectra averaged over 256 sequences,   the relative error is about $1/sqrt(256)$, which corresponds to 6.25%.
  This is larger than the systematic deviation between the quadratic model and the real PSD
  for the first 20 points.

For each combination of kernel, sequence length and number of sequences, data are stored in #link("https://zarr.readthedocs.io", [ZARR]) version 3 ZIP archives, using the pattern `{kernel_name}_nstep{nstep:05d}_nseq{nseq:04d}.zip`.
The data stored in each ZARR file are described in @tab-zarr.

#figure(
  table(
    columns: 2,
    align: left,
    table.header([ZARR field], [Description]),
    `root.attrs["corrtime_int"]`, [The integrated autocorrelation time],
    `root.attrs["typst"]`, [A typst equation describing the kernel],
    `root.attrs["latex"]`, [A latex equation describing the kernel],
    `root["times"]`, [The time axis of the sequences],
    `root["freqs"]`, [The frequency axis of the power spectrum],
    `root["omegas"]`, [$2 pi times$ the frequency axis],
    `root["psd"]`, [The reference power spectrum with normalization conventions given above],
    `root["acf"]`, [The reference autocorrelation function],
    `root["sequences"]`, [The stochastic time-dependent sequences],
  ),
  caption: [Overview of data stored in each ZARR file.]
) <tab-zarr>

All arrays, except `sequences` are 1D arrays.
The sequences are stored in a 3D array with shape `(ncase, nseq, nstep)`, where `ncase` is 64, `nseq` is the number of sequences ($M$) and `nstep` is the number of steps ($N$).
The ground truth of the autocorrelation integral is `root["psd"][0]`.

= Data generation

All Python scripts required for data generation and analysis are included in the archive.
These scripts make use of open-source software libraries (see below).

The script `plan.py` defines the workflow to reconstruct the entire dataset from scratch.
It can be executed with #link("https://reproducible-reporting.github.io/stepup-core/stable/", [StepUp]) as follows on the command line:

```bash
stepup boot -n 8
```

where `8` is the number of parallel workers.

= Software used

The following software is required to use the dataset:

- Python >= 3.12
- NumPy == 2
- Zarr == 3

To fully reconstruct the dataset, the following additional Python packages are required:

- StepUp >= 3.0.3
- StepUp RepRep >= 3.0.3
