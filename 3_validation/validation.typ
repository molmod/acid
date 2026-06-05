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
  *#it.supplement #context (it.counter.display(it.numbering))#it.separator*#it.body
]
#let diag = math.op("diag")

#align(center)[
  #text(size: 24pt)[
    *Validation of the AutoCorrelation Integral Drill (ACID) 2*
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
This document presents the validation of the ACID 2 dataset.
Unit tests ensure correctness of the mathematical derivations and implementations,
as described in `overview.typ`.
Here,
the validation of the resulting data is discussed,
with the goal of assessing whether the samples:
- Follow the desired distributions.
- Satisfy stationarity.
- Show minimal bias introduced by the encoding and decoding scheme.

= Autocorrelation Function Consistency
This validation assesses whether the sampled trajectories are consistent with the target distribution defined by the Autocorrelation Function (ACF).

To probe this,
differences in the trajectory at different times are considered,
$
 y(Delta_t) = x(t + Delta_t) - x(t)
$
In contrast to $x(t)$,
whose distribution depends only on the variance,
the distribution of $y(Delta_t)$ is dependent on the ACF.
Its variance is given by
$
  "Var"[y] = "Var"[x(t + Delta_t)] + "Var"[x(t)] - 2 "Cov"[x(t + Delta_t),x(t)]
$
Under stationarity,
where the variance is constant and the covariance depends only on the time difference,
this simplifies to
$
  "Var"[y] = 2 (sigma^2 - "ACF"(Delta_t))
$
using
$
"Var"[x(t + Delta_t)] = "Var"[x(t)] = sigma^2  quad "and" quad "Cov"[x(t + Delta_t),x(t)] =  "ACF"(Delta_t)
$

A normalized variable $z$ is introduced
$
  z(Delta_t) = y(Delta_t) / "Std"[y],
$
which follows a standard normal distribution if the trajectories are sampled from the correct distribution.

This hypothesis is tested using the one-sample Cramér-von Mises (CvM) test with
$
  H_0 : z_i tilde.op cal(N)(0, 1)
$
The test statistic is calculated using
$
T = 1/(12 N_"samples") + sum_(i = 1)^N_"samples" [(2i-1)/(2N_"samples") - F^*(z_i)]^2
$
where $F^*(z_i)$ is the theoretical distribution evaluated at the empirical data points,
and $N_"samples"$ is the number of samples $z_i$ at a given $Delta_t$.

The resulting $p$-values are evaluated as a function of $Delta_t$ in @fig-acf-consist.
Comparison of these $p$-values against a conventional threshold such as $alpha = 0.05$ provides a first indication of agreement with the expected distribution.

However, individual $p$-values must be interpreted with care.
Even when the null hypothesis is correct,
$p$-values are random variables that are uniformly distributed on $[0,1]$,
so that a fraction $alpha$ of all tests will yield $p lt alpha$ @murdoch2008p @wasserstein2016asa.
Consequently, isolated "significant" values are expected and do not in themselves indicate a deviation from the model.
Likewise,
large $p$-values correspond to observations that are not unusual under the assumed distribution,
but they should not be interpreted as direct evidence for its correctness @greenland2016statistical.

For this reason,
the validation focuses on the distribution of $p$-values across all considered $Delta_t$.
Under $H_0$,
these should follow a uniform distribution
$
  H_0 : p_i tilde.op U(0, 1),
$
which is tested using a second CvM test,
shown in the bottom panel of @fig-acf-consist.


#figure(
  image("output/acf_consist.svg"),
  caption: [
ACF consistency validation.
Top panels: $p$-values of the CvM test as a function of $Delta_t$,
with $alpha = 0.05$ (red dashed)
and low-covariance points in light gray.
Bottom panels: distributions of the $p$-values.
The dashed red line indicates the expected uniformity,
and $p_(U(0,1))$ corresponds to the CvM test for $U(0,1)$.
  ],
) <fig-acf-consist>

= Stationarity
Stationarity is assessed by evaluating the distribution of $x(t)$ at different relative times $t/N = 0.01$, $0.5$, and $0.9$,
probing early, intermediate, and late stages of the trajectories.
For each relative time,
samples are pooled across all trajectories.

Under stationarity,
the distribution of $x(t)$ must be independent of $t$ and follow
$
  x_i tilde.op cal(N)(0, sigma^2)
$

To test this,
a Cramér-von Mises test is applied on the normalized variables
$
  z_i = x_i / sigma
$
with
$
  H_0 : z_i tilde.op cal(N)(0, 1)
$

The resulting test statistics and $p$-values are reported for each relative time,
together with corresponding Q-Q plots comparing empirical and theoretical quantiles in @fig-stat.

As in the ACF consistency analysis,
individual $p$-values should be interpreted with care:
even under $H_0$,
the $p$-values follow a $U(0,1)$ distribution.
As a result,
a fraction $alpha$ of all tests are expected to have $p lt alpha$.
Consequently,
the occurrence of a $p$-value below $0.05$ does not in itself indicate a violation of stationarity.

Instead of relying on these individual $p$-values,
the assessment focuses on consistency across early, intermediate, and late times,
together with the agreement observed in the Q-Q plots.

#figure(
  image("output/stationarity.svg"),
  caption: [
Validation of stationarity.
Q-Q plots of $x(t)$ at relative times $t/N = 0.01$, $0.5$, and $0.9$.
Theoretical quantiles are computed from $cal(N)(0, sigma^2)$.
The dotted line indicates perfect agreement.
  ],
) <fig-stat>


= Encoding/decoding scheme

To reduce storage requirements,
the sequences are not stored as floating-point values,
but as unsigned integers.
Each floating-point value is mapped through the cumulative distribution function (CDF) of a Gaussian distribution and subsequently discretized on a uniform grid of $2^16$ points in the interval $[0,1]$.
This discretization yields an integer index representing the position on the grid.

Decoding is performed using a fixed lookup table constructed from the corresponding percent point function (inverse CDF).
Each stored index is mapped back to a floating-point value via the midpoint of the associated bin,
yielding a reconstructed trajectory $x_"codec" (t)$.

To quantify the impact of this discretization,
the power spectral density (PSD) of the trajectories is compared against a reference PSD.

Using the analytical ACF,
the covariance matrix ($bold(C)$) is constructed as
$
  bold(C)_(i j) = "ACF"(abs(i-j)),
$
with dimensions $N times N$.
The resulting reference PSD is obtained from the diagonal of the Fourier-transformed covariance matrix
$
  "PSD" = diag(bold(F)bold(C)bold(F)^dagger)
$
where $bold(F)$ denotes the discrete Fourier transform matrix.
Consequently,
this reference PSD construction incorporates the same finite-size and FFT-related artifacts as the sampled trajectories.

In parallel,
sampled trajectories are generated in full floating-point precision,
and their PSD is estimated.
This provides a baseline error,
defined as the root-mean-square error (RMSE) with respect to the reference PSD,
$
  "RMSE"_"float,ref" = sqrt(1/(M N_f) sum_(f=1)^N_f sum_(k=1)^M ("PSD"_("float")^((k)) (f) - "PSD"_("reference") (f))^2)
$
where $"PSD"_("float")^((k)) (f)$ is the floating-point precision PSD of sequence $k$ at frequency $f$,
$M$ is the number of independent sequences,
and $N_f$ is the number of non-negative frequency points.


The same procedure is then applied after encoding and decoding the floating-point trajectories using different codec resolutions.
For a given number of bins $R$,
the codec produces reconstructed trajectories from which the PSD and corresponding RMSE are computed relative to the reference PSD
$
  "RMSE"_"codec,ref"^((R)) = sqrt(1/(M N_f) sum_(f=1)^N_f sum_(k=1)^M ("PSD"_("codec")^((k,R))(f) - "PSD"_("reference")(f))^2)
$
The dependence of the $"RMSE"_"codec,ref"$ on the resolution is shown in the top panels of @fig-codec.
In addition,
the $"RMSE"$ between the codec and the floating-point PSD is evaluated.
$
  "RMSE"_"codec,float"^((R)) = sqrt(1/(M N_f) sum_(f=1)^N_f sum_(k=1)^M ("PSD"_("codec")^((k,R))(f) - "PSD"_("float")^((k))(f))^2)
$
This measure isolates the deviations introduced by the codec itself,
independently of sampling noise.
The $"RMSE"_"codec,float"$ should converge to the floating-point baseline as the resolution increases.

The bottom panels of @fig-codec demonstrate the scenario with the largest number of independent sequences considered in ACID 2: $M = 256$ and $"nseed" = 64$.
Even under these conditions,
the error introduced by the codec using $2^16$ bins remains significantly smaller than the intrinsic sampling error.
This comparison ensures that residual discrepancies are dominated by finite-sampling effects rather than by the discretization itself.

#figure(
  image("output/codec.svg"),
  caption: [
Codec validation.
Top panels: RMSE of the codec PSDs relative to the reference PSD as a function of resolution,
with the floating-point baseline (red dashed line)
and the production resolution ($2^16$ bins, red marker)
Bottom panels: RMSE of the codec PSDs relative to the floating-point PSDs.
  ],
) <fig-codec>

#bibliography("references.bib")
