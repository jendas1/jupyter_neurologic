from neurologic import run, plot_statistics, learned_template
import sys

output = run(sys.argv[1] if len(sys.argv) >= 2 else "rules.pl",
             sys.argv[2] if len(sys.argv) >= 3 else "training_set.pl", **{"learning-rate": "0.001"})
