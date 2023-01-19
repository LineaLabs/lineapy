from dataclasses import dataclass


@dataclass
class InputVariable:
    """
    Class to generate code related input variable and it's default value

    Attributes
    ----------
    variable_name:
        variable name
    value:
        variable value
    value_type:
        variable object type
    default_args:
        assignment of variable to a default value
        ex: ``a = 1``
    parser_body:
        code block that uses python parser library to get a input variable from CLI.
        ex: ``parser.add_argument('--a', default=1, type=int)``
    parser_args:
        code block that unpacks input variable from args.
        ex: ``a = args.a``

    """

    def __init__(self, variable_name, value, value_type) -> None:
        self.variable_name = variable_name
        self.value = value
        self.value_type = value_type.__name__
        self.default_args = f"{self.variable_name} = {repr(self.value)}"
        self.parser_body = f"parser.add_argument('--{self.variable_name}', type={self.value_type}, default={repr(self.value)})"
        self.parser_args = f"{self.variable_name} = args.{self.variable_name}"
