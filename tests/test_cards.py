from neurologic import run, learned_template
from neurologic.statistics import plot_statistics
import sys

if __name__ == '__main__':
    output = run(sys.argv[1] if len(sys.argv) >= 2 else "rules.pl",
                 sys.argv[2] if len(sys.argv) >= 3 else "training_set.pl", **{"learning-rate": "0.001"})
