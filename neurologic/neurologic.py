import glob
import os
import re
import subprocess
from collections import OrderedDict
from glob import glob, escape
from os.path import dirname

import holoviews as hv
import pandas as pd

from neurologic.common import parse, extract_parameters
from neurologic.examples_unfolder import unfold_examplesf
from neurologic.template_transformer import transform

NEUROLOGIC_JAR_PATH = os.path.join(os.path.dirname(__file__), "neurologic.jar")
RAW_RULES_PATH = "./.rules_raw.pl"
RAW_EXAMPLES_PATH = "./.examples_raw.pl"

error_indexes = {"training": "trainError-AVG",
                 "training-max": "trainError-MAX",
                 "testing": "testError-AVG",
                 "testing-max": "testError-MAX"}


def get_all_parameters(output_folder):
    all_parameters = OrderedDict()
    for name in glob(escape(output_folder) + "learning_stats-fold*-restart*.*"):
        parameters = extract_parameters(name)
        for ind, params in enumerate(parameters):
            for key, value in params.items():
                all_parameters.setdefault(key, {"values": set(), "type": "dataset" if not ind else "learning"})[
                    "values"].add(value)
    all_parameters.setdefault("error type", {"type": "checking"})["values"] = error_indexes.keys()
    return all_parameters


def kwargs_to_cli(**kwargs):
    return [f"--{key}={value}" for key, value in kwargs.items()]


def execute_jar(jar_path, parameters):
    print(f"java -jar '{jar_path}'", " ".join(map(lambda x: f"{x}", parameters)))
    args = ["java", "-jar", jar_path, *parameters]
    # process = subprocess.Popen(args, stdout=subprocess.DEVNULL)
    # process.wait()
    process = subprocess.run(args)
    return process


def get_output_folder(parameters):
    return "./outputs/" + os.path.dirname(parameters["rules"]) + "/"


def run(rules_path, training_set_path, **kwargs):
    parameters = kwargs
    with open(RAW_RULES_PATH, "w") as f:
        f.write(transform(open(rules_path, "r").read()))
    unfold_examplesf(training_set_path, RAW_EXAMPLES_PATH)
    parameters["examples"] = RAW_EXAMPLES_PATH
    parameters["rules"] = RAW_RULES_PATH
    execute_jar(NEUROLOGIC_JAR_PATH, kwargs_to_cli(**parameters))
    return get_output_folder(parameters)


def stats_from_ser(base_path, fold, restart):
    data_path = base_path + f"/learning_stats-fold{fold}-restart{restart}.ser"
    headers = open(base_path + "/learning_statsNames.csv").read().split(",")
    data = parse(open(data_path, 'rb'))
    df = pd.DataFrame(data[0]['data'])
    df = df.T
    df.columns = headers
    return df


def load_statistics(output_folder):
    raw_stats = []
    raw_info = []
    for stats in glob(escape(output_folder) + "learning_stats-fold*-restart*.*"):
        learning_parameters = {"fold": int(re.search(r"fold([0-9]+)", stats).group(1)),
                               "restart": int(re.search(r"restart([0-9]+)", stats).group(1))}
        if stats.endswith(".ser"):
            raw_stats.append(
                stats_from_ser(dirname(stats), learning_parameters["fold"], learning_parameters['restart']))
        else:
            raw_stats.append(pd.read_csv(stats))
        raw_info.append(learning_parameters)
    return raw_stats, raw_info


def _stats_plot(raw_stats, raw_info, **kwargs):
    ind = dict(kwargs)
    error_type = ind.pop("error type")
    data = raw_stats[raw_info.index(ind)]
    return hv.Curve(data[error_indexes[error_type]])


def plot_statistics(output_folder):
    raw_stats, raw_info = load_statistics(output_folder)
    parameters = get_all_parameters(output_folder)
    dimensions = [hv.Dimension(key, values=list(value['values'])) for key, value in parameters.items()]
    dmap = hv.DynamicMap(
        lambda *vals: _stats_plot(raw_stats, raw_info, **{key: vals[i] for i, key in enumerate(parameters.keys())}),
        kdims=dimensions)
    return dmap


def learned_template(output_folder):
    # TODO : Pick best fold
    return open(os.path.join(output_folder, "learned-fold0.txt"), "r").read()
