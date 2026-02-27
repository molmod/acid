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

// Load the cases to be reported from sys.inputs
#let cases = yaml("cases.yaml")

// Title page
#align(center)[
  #text(size: 24pt)[
    *AutoCorrelation Integral Drill (ACID):* \
    Testing Overview
  ]

  Gözdenur Toraman,#super[†] Dieter Fauconnier,#super[†‡] and Toon Verstraelen#super[✶¶]

  † Soete Laboratory, Ghent University, Technologiepark-Zwijnaarde 46, 9052 Ghent, Belgium\
  ‡ FlandersMake\@UGent, Core Lab MIRO, 3001 Leuven, Belgium\
  ¶ Center for Molecular Modeling (CMM), Ghent University, Technologiepark-Zwijnaarde
  46, B-9052, Ghent, Belgium

  ✶E-mail: #link("mailto:toon.verstraelen@ugent.be", "toon.verstraelen@ugent.be")

  Version #read("git-version.txt").trim() #read("git-date.txt").trim()
]

This document summarizes the performance of different software packages, versions and their settings
in estimating the autocorrelation integral using the ACID test set.
When applicable, the performance for the estimation of the exponential correlation time is also reported.

#outline()

= Description of Test Cases

The following test cases were benchmarked with the ACID test set:

#for (case, info) in cases.pairs() [
  #raw(case)
  #block(inset: (left: 12pt, top: 3pt, bottom: 3pt))[
    *#info.program* version *#info.version* with the following settings:
    #for setting in info.settings [
      - #eval("[" + setting +"]")
    ]
  ]
]

= Definitions of Summary Statistics

The two tables below contain summary statistics, averaged over all kernels considered for a specific combination software tool, version and settings.
These statistics are defined as follows:

#include "summary_stats.typ"

= Summary Statistics

#let summaries = (
  ("acint", "Autocorrelation Integral"),
  ("corrtime_exp", "Exponential Correlation Time"),
)

#for (field, label) in summaries {
  align(center, box(inset: 6pt)[
    #set par(spacing: 0.5em, leading: 0.5em)
    #align(center)[*Summary statistics for the #label*]
    #table(
      columns: (2.5fr,) + (1fr,)*9,
      align: center,
      stroke: none,
      table.hline(y: 1, stroke: black),
      table.header(
        [*Test case*],
        [Kernels],
        [compl.],
        [$log_10 A$],
        [$c_N$],
        [$c_M$],
        [$chevron.l "uc" chevron.r$],
        [$"rms"_"uc"$],
        [$chevron.l "bias" chevron.r$],
        [$"rms"_"bias"$]
      ),
      ..for case in cases.keys() {
        let config = json(strfmt("reports/{}/report_config.json", case))
        if (field == "corrtime_exp" and not config.has_corrtime_exp) {
          continue
        }
        let sums = (:)
        for kernel in config.kernels {
          let stats = json(strfmt("reports/{}/{}_{}_stats.json", case, kernel, field))
          for (key, value) in stats.pairs() {
            if key in sums {
              sums.at(key) += value
            } else {
              sums.insert(key, value)
            }
          }
        }
        for key in sums.keys() {
          sums.at(key) /= config.kernels.len()
        }
        (
          [#case],
          [$#config.kernels.len()$],
          [$#eval(strfmt("{:.0}", sums.frac_complete * 100))$],
          [$#eval(strfmt("{:.2}", sums.log10_prefac))$],
          [$#eval(strfmt("{:.2}", sums.coeff_nseq))$],
          [$#eval(strfmt("{:.2}", sums.coeff_nstep))$],
          [$#eval(strfmt("{:.0}", sums.mean_uc * 100))$],
          [$#eval(strfmt("{:.0}", sums.rms_uc * 100))$],
          [$#eval(strfmt("{:.0}", sums.mean_bias * 100))$],
          [$#eval(strfmt("{:.0}", sums.rms_bias * 100))$],
        )
      }
    )
  ])
}
