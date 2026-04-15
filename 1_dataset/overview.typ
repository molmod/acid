// SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
// SPDX-License-Identifier: CC-BY-SA-4.0

#set page("a4", margin: 2cm, numbering: "1 / 1")
#import "@preview/diverential:0.3.0": *
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

These autocorrelation functions can also be used to compute Mean-Squared Displacements (MSDs) of the integrated stochastic trajectory.
The general link between squared displacements and autocorrelation functions follows from e.g. #link("https://doi.org/10.1016/C2009-0-63921-0", [the book by Frenkel and Smit]).
Adopting this approach, the MSD can be written as

$
  "MSD"_y (Delta_t) & = chevron.l hat(y)(Delta_t)^2 chevron.r \
                    & = lr(chevron.l (integral_0^Delta_t hat(x)(t) dif t)^2 chevron.r) \
                    & = integral_0^Delta_t dif t_1 integral_0^Delta_t chevron.l hat(x)(t_1) hat(x)(t_2)chevron.r dif t_2 \
                    & = 2 integral_0^Delta_t (Delta_t - u) c(u) dif u
$
where $hat(y)(t)$ is defined as the time integral of the stochastic trajectory $hat(x)(t)$
$
  hat(y)(t) = integral_0^t hat(x)(s) dif s
$

== ACF Models
1. The *white noise* model consists of uncorrelated data and has the following ACF:

   $
       c(Delta_t) = A_0 delta(Delta_t)
   $

   The PSD is constant:

   $
       C(f) = A_0
   $
   The MSD is:

   $
       "MSD" = A_0 abs(Delta_t)
   $

   where we used the convention
  $
    integral_0^abs(Delta_t) delta(s) dif s = 1/2 integral_(-abs(Delta_t))^abs(Delta_t) delta(s) dif s = 1/2
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

   The MSD is:

   $
       "MSD" = A_0 abs(Delta_t) + A_0 tau[exp(- abs(Delta_t)/tau) - 1]
   $

   This model will be denoted as $upright(E)(A_0, tau)$.

3. The *stochastic harmonic oscillator* was adapted from #link("https://doi.org/10.3847/1538-3881/aa9332", [the work of Foreman-Mackey et al.])
   Its ACF (with modified normalization conventions) is:

   $
     c(Delta_t) = A_0 pi f_0 Q exp(-(pi f_0 abs(Delta_t))/Q) cases(
       cosh(b Delta_t) + 1/(2 eta Q) sinh(b abs(Delta_t)) & quad "if" quad 0 < Q < 1/2,
       1 + 2 pi f_0 abs(Delta_t) & quad "if" quad Q = 1/2,
       cos(b Delta_t) + 1/(2 eta Q) sin(b abs(Delta_t)) & quad "if" quad Q > 1/2
     )
   $

   with

   $
     b = 2pi f_0 eta quad "and" quad eta = abs(1/(4 Q^2) - 1)^(1/2)
   $

   The PSD is:

   $
       C(f) = (A_0 f_0^4)/((f^2 - f_0^2)^2 + (f f_0\/Q)^2)
   $

   where $Q$ represents the quality of the oscillator and $f_0$ is the resonant frequency.
   (Note that Foreman-Mackey et al. use a parameter $S_0=A_0/2$, a unitary normalization convention for the Fourier transform, and an angular frequency. These differences are only a matter of notation.)

  The MSD is:

  $
    "MSD" = A_0 abs(Delta_t) - ell + ell exp(- (pi f_0 abs(Delta_t)) / Q) cases(
      cosh(b Delta_t) + 1/(2 eta Q) ((1 - 3 Q^2)/(1-Q^2)) sinh(b abs(Delta_t)) & quad "if" quad 0 < Q < 1/2,
      1 + 2/3pi f_0 abs(Delta_t) & quad "if" quad Q = 1/2,
      cos(b Delta_t) + 1/(2 eta Q)((1-3Q^2)/(1 - Q^2))sin(b abs(Delta_t)) & quad "if" quad Q > 1/2
    )
  $
  with

  $
      ell = (A_0 (1 - Q^2))/(2 pi f_0 Q)
  $

   This model will be denoted as $upright(S)(A_0, f_0, Q)$.

== Kernel Construction

Using these three models, 12 covariance kernels are defined in @tab-summary and were used to generate time-correlated sequences,
where the integrated correlation times ($tau_"int"$) are calculated using

$
      tau_"int" = 1/2 C(f = 0) / c(Delta_t = 0)
$

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
For sequence length, test cases are created comprising $M =$ 1, 4, 16, 64, and 256 independent sequences.
To ensure statistical robustness, each $("kernel", N, M)$ combination is repeated with 64 unique random seeds.

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

#figure(
  image("output/plot_msds.svg"),
  caption: [
    Mean-squared displacements of the kernels.
    The analytical model is plotted as a dotted black line.
    The empirical MSD derived from the first out of 64 test cases
    for $N=1024$ and $M=256$ is plotted as a solid red line.
  ],
) <fig-msds>

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

== Data Organization
For each kernel, data are stored in an uncompressed ZIP archive following the pattern `{kernel_name}.zip`.
Due to the efficient encoding discussed below,
compression would reduce the file size by less than 1%.
Each ZIP archive contains both data and metadata.
An overview of the stored data is provided in @tab-zip,
while the stored metadata are listed in @tab-meta.

#figure(
  table(
    columns: 2,
    align: left,
    table.header([filename], [Description]),
    `meta.json`, [Metadata described in @tab-meta],
    `nstepXXXXX/times.npy`, [Time axis for $N$ = `XXXXX`],
    `nstepXXXXX/freqs.npy`, [Frequency axis of the power spectrum for $N$ = `XXXXX`],
    `nstepXXXXX/psd.npy`, [Reference power spectral density for $N$ = `XXXXX`],
    `nstepXXXXX/acf.npy`, [Reference autocorrelation function for $N$ = `XXXXX`],
    `nstepXXXXX/msd.npy`, [Reference mean-squared displacement function for $N$ = `XXXXX`],
    `nstepXXXXX/nseqYYYY/sequences_ZZ.npy`,
    [
      Stochastic sequences for a given $N$ = `XXXXX`, $M$ = `YYYY`, and seed index `ZZ`
    ],
  ),
  caption: [Overview of data stored in each ZIP archive. The dataset is organized in subdirectories grouped by the number of steps (`nstepXXXXX`) and the number of sequences (`nseqYYYY`). Inside each `nstepXXXXX/nseqYYYY/` subfolder, the files `sequences_ZZ.npy` store the stochastic time-dependent sequences, with the seed index `ZZ` running from 00 to 63.],
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
  caption: [Metadata stored in `meta.json` in each ZIP archive.]
) <tab-meta>

All data arrays are one-dimensional, except for `sequences_??`.
The sequences are stored in a two-dimensional array with shape `(nseq, nstep)`,
where `nseq` is the number of sequences ($M$) and `nstep` is the number of steps ($N$).
The sequences are encoded as unsigned integers and can be converted back to floating-point values as shown in @code-decode.
Each ZIP archive is also a valid NPZ file,
and all data arrays (not metadata) can be accessed using `numpy.load`,
as shown in @code-numpy.

The ground truth value of the autocorrelation integral is stored in the metadata as `acint`
and is equal to `psd[0]`.
Empirical MSDs are computed from the time integral of the trajectories as illustrated in @code-msd.
The implementation in this example is intentionally kept simple to demonstrate data usage.
More efficient strategies have been proposed,
which avoid overlapping windows and evaluate only a selected subset of time lags,
as described by e.g. #link("https://doi.org/10.1063/5.0188081",[Moustafa et al.])


#figure(
  box(
    stroke: black,
    inset: 1em,
    ```python
    import json
    import zipfile

    import numpy as np

    with zipfile.ZipFile("exp1w.zip") as zf:
        with zf.open("meta.json") as f:
            meta = json.load(f)
        with zf.open("nstep01024/nseq0256/sequences_00.npy") as f:
            cdfi = np.load(f)
    lookup_table = np.load("codec.zip")["midpoint"]
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

    freqs = np.load("exp1w.zip")["nstep01024/freqs.npy"]
    traj = np.load("exp1w.zip")["nstep01024/nseq0064/sequences_00.npy"]
    ```
  ),
  caption: [
    Example Python code showing how to access arrays in the ZIP files with `numpy.load`.
  ],
  kind: "code",
  supplement: "Code",
) <code-numpy>


#figure(
  box(
    stroke: black,
    inset: 1em,
    ```python
    import numpy as np

    sequences = np.load("exp1w.zip")["nstep01024/nseq0064/sequences_00.npy"]
    antiderivatives = np.cumsum(sequences, axis=1)
    nstep = sequences.shape[1]

    msds = np.zeros(nstep)
    for delta in range(nstep):
        diffs = antiderivatives[:, delta:] - antiderivatives[:, : nstep - delta]
        msds[delta] = np.mean(diffs**2)
    ```,
  ),
  caption: [
    Example Python code showing how to compute the mean-squared displacements of the trajectories.
  ],
  kind: "code",
  supplement: "Code",
) <code-msd>


= Trajectory generation

Synthetic trajectories consistent with the predefined autocorrelation kernels are generated using linear Stochastic Differential Equations (SDEs),
following the methodology of #link("https://doi.org/10.1093/oso/9780195140187.001.0001", [Zwanzig]).
The most general second-order representation relevant here is
$
  dv(x(t), t, deg: 2) = theta_1 x + theta_2 dv(x (t), t) + F_v (t)
$
which may be rewritten as a system of coupled first-order equations.
$
  dv(x (t), t) & = v (t) \
  dv(v (t), t) & = theta_1 x(t) + theta_2 v(t) + F_v (t)
$
In matrix form,
this two-dimensional system can be written as a single linear differential equation
$
  dv(bold(X) (t), t) = bold(Theta) bold(X) (t) + bold(F)(t)
$
where
$
  bold(X)(t) = mat(
    x(t);
    dot(x)(t)
  ), quad bold(Theta) = mat(
    0, 1;
    theta_1, theta_2
  ), quad bold(F)(t) = mat(0; F_v (t))
$
The stochastic part of these equations satisfies the condition
$
  chevron.l bold(F)(t) bold(F) (t')chevron.r = 2 bold(B) delta(t-t')
$
This linear differential equation is exactly solvable with an analytical solution
$
  bold(X)(t) = e^(bold(Theta) t) bold(X)(0) + integral_0^t e^(bold(Theta)(t-s)) bold(F)(s) dif s
$
Synthetic trajectories are generated by sampling a multivariate Gaussian distribution for each discrete timestep $h$.
The mean of the Gaussian distribution corresponding to this time increment $h$
is given by $e^(bold(Theta) h) bold(X)(t)$.
The second moment of this increment depends only on the stochastic term
$
  chevron.l bold(X)(t) bold(X) (t) chevron.r &= integral_0^t integral_0^t e^(bold(Theta)(t-s)) chevron.l bold(F)(s) bold(F) (s')chevron.r e^(bold(Theta^dagger)(t-s')) dif s dif s' \
  &= 2 integral_0^t e^(bold(Theta)(t-s)) bold(B) e^(bold(Theta^dagger)(t-s)) dif t \
  &= 2 integral_0^t e^(bold(Theta)t) bold(B) e^(bold(Theta^dagger)t) dif t
$
In Zwanzig's derivation,
the second moment of the stationary distribution, $M=lim_(t->infinity) chevron.l bold(X)(t) bold(X) (t) chevron.r$, is obtained as the solution of this integral reformulated as a continuous-time Lyapunov equation
$
  bold(Theta) bold(M) + bold(M) bold(Theta)^dagger & = 2 integral_0^infinity dv(, t) e^(bold(Theta) t) bold(B) e^(bold(Theta)^dagger t) dif t \
  &= 2 (e^(bold(Theta) t) bold(B) e^(bold(Theta)^dagger t))_(t -> infinity) - 2 bold(B)\
  &= - 2 bold(B)
$
For the trajectory generation in ACID,
the relevant quantity is not the equilibrium second moment,
but the covariance corresponding to the finite increment $h$,
$M_h = chevron.l bold(X)(h) bold(X) (h) chevron.r$.
Adapting the integration limits gives
$
  bold(Theta) bold(M)_h + bold(M)_h bold(Theta)^dagger & = 2 integral_0^(h) dv(, t) e^(bold(Theta) t) bold(B) e^(bold(Theta)^dagger t) dif t \
  &= 2 e^(bold(Theta) h) bold(B) e^(bold(Theta)^dagger h) - 2 bold(B)\
$
Solving this Lyapunov equation yields the desired covariance per increment $M_h$.
As a result,
the discrete-time update in ACID is given by sampling the multivariate Gaussian distribution
$
  bold(X) (t + h) ~ cal(N)(e^(bold(Theta) h) bold(X)(t), bold(M)_h)
$


Using this framework, trajectories for the three kernel models are
generated using these linear SDEs as follows.

1. *White noise*:
This represents a memoryless process,
solely dependent on the stochastic force.
Each timestep is an independent Gaussian increment with variance $A_0$.
$
  x(t+1) ~cal(N)(0,A_0)
$

2. *Exponential model*:
The corresponding SDE is one-dimensional and requires sampling a univariate Gaussian distribution rather than a multivariate one:
$
  dv(x(t), t) = theta x(t) + F(t), quad theta = - 1/tau
$
$
  x(t+1) ~ cal(N)(e^(theta h)x(t), sigma^2) ,quad sigma^2 = A_0/(2tau) (1 - e^(-(2h)/tau))
$
3. *Stochastic Harmonic Oscillator*:
The underlying set of linear SDEs for this two-dimensional system is given by
$
  dv(bold(X)(t), t) = bold(Theta) bold(X)(t) + bold(F)(t)
  , quad "with"
  bold(Theta) = mat(
    0, 1;
    -(2 pi f_0)^2, - (2 pi f_0)/ Q
  )
$
with the noise satisfying

$
  chevron.l bold(F)(t) bold(F) (t')chevron.r = 2 bold(B) delta(t-t'), quad "with" bold(B) = mat(
    0, 0;
    0, (A_0 (2 pi f_0)^4)/2
  )
$

The increment covariance $bold(M_h)$ is obtained by numerically solving the finite-time Lyapunov equation as described above.
A closed-form expression exists,
but is lengthy and depends on the damping regime,
and is therefore not shown here.

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
