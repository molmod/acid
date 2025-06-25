#import "@preview/oxifmt:1.0.0": strfmt

#set page("a4", margin: 2cm, numbering: "1")
#show link: set text(blue)
#set table.cell(breakable: false)

#align(center)[
  #text(size: 24pt)[
    *Validation of the STable AutoCorrelation Integral Estimator (STACIE)
    Using The AutoCorrelation Integral Drill (ACID) Test Set* \
    model: lorentz(0.1)
  ]

  Gözdenur Toraman,#super[†] Dieter Fauconnier,#super[†‡] and Toon Verstraelen#super[✶¶]

  † Soete Laboratory, Ghent University, Technologiepark-Zwijnaarde 46, 9052 Ghent, Belgium\
  ‡ FlandersMake\@UGent, Core Lab EEDT-MP, 3001 Leuven, Belgium\
  ¶ Center for Molecular Modeling (CMM), Ghent University, Technologiepark-Zwijnaarde
  46, B-9052, Ghent, Belgium

  ✶E-mail: #link("mailto:toon.verstraelen@ugent.be", "toon.verstraelen@ugent.be")

  Version #read("gitline.txt")
]

#set heading(numbering: "1.1.")
#outline()
#pagebreak()

= Description of Figures and Tables

The following sections contain figures and tables with the same type of results in each section,
but computed for different kernels.
All figures and tables are labeled with a letter and are explained here.
For a full discussion of the results, we refer to the STACIE paper: TODO ADD CITATION.

#set enum(numbering: "(a)")

+ *Illustration of input data.*
  - Left: an example input sequences (first 100 steps).
  - Center: the sampling autocorrelation function (ACF)
    of the input data ($N=1024$, $M=256$, purple line)
    and the analytical ACF (dashed line).
  - Right: the sampling power spectral density (PSD)
    of the input data ($N=1024$, $M=256$, turquoise line)
    and the analytical PSD (dashed line).
+ *Scaling of uncertainty of the autocorrelation integral with input data.*
  - The slope of the slanted gray lines indicates the ideal scaling of the uncertainty
    (proportional to $1/sqrt(N M)$).
    The spacing between the lines corresponds to a factor of 2 in the uncertainty,
    the ideal case when changing $N$ by a factor of 4.
  - A square represents the standard deviations over 64 repetitions of STACIE's estimate
    of the autocorrelation integral for a specific combination of $N$ and $M$.
  - The dotted lines represent the corresponding predicted uncertainties.
+ *Assessment of the error estimate of the autocorrelation integral.*
  - The square blocks show the ratio of the standard deviation of the STACIE estimate
    and the RMS value of the predicted uncertainty, over 64 repetitions.
    This value is ideally 100%.
  - The dots show the ratio of the mean error
    and the RMS value of the predicted uncertainty, over 64 repetitions.
    This value is ideally 0%.
+ *Scaling of the uncertainty of the exponential correlation time with input data.*
  - This figure follows the same convention as in (b),
    but shows results for the uncertainty of the exponential correlation time.
+ *Assessment of the error estimate of the exponential correlation time.*
  - This figure follows the same convention as in (c),
    but shows results for the uncertainty of the exponential correlation time.
+ *Sensitivity of the autocorrelation integral to the cutoff frequency.*
  - This plot shows how the autocorrelation integral correlates with
    the effective number of points used in the fit (top) and the cutoff frequency (bottom).
  - Results are shown only for the $M=64$.
  - The color code for different $N$
    corresponds to the legends shown in figures (b), (c), (d) and (e).
+ *Sensitivity of the exponential correlation time to the cutoff frequency.*
  - The same conventions as in (f) apply,
    but this figure shows results for the exponential correlation time.
+ *Sanity check counts for the effective number of points*
  - Number of test cases for each combination of $N$ and $M$
    where the effective number of points used in the fit is below $20 P = 40$.
+ *Sanity check counts for the regression cost z-score*
  - Number of test cases for each combination of $N$ and $M$
    where the z-score of the regression cost exceeds 2.
+ *Sanity check counts for the cutoff criterion z-score*
  - Number of test cases for each combination of $N$ and $M$
    where the z-score of the cutoff criterion exceeds 2.

#let kernels = json("kernels.json")
#for (kernel, models) in kernels {
  if "lorentz" in models {
    heading(level: 1, [Kernel #kernel])
    v(1em)
    box(
      grid(
        columns: 2,
        gutter: 6pt,
        align: center,
        grid.cell(
            colspan: 2,
            [*(a) Illustration of input data*],
        ),
        grid.cell(
            colspan: 2,
            image("figures/plot_acid_sequences_" + kernel + "_nstep01024_nseq0256.svg"),
        ),
        [*(b) Scaling of uncertainty of the autocorrelation integral with input data*],
        [*(c) Assessment of the error estimate of the autocorrelation integral*],
        image("figures/plot_acint_scaling_" + kernel + "_lorentz.svg"),
        image("figures/plot_acint_ratios_" + kernel + "_lorentz.svg"),
        [*(d) Scaling of uncertainty of the exponential correlation time with input data*],
        [*(e) Assessment of the error estimate of the exponential correlation time*],
        image("figures/plot_corrtime_exp_scaling_" + kernel + "_lorentz.svg"),
        image("figures/plot_corrtime_exp_ratios_" + kernel + "_lorentz.svg"),
      )
    )

    pagebreak()

    box(
      grid(
        columns: 2,
        gutter: 6pt,
        align: center,
        [*(f) Sensitivity of the autocorrelation integral to the cutoff frequency*],
        [*(g) Sensitivity of the exponential correlation time to the cutoff frequency*],
        image("figures/plot_cutoff_acint_" + kernel + "_nseq0064_lorentz.svg"),
        image("figures/plot_cutoff_corrtime_exp_" + kernel + "_nseq0064_lorentz.svg"),
      )
    )

    // tables

    align(center, text(weight: "bold")[
      (h) Sanity check counts for the effective number of points
    ])
    let neff_data = csv("tables/" + kernel + "_lorentz_neff.csv").flatten()
    table(
      columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
      stroke: (x, y) => if y == 0 {
        (bottom: 0.7pt + black)
      },
      ..neff_data.map(x => [#eval(x)]),
    )

    align(center, text(weight: "bold")[
      (i) Sanity check counts for the regression cost z-score
    ])
    let cost_zscore_data = csv("tables/" + kernel + "_lorentz_cost_zscore.csv").flatten()
    table(
      columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
      stroke: (x, y) => if y == 0 {
        (bottom: 0.7pt + black)
      },
      ..cost_zscore_data.map(x => [#eval(x)]),
    )

    align(center, text(weight: "bold")[
      (j) Sanity check counts for the cutoff criterion z-score
    ])
    let criterion_zscore_data = csv("tables/" + kernel + "_lorentz_criterion_zscore.csv").flatten()
    table(
      columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
      stroke: (x, y) => if y == 0 {
        (bottom: 0.7pt + black)
      },
      ..criterion_zscore_data.map(x => [#eval(x)]),
    )
  }
}
