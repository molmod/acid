#import "@preview/oxifmt:1.0.0": strfmt

// General layout settings
#set page("a4", margin: 2cm, numbering: "1")
#show link: set text(blue)
#set table.cell(breakable: false)
#set heading(numbering: "1.")
#show heading: it => {
  if (counter(heading).get().at(0) >= 1) { pagebreak() }
  it
}

// This is a template for the detailed report of the ACID test cases
// for a given combination of software tool, version and settings.
// The parameters are read from the config JSON file passed through sys.inputs.

#let config = if "config" in sys.inputs {
  json(sys.inputs.at("config"))
} else {
  (
    "has_corrtime_exp": true,
    "has_neff": true,
    "has_mcmap": false,
    "case": "stacie_v1.2.1_lorentz",
    "kernels": ("exp1w",),
    "npar": 3,
  )
}

// Title page
#align(center)[
  #text(size: 24pt)[
    *AutoCorrelation Integral Drill (ACID):* \
    test case "#config.case"
  ]

  Gözdenur Toraman,#super[†] Dieter Fauconnier,#super[†‡] and Toon Verstraelen#super[✶¶]

  † Soete Laboratory, Ghent University, Technologiepark-Zwijnaarde 46, 9052 Ghent, Belgium\
  ‡ FlandersMake\@UGent, Core Lab MIRO, 3001 Leuven, Belgium\
  ¶ Center for Molecular Modeling (CMM), Ghent University, Technologiepark-Zwijnaarde
  46, B-9052, Ghent, Belgium

  ✶E-mail: #link("mailto:toon.verstraelen@ugent.be", "toon.verstraelen@ugent.be")

  Version #read("git-version.txt").trim() #read("git-date.txt").trim()
]

#let info = yaml("cases.yaml").at(config.case)

This document contains detailed results for the performance on the ACID test set
of  *#info.program* version *#info.version* with the following settings:
#for setting in info.settings [
  - #eval("[" + setting +"]")
]

#outline()

= Description of Figures and Tables

The following sections contain figures and tables with the same type of results in each section,
but computed for different kernels.
All figures and tables are labeled with a letter and are explained below.
For a full discussion of the results, we refer to the STACIE paper. @Toraman2025

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
    Lower values mean that STACIE's predictions have a smaller spread than the predicted uncertainty.
  - The dots show the ratio of the mean error
    and the RMS value of the predicted uncertainty, over 64 repetitions.
    This value is ideally 0%.
#if config.has_corrtime_exp [
+ *Scaling of the uncertainty of the exponential correlation time with input data.*
  - This figure follows the same convention as figure (b),
    but shows results for the uncertainty of the exponential correlation time.
+ *Assessment of the error estimate of the exponential correlation time.*
  - This figure follows the same convention as figure (c),
    but shows results for the uncertainty of the exponential correlation time.
]
#if config.has_mcmap [
+ *Validation of the Maximum A Posteriori (MAP) estimate.*
  - The MAP estimate for the autocorrelation integral
    (blue, cross is the maximizer, ellipse is the 2-sigma volume).
  - The Monte Carlo samples of the posterior distribution
    of the model parameters (black points).
  - The mean and covariance of the Monte Carlo samples
    (red, cross is the mean, ellipse is the 2-sigma volume).
]
#if config.has_neff [
+ *Sensitivity of the autocorrelation integral to the cutoff frequency.*
  - This plot shows how the autocorrelation integral correlates with
    the effective number of points used in the fit (top) and the cutoff frequency (bottom).
  - Results are shown only for the $M=64$.
  - The color code for different $N$ is the same is in the error scaling plots.
#if config.has_corrtime_exp [
+ *Sensitivity of the exponential correlation time to the cutoff frequency.*
  - The same conventions as in the previous figure apply.
    The only difference is that this figure shows results for the exponential correlation time.
]
+ *Number of successful test cases*
  (Failures are typically due to not finding any cutoff frequency with acceptable results.)
+ *Sanity check counts for the effective number of points*
  - Number of test cases for each combination of $N$ and $M$
    where the effective number of points used in the fit is below $20 P = #config.npar$.
+ *Sanity check counts for the regression cost z-score*
  - Number of test cases for each combination of $N$ and $M$
    where the z-score of the regression cost exceeds 2.
+ *Sanity check counts for the cutoff criterion z-score*
  - Number of test cases for each combination of $N$ and $M$
    where the z-score of the cutoff criterion exceeds 2.
]

#for kernel in config.kernels {
  heading(level: 1, [Kernel #kernel])
  v(1em)

  // Helper to create labeled panels
  let ic = counter("panel")
  let panel(it) = block[
    #ic.step()
    #text(weight: "bold")[
      #context ic.display("(a)")
      #it
    ]
  ]

  // Compact paragraph layout inside the grid
  set par(spacing: 0.5em, leading: 0.5em)
  set grid.cell(breakable: false)

  grid(
    columns: 2,
    gutter: 6pt,
    align: center,
    grid.cell(colspan: 2)[
      #panel[Illustration of input data]
      #image(strfmt("reports/shared/subset_{}.svg", kernel))
    ],
    [
      #panel[Scaling of uncertainty of the autocorrelation integral with input data]
      #image(strfmt("reports/{}/{}_acint_scaling.svg", config.case, kernel))
    ],
    [
      #panel[Assessment of the error estimate of the autocorrelation integral]
      #image(strfmt("reports/{}/{}_acint_ratios.svg", config.case, kernel))
    ],
    ..if config.has_corrtime_exp {(
      [
        #panel[Scaling of uncertainty of the exponential correlation time with input data]
        #image(strfmt("reports/{}/{}_corrtime_exp_scaling.svg", config.case, kernel))
      ],
      [
      #panel[Assessment of the error estimate of the exponential correlation time]
      #image(strfmt("reports/{}/{}_corrtime_exp_ratios.svg", config.case, kernel))
      ],
    )},
    ..if config.has_mcmap {([
      #panel[Validation of the Maximum A Posteriori (MAP) estimate]
      #image(strfmt("reports/{}/{}_mcmap.svg", config.case, kernel))
    ],)},
    ..if config.has_neff {([
      #panel[Scaling of (uncertainty of) the autocorrelation integral with input data]
      #image(strfmt("reports/{}/{}_acint_cutoff.svg", config.case, kernel))
    ],)},
    ..if (config.has_neff and config.has_corrtime_exp) {([
      #panel[Scaling of (uncertainty of) the exponential correlation time with input data]
      #image(strfmt("reports/{}/{}_corrtime_exp_cutoff.svg", config.case, kernel))
    ],)},
    ..if config.has_neff {
      // tables
      let table_cases = (
        ("ncomplete", "Number of completed test cases"),
        ("neff", "Sanity check counts for the effective number of points"),
        ("cost_zscore", "Sanity check counts for the regression cost z-score"),
        ("criterion_zscore", "Sanity check counts for the cutoff criterion z-score"),
      )
      (..for (field, label) in table_cases {
        (grid.cell(colspan: 2)[
          #panel[#label]
          #let data = csv(strfmt("reports/{}/{}_{}.csv", config.case, kernel, field)).flatten()
          #table(
            columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
            stroke: none,
            table.hline(y: 1, stroke: black),
            ..data.map(x => [#eval(x)]),
          )
        ],)
      },)
    },
  )
}

= Summary Statistics

Definition of the summary statistics, which are computed for the autocorrelation integral
and, if applicable, the exponential correlation time:

#include "summary_stats.typ"

#let summaries = (
  ("acint", "Autocorrelation Integral"),
)
#if config.has_corrtime_exp {
  summaries.push(("corrtime_exp", "Exponential Correlation Time"))
}

#for (field, label) in summaries {
  align(center, box(inset: 6pt)[
    #set par(spacing: 0.5em, leading: 0.5em)
    #align(center)[*Summary statistics for the #label*]
    #table(
      columns: (1fr,)*9,
      align: center,
      stroke: none,
      table.hline(y: 1, stroke: black),
      table.header(
        [*Kernel*],
        [compl.],
        [$log_10 A$],
        [$c_N$],
        [$c_M$],
        [$chevron.l "uc" chevron.r$],
        [$"rms"_"uc"$],
        [$chevron.l "bias" chevron.r$],
        [$"rms"_"bias"$]
      ),
      ..for kernel in config.kernels {
        let stats = json(strfmt("reports/{}/{}_{}_stats.json", config.case, kernel, field))
        (
          [#kernel],
          [$#eval(strfmt("{:.0}", stats.frac_complete * 100))$],
          [$#eval(strfmt("{:.2}", stats.log10_prefac))$],
          [$#eval(strfmt("{:.2}", stats.coeff_nseq))$],
          [$#eval(strfmt("{:.2}", stats.coeff_nstep))$],
          [$#eval(strfmt("{:.0}", stats.mean_uc * 100))$],
          [$#eval(strfmt("{:.0}", stats.rms_uc * 100))$],
          [$#eval(strfmt("{:.0}", stats.mean_bias * 100))$],
          [$#eval(strfmt("{:.0}", stats.rms_bias * 100))$],
        )
      }
    )
  ])
}

#bibliography("references.bib")
