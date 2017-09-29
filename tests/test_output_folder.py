from neurologic.neurologic import _get_output_folder


def test_output_folder_name():
    assert _get_output_folder("./hello/rules.pl") == "./outputs/hello/"


def test_output_file_name():
    assert _get_output_folder("hello.pl") == "./outputs/hello/"


def test_output_unnamed_name():
    assert _get_output_folder("rules.pl") == "./outputs/unnamed/"


def test_priority_hints():
    assert _get_output_folder("sample_tasks/scrabble_rules.pl") == "./outputs/scrabble/"
