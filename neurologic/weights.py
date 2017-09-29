import os
from typing import Union

import pandas as pd
from lark import Tree

from neurologic import FixZeroArity, neurologic_parser, ToCodeTransformer
from neurologic.common import parse


def prettify_rule(rule: Tree):
    return FixZeroArity().restore(rule)


def weights_from_ser(base_path: str, fold: Union[str, int], restart: Union[str, int]) -> pd.DataFrame:
    """
    Load weights from .ser format.
    :param base_path: Path to neurologic output folder
    :param fold: Fold number
    :param restart: Restart number
    :return:
    """
    data_path = os.path.join(base_path, f"weightsHistory-fold{fold}-restart{restart}.ser")
    headers_table = pd.read_csv(os.path.join(base_path, "weightNames.csv"))
    rules = neurologic_parser.parse(open(os.path.join(base_path, "rules.pl")).read())
    new_columns = []
    for column in headers_table.columns:
        try:
            col_rule = neurologic_parser.parse(column)[0]
            for line in rules.children:
                if line.data == "rule" and line["head"] == col_rule["body"][0]:
                    col_rule["body"] = line["body"]
            new_columns.append(ToCodeTransformer().transform(prettify_rule(col_rule)))
        except:
            new_columns.append(column)

    data = parse(open(data_path, 'rb'))
    df = pd.DataFrame(data[0]['data'])
    df.columns = new_columns
    return df