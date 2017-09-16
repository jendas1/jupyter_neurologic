import glob
import os
import re
import subprocess
from collections import OrderedDict
from glob import glob, escape
from os.path import dirname

import holoviews as hv
import pandas as pd
from IPython.core.display import display_svg
from ipywidgets import interact
import ipywidgets as widgets

from neurologic.common import parse, extract_parameters
from neurologic import examples_transformer
from neurologic import template_transformer

NEUROLOGIC_JAR_PATH = os.path.join(os.path.dirname(__file__), "neurologic.jar")
RAW_RULES_PATH = "./.rules_raw.pl"
RAW_EXAMPLES_PATH = "./.examples_raw.pl"

_error_indexes = {"training": "trainError-AVG",
                  "training-max": "trainError-MAX",
                  "testing": "testError-AVG",
                  "testing-max": "testError-MAX"}


def _get_all_parameters(output_folder):
    all_parameters = OrderedDict()
    for name in glob(os.path.join(escape(output_folder), "learning_stats-fold*-restart*.*")):
        parameters = extract_parameters(name)
        for ind, params in enumerate(parameters):
            for key, value in params.items():
                all_parameters.setdefault(key, {"values": set(), "type": "dataset" if not ind else "learning"})[
                    "values"].add(value)
    all_parameters.setdefault("error type", {"type": "checking"})["values"] = _error_indexes.keys()
    return all_parameters


def kwargs_to_cli(**kwargs):
    return [f"--{key}={value.replace('_','-')}" for key, value in kwargs.items()]


def _execute_jar(jar_path, parameters):
    print(f"java -jar '{jar_path}'", " ".join(map(lambda x: f"{x}", parameters)))
    args = ["java", "-jar", jar_path, *parameters]
    # process = subprocess.Popen(args, stdout=subprocess.DEVNULL)
    # process.wait()
    process = subprocess.run(args)
    return process


def _get_output_folder(parameters):
    return os.path.join(".", "outputs", os.path.dirname(parameters["rules"]))


def run(rules_path, training_set_path, **kwargs):
    """
    Execute the learning phase. This function translates the arguments for Java neurologic.jar executable and calls it.
    BEWARE: The learning phase often takes a while to finish!

    :param rules_path: File with rules
    :param training_set_path: File with examples
    Keyword Arguments:
        activations <ACTIVATION>                      lambda-kappa
                                                         activation functions
                                                         (default: sig_sig)
        alldiff <arg>                            Differently named
                                                         variables in a single
                                                         rule must bind to
                                                         different constants
        batch                                          Enable batch
                                                            learning(RPROP)
                                                            (default: off)
        bottomUp <arg>                               Use bottom-up
                                                            grounder (from
                                                            Ondrej) instead of
                                                            top-down search
                                                            (default)
        cumulativeSteps <arg>                        Cumulative number of
                                                            learning steps
                                                            (default: 0 )
        debug <arg>                                Enable debug mode
                                                            (=detailed output)
        dropout <DROPOUT>                             dropout rate
                                                            (default: 0)
        drawing <arg>                               Enable picture
                                                            drawing/exporting
                                                            into ./images
        embeddings <arg>                             Enable/load
                                                            embeddings from a
                                                            predefined csv file
                                                            at
                                                            ./in/embeddings.csv
        folds <FOLDS>                                  Number of folds for
                                                            k-fold
                                                            cross-validation
                                                            (default: 1)
        grounding <GROUNDING>                         grounding variant
                                                            (default: avg)
        kappaAdaptiveOffset <kappaAdaptiveOffset>     Enable kappa offset
                                                            based on number of
                                                            input literals
                                                            (default: off)
        learning_epochs <EPOCHS>                      Number of learning
                                                            epochs before test
                                                            phase (default: 1)
        lambdaAdaptiveOffset <lambdaAdaptiveOffset>   Enable lambda offset
                                                            based on number of
                                                            input literals
                                                            (default: off)
        learning_rate <RATE>                          Learning rate for
                                                            backpropagation
                                                            (default: 0.05)
        learnDecay <arg>                             learning rate decay
                                                            over time (default: 0
                                                            )
        learning_steps <STEPS>                        Number of learning
                                                            steps before
                                                            resubstitution
                                                            (default: 10000)
        output <arg>                                 Results directory
        restart_count <RESTARTS>                      Number of restarts
                                                            (default: 1)
        saving <arg>                                saving the best
                                                            template after each
                                                            bp-step over all
                                                            examples (default: 1
                                                            )
        seed <SEED>                                   seed value (default:
                                                            1)
        SGD <arg>                                    Stochastic grdient
                                                            descend (default: 1)
        example_count <SIZE>                        Maximal count of
                                                            examples (default:
                                                            1000000)
        pretrained <PRETRAINED>                        File with pretrained
                                                            network template
        testSet <TEST-FILE>                         File with test
                                                            examples
        taskType <arg>                                TASKTYPE
        initialization <INITIALIZATION>               weight initialization
                                                         method (default:
                                                         longtail)

    :return: Path to the output folder where all information about the learning phase is.
    """
    parameters = kwargs
    with open(RAW_RULES_PATH, "w") as f:
        f.write(template_transformer.transform(open(rules_path, "r").read()))
    with open(RAW_EXAMPLES_PATH, "w") as f:
        f.write(examples_transformer.transform(open(training_set_path, "r").read()))
    parameters["examples"] = RAW_EXAMPLES_PATH
    parameters["rules"] = RAW_RULES_PATH
    _execute_jar(NEUROLOGIC_JAR_PATH, kwargs_to_cli(**parameters))
    return _get_output_folder(parameters)


def _stats_from_ser(base_path, fold, restart):
    data_path = os.path.join(base_path, f"learning_stats-fold{fold}-restart{restart}.ser")
    headers = open(os.path.join(base_path, "learning_statsNames.csv")).read().split(",")
    data = parse(open(data_path, 'rb'))
    df = pd.DataFrame(data[0]['data'])
    df = df.T
    df.columns = headers
    return df


def _load_statistics(output_folder: str):
    raw_stats = []
    raw_info = []
    for stats in glob(os.path.join(escape(output_folder), "learning_stats-fold*-restart*.*")):
        learning_parameters = {"fold": int(re.search(r"fold([0-9]+)", stats).group(1)),
                               "restart": int(re.search(r"restart([0-9]+)", stats).group(1))}
        if stats.endswith(".ser"):
            raw_stats.append(
                _stats_from_ser(dirname(stats), learning_parameters["fold"], learning_parameters['restart']))
        else:
            raw_stats.append(pd.read_csv(stats))
        raw_info.append(learning_parameters)
    return raw_stats, raw_info


def _stats_plot(raw_stats, raw_info, **kwargs):
    ind = dict(kwargs)
    error_type = ind.pop("error type")
    data = raw_stats[raw_info.index(ind)]
    return hv.Curve(data[_error_indexes[error_type]], kdims=[hv.Dimension('Epoch')], vdims=[hv.Dimension('Error')])


def plot_statistics(output_folder: str):
    """

    :param output_folder: Path to neurologic output folder
    :return:
    """
    raw_stats, raw_info = _load_statistics(output_folder)
    parameters = _get_all_parameters(output_folder)
    dimensions = [hv.Dimension(key, values=list(value['values'])) for key, value in parameters.items()]
    dmap = hv.DynamicMap(
        lambda *vals: _stats_plot(raw_stats, raw_info, **{key: vals[i] for i, key in enumerate(parameters.keys())}),
        kdims=dimensions)
    return dmap


def _display_neural_net_holoviews(output_folder: str, example_index: int):
    image_file = os.path.join(output_folder, "images", f"network β #{example_index} post learning.png")
    dot_file = os.path.join(output_folder, "images", f"network β #{example_index} post learning.dot")
    if not os.path.exists(image_file) or True:
        subprocess.run(["dot", "-Tpng", "-Gdpi=300", dot_file, "-o", image_file])
    return hv.RGB.load_image(image_file)


def _display_neural_net_svg(output_folder: str, example_index: int):
    image_file = os.path.join(output_folder, "images", f"network β #{example_index} post learning.svg")
    dot_file = os.path.join(output_folder, "images", f"network β #{example_index} post learning.dot")
    if not os.path.exists(image_file) or True:
        subprocess.run(["dot", "-Tsvg", dot_file, "-o", image_file])
    # Workaround for normal size
    svg_data = open(image_file, "r").read()
    svg_data = re.sub('<svg width="[0-9]+pt" height="[0-9]+pt"', '<svg width="100%" height="100%"', svg_data)
    return display_svg(svg_data, raw=True)


def _display_neural_nets_holoviews(output_folder: str):
    examples = range(len(list(glob(os.path.join(output_folder, "images", "network β #* post learning.dot")))))
    dimensions = [hv.Dimension("Example", values=examples)]
    return hv.DynamicMap(
        lambda index: _display_neural_net_holoviews(output_folder, index),
        kdims=dimensions
    )


def _display_neural_nets_ipywidgets(output_folder: str):
    examples_count = len(list(glob(os.path.join(output_folder, "images", "network β #* post learning.dot"))))
    return interact(lambda example_number: _display_neural_net_svg(output_folder, example_number),
                    example_number=widgets.IntSlider(value=0, min=0, max=examples_count - 1, step=1))


def display_neural_nets(output_folder: str):
    """
    Process the
    :param output_folder: Path to neurologic output folder
    """
    return _display_neural_nets_ipywidgets(output_folder)


def learned_template(output_folder: str) -> str:
    """
    :param output_folder: Path to neurologic output folder
    :return: Learned template in a NeuroLogic format
    """
    # TODO : Pick best fold
    return template_transformer.transform_result(open(os.path.join(output_folder, "learned-fold0.txt"), "r").read())
