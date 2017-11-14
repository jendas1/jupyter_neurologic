import glob
import os
import subprocess
from collections import OrderedDict
from glob import glob, escape

import holoviews as hv
import ipywidgets as widgets
from IPython.core.display import display_svg
from ipywidgets import interact

from neurologic import examples_transformer
from neurologic import template_transformer
from neurologic.common import extract_parameters, _svg_from_dot

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
    return [f"--{key.replace('_','-')}={value}" for key, value in kwargs.items()]


def _execute_jar(jar_path, parameters):
    print(f"java -jar '{jar_path}'", " ".join(map(lambda x: f"{x}", parameters)))
    args = ["java", "-jar", jar_path, *parameters]
    # process = subprocess.Popen(args, stdout=subprocess.DEVNULL)
    # process.wait()
    process = subprocess.run(args)
    return process


def _get_output_folder(rule_path):
    """
    Return location of output folder based on rule name.
    Same implementation can be found also in Java Neurologic.
    """
    folder_name = os.path.basename(os.path.dirname(rule_path))
    file_name = os.path.basename(rule_path).split(".")[0]
    rule_names = {"rules", "template"}
    if folder_name not in [".", ""] and file_name in rule_names:
        output_folder = folder_name
    elif any(map(lambda name: file_name.endswith("_" + name), rule_names)):
        output_folder = file_name.rsplit("_", 1)[0]
    elif file_name not in rule_names:
        output_folder = file_name
    else:
        output_folder = "unnamed"
    return os.path.join(".", "outputs", output_folder, "")


def run(rules_path, training_set_path, **kwargs):
    """
    Execute the learning phase. This function translates the arguments for Java neurologic.jar executable and calls it.
    BEWARE: The learning phase often takes a while to finish!

    :param rules_path: File with rules
    :param training_set_path: File with examples
    Optional arguments:
    :param aggregation: Aggregation variant (defalut avg)
    All Keyword Arguments:
        activations <ACTIVATION>                      lambda-kappa
                                                         activation functions
                                                         (default: id_id)
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
        aggregation <AGGREGATION_TYPE>                 Aggregation variant
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
    if "output" not in parameters:
        parameters["output"] = _get_output_folder(rules_path)

    # Global option
    if "activations" not in parameters:
        parameters["activations"] = "id_id"
    renamed_keys = {
        "aggregation": "grounding"
    }
    parameters = {key if key not in renamed_keys else renamed_keys[key]: value for key, value in parameters.items()}

    _execute_jar(NEUROLOGIC_JAR_PATH, kwargs_to_cli(**parameters))
    return parameters["output"]


def _display_neural_net_holoviews(output_folder: str, example_index: int):
    image_file = os.path.join(output_folder, "images", f"network β #{example_index} post learning.png")
    dot_file = os.path.join(output_folder, "images", f"network β #{example_index} post learning.dot")
    if not os.path.exists(image_file) or True:
        subprocess.run(["dot", "-Tpng", "-Gdpi=300", dot_file, "-o", image_file])
    return hv.RGB.load_image(image_file)


def _display_neural_net_svg(output_folder: str, example_index: int):
    dot_file = os.path.join(output_folder, "images", f"network β #{example_index} post learning.dot")
    return display_svg(_svg_from_dot(dot_file), raw=True)


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
