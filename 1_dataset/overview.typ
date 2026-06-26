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
The first application was to validate the algorithm implemented in #link("https://molmod.github.io/stacie", [STACIE]) @toraman2025stable.

The set contains in total 19200 test cases, and each case consists of one or more time series.
They are organized such that one can systematically study the convergence of the statistical estimate of the autocorrelation integral (and its uncertainty)
with increasing sequence length ($N$) and increasing number of sequences used as input ($M$).

= Overview of the data

Covariance kernels are constructed with one or two of the following four models.
In all models, the parameter $A_0$ corresponds to the integral of the autocorrelation function for that specific contribution.
This value is equal to the zero-frequency limit of the power spectral density.
The four kernel models in continuous time and frequency domains are described by their autocorrelation function (ACF):

$
  c(Delta_t) = upright("COV")[ hat(x)(t), hat(x)(t + Delta_t)]
$

or equivalently their power spectral density (PSD):

$
  C(f) = integral_(-infinity)^infinity c(Delta_t) e^(-2 pi i f Delta_t) dif Delta_t
$

These autocorrelation functions can also be used to compute Mean-Squared Displacements (MSDs) of the integrated stochastic trajectory.
The general link between squared displacements and autocorrelation functions follows from e.g. the book by Frenkel and Smit @frenkel2023understanding.
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

3. The *stochastic harmonic oscillator* was adapted from the work of Foreman-Mackey et al. @foreman2017fast
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

4. The *power-law model* has an ACF with power-law decay:
  $
    c(Delta_t) = (A_0 (alpha -1))/(2 theta ) (1+ abs(Delta_t) / theta)^(-alpha)
  $
  where $alpha gt 1$ represents the power-law exponent, and $theta gt 0$ is a characteristic time scale.

  The PSD is:
  $
    C(f) = A_0 (alpha - 1) Re[e^(2 pi i f theta)E_alpha (2 pi i f theta)]
  $
  where $Re(z)$ denotes the real part and $E_p (z)$ represents the generalized exponential integral defined as
  $
    E_p (z) = integral_1^infinity (e^(-z t))/t^p dif t
  $
  The corresponding MSD is:
  $
    "MSD" = A_0 abs(Delta_t) + (A_0 theta) / (alpha - 2) [ -1 + (1+ abs(Delta_t)/ theta)^(-alpha + 2)]
  $
  This expression for the MSD is only well-defined for $alpha eq.not 2$,
  due to the denominator of $(alpha - 2)$.

  This model will be denoted as $upright(P)(A_0, alpha, theta)$.

== Kernel Construction

Using these four models, 12 covariance kernels are defined in @tab-summary and were used to generate time-correlated sequences,
where the integrated correlation times ($tau_"int"$) are calculated using

$
      tau_"int" = 1/2 C(f = 0) / c(Delta_t = 0)
$

#let kernels = csv(sys.inputs.kernels)
#figure(
  table(
      columns: 6,
      align: (left, left, center, center, center, center),
      table.header[Kernel][Definition][Variance][ACF integral][$tau_"int"$][$tau_"exp"$],
      ..for(label,typeq,_,var,acint,cti,cte) in kernels{
          (label, eval("$" + typeq + "$"), var, acint, cti, cte)
      },
  ),
  caption: [Summary of kernels used in the ACID test set.]
) <tab-summary>

For each kernel, sequences with $N =$ 256, 1024, 4096, 16384, and 65536 steps are generated, using a dimensionless time step $h=1$.
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

The kernels are parametrized such that the low-frequency region of the PSD can be approximated by either a quadratic dependence or a power-law dependence with exponent $1/2$.
The inclusion of the $f^(1/2)$ term parallels an early discussion by #link("https://doi.org/10.1063/1.445384", [Holian and Evans]), who argued that a long-time tail in the ACF proportional to $t^(-3/2)$ is expected to give rise to a $-f^(1/2)$ cusp in the low-frequency PSD.

The deviation from the best of these fits is constrained to remain below 2.5% RMS for the first 10 frequency points (for $N = 1024$) and below 10% for the first 20 points.
As a result,
even short sequences ($N = 1024$) remain long enough to capture the slowest time correlations.

For comparison,
the relative error when averaging over $M = 256$ independent sequences is on the order of $1/sqrt(256) = 6.25%$,
which is larger than the imposed deviation threshold for the 10 lowest frequency points.

The power-law kernels are further controlled through the parameter $alpha$,
which directly affects the second term of their MSD:
  - For $alpha gt 2$,
    the MSD rapidly approaches its asymptotic linear scaling,
    and corresponding MSD fits are well-behaved.
  - For $1 lt alpha lt 2$,
    the convergence toward the linear regime is significantly slower,
    making MSD-based analysis more challenging.

The $1 lt alpha lt 2$ regime therefore provides the most challenging and informative test cases,
and all power-law kernels are defined within it.
The choice $alpha = 3/2$ is motivated by its physical relevance for diffusion in dense three-dimensional fluids, as discussed by Alder and Wainwright @alder1970decay.


== Data Organization
For each kernel, the data are stored in an uncompressed ZIP archive following the pattern `{kernel_name}.zip`.

Each ZIP archive contains both data and metadata.
An overview of the stored data is provided in @tab-zip,
while the metadata are listed in @tab-meta.
The archive is also a valid NPZ file,
so all data arrays (excluding metadata) can be accessed directly using `numpy.load`,
as shown in @code-numpy.

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


All data arrays are one-dimensional except for `sequences_??.npy`,
which are stored as two-dimensional arrays with shape `(nseq, nstep)`,
where `nseq` is the number of sequences ($M$) and `nstep` is the number of steps ($N$).

To reduce storage requirements,
the sequences are not stored as floating-point values,
but as unsigned integers.
Each floating-point value is mapped through the Cumulative Distribution Function (CDF) of a Gaussian distribution
and discretized on a uniform grid of $2^{16}$ points in $[0,1]$.
This discretization yields an integer representing the corresponding index on the grid.
A fixed lookup table,
constructed from the corresponding percent point function (inverse of the CDF),
assigns a corresponding floating-point value to each index for decoding,
as demonstrated in @code-decode.

As a result of this integer encoding,
further compression of the ZIP archives yields less than 1% reduction and is therefore not applied.

The ground truth value of the autocorrelation integral is stored in the metadata as `acint`
and is equal to `psd[0]`.
Empirical MSDs are computed from the time integral of the trajectories,
as illustrated in @code-msd.
The implementation here is intentionally kept simple to demonstrate data usage.
More efficient strategies have been proposed,
which avoid overlapping windows and evaluate only a selected subset of time lags,
as described by e.g. Moustafa et al. @moustafa2024efficient


#figure(
  box(
    stroke: black,
    inset: 1em,
    ```python
    import numpy as np

    freqs = np.load("exp1w.zip")["nstep01024/freqs.npy"]
    traj = np.load("exp1w.zip")["nstep01024/nseq0064/sequences_00.npy"]
    ```,
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
following the methodology of Zwanzig @zwanzig2001nonequilibrium.
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
  &= 2 integral_0^t e^(bold(Theta)(t-s)) bold(B) e^(bold(Theta^dagger)(t-s)) dif s \
  &= 2 integral_0^t e^(bold(Theta)t') bold(B) e^(bold(Theta^dagger)t') dif t'
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


Using this framework, trajectories for the four kernel models are
generated using these linear SDEs as follows.

1. *White noise*:
This represents a memoryless process,
solely dependent on the stochastic force.
Each timestep is an independent Gaussian increment with variance $A_0$.
$
  x(t + h) ~cal(N)(0,A_0)
$

2. *Exponential model*:
The corresponding SDE is one-dimensional and requires sampling a univariate Gaussian distribution rather than a multivariate one:
$
  dv(x(t), t) = theta x(t) + F(t), quad theta = - 1/tau
$
$
  x(t + h) ~ cal(N)(e^(theta h)x(t), sigma^2) ,quad sigma^2 = A_0/(2tau) (1 - e^(-(2h)/tau))
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


4. *Power-law model*:
To the best of our knowledge,
the power-law model cannot be represented exactly by any finite-dimensional linear SDE.
Instead, the power-law decaying ACF can be represented as a superposition of exponentials,
based on the following Laplace-type integral representation
$
  (1+ abs(Delta_t)/theta)^(-alpha) & = cal(L)[w(tau)] \
                                   & = integral_0^infinity w(tau) exp(-abs(Delta_t)/tau) dif tau
$
with
$
  w(tau) & = theta^2/Gamma(alpha) tau^(-(alpha + 1)) exp(-theta/tau)
$
Using this identity,
the power-law kernel can be rewritten as
$
  c(Delta_t) = (A_0 (alpha - 1))/(2 theta) integral_0^infinity w(tau) exp(-abs(Delta_t)/tau) dif tau
$


Using numerical quadrature,
this integral can be approximated by a finite sum of exponentially decaying kernels:
$
  c(Delta_t) & approx sum_(i=1)^("order")w(tau_i) ((A_0(alpha-1))/(2theta)) exp(-abs(Delta_t)/tau_i) \
             & approx sum_(i=1)^("order")w(tau_i) A_(0,i)^"exp"/(2tau_i) exp(-abs(Delta_t)/tau_i) \
             & approx sum_(i=1)^("order")w(tau_i) upright(E)(A_(0,i)^"exp", tau_i) \
$
where $upright(E)(A_(0,i)^"exp", tau)$ is the previously defined exponential kernel and $A_(0,i)^"exp"$ is defined as
$
  A_(0,i)^"exp" = (A_0(alpha-1) tau_i)/(theta)
$
To construct the quadrature grid,
the semi-infinite integration domain $tau in [0, infinity)$ is mapped to a finite interval using the variable transformation:
$
  1/tau = s((1 + k)/(1 - k)) quad k in[-1,1]
$
with $s$ a dimensionless scaling factor to improve the coverage of large time lags.
The quadrature nodes $tau_i$ and weights $w(tau_i)$ are obtained using Chebyshev quadrature of the first kind.
By increasing the quadrature order,
arbitrary accuracy can be reached.

Finally, trajectories of the power-law model are generated by sampling a finite set of independent exponential kernels,
and taking linear combinations of the resulting trajectories according to
$
  x^("pow")(t) = sum_i sqrt(w(tau_i)) space x_i^"exp" (t)
$

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

= Unit tests
To ensure the correctness of the implementations and analytical expressions,
a comprehensive set of unit tests is included in the repository.
In particular,
these tests verify:
- The low-frequency part of the PSD,
  as discussed above.
- The correctness of the lookup table used for encoding and decoding the trajectories.
- Consistency between derived quantities.
  The ACF is recovered from the MSD by differentiation, and the PSD from the ACF by Fourier transformation.
- The accuracy of the quadrature-based approximation of the power-law kernel.

All tests can be executed using the `pytest` command in the top-level directory.

= Software used

The following software is required to use the dataset:

- Python >= 3.11
- NumPy >= 2
- SciPy >= 1.16
- mpmath >= 1.4

To fully reconstruct the dataset, the following additional Python packages are required:

- StepUp >= 3.2.2
- StepUp RepRep >= 3.1.8

#bibliography("references.bib")
