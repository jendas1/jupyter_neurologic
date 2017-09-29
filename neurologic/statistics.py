import glob
import os
import re
from glob import escape, glob
from os.path import dirname

import holoviews as hv
import pandas as pd

from neurologic.common import parse
from neurologic.neurologic import _error_indexes, _get_all_parameters


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