- *Kernel*: the kernel used to generate the test data.
- *compl.*: fraction of completed test cases (in %, ideally 100).
- A model is fitted to the relative standard deviation (see scaling plots) of the form
  $
    log_10 ("rel. std.") = log_10 A - c_N log_10 N - c_M log_10 M
  $
  where $N$ is the sequence length and $M$ the number of sequences.
  The fitted parameters of this model are reported below.
  Ideally these parameters are:
  - $log_10 A$: prefactor (lower is better)
  - $c_N$: coefficient for the dependence on $N$ (higher is better, ideally 0.5)
  - $c_M$: coefficient for the dependence on $M$ (higher is better, ideally 0.5)
- The ratios of the standard deviation of the ACID estimate
  and the RMS value of the predicted uncertainty (in %)
  for different value of $N$ and $M$ are reported as:
  - $chevron.l "uc" chevron.r$: mean value (ideally 100).
  - $"rms"_"uc"$: root mean square (RMS) deviation from 100 (ideally 0).
- The ratios of the mean error of the ACID estimate
  and the RMS value of the predicted uncertainty (in %)
  for different value of $N$ and $M$ are reported as:
  - $chevron.l "bias" chevron.r$: mean value (ideally 0).
  - $"rms"_"bias"$: root mean square (RMS) deviation from 0 (ideally 0).
