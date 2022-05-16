from lineapy.plugins import utils


def test_slugify() -> None:
    """
    Taken from https://github.com/django/blob/master/tests/utils_tests/test_text.py
    """
    items = (
        # given - expected - Unicode?
        ("Hello, World!", "hello_world", False),
        ("spam & eggs", "spam_eggs", False),
        (" multiple---dash and  space ", "multiple_dash_and_space", False),
        ("\t whitespace-in-value \n", "whitespace_in_value", False),
        ("underscore_in-value", "underscore_in_value", False),
        ("__strip__underscore-value___", "strip__underscore_value", False),
        ("--strip-dash-value---", "strip_dash_value", False),
        ("__strip-mixed-value---", "strip_mixed_value", False),
        ("_ -strip-mixed-value _-", "strip_mixed_value", False),
        ("spam & ıçüş", "spam_ıçüş", True),
        ("foo ıç bar", "foo_ıç_bar", True),
        ("    foo ıç bar", "foo_ıç_bar", True),
        ("你好", "你好", True),
        ("İstanbul", "istanbul", True),
    )
    for value, output, is_unicode in items:
        assert utils.slugify(value, allow_unicode=is_unicode) == output
