import re
import sys

rule_match = r"(.+?)(\(.+?\))?"
rule_pattern = r"(<?-?\d+\.?\d*>?)[ \t]+(.+?)(\(.*?\))?[ \t]+:-[ \t]+(.+)?\.[ \t]*(?:\n|$)"


def unfold_examples(rule_str):
    output = []
    for weight, head_name, head_variables, tail in re.findall(rule_pattern, rule_str):
        if head_variables == "()":
            head_variables = "(a)"
        output.append(f"{weight} {tail},final{head_name}{head_variables}.")
    output_str = "\n".join(output)
    return output_str


def unfold_examplesf(examples_path, output_path):
    rule_str = open(examples_path).read()
    output_str = unfold_examples(rule_str)
    open(output_path, "w").write(output_str)


if __name__ == "__main__":
    unfold_examplesf(sys.argv[1], sys.argv[2])
