from dataclasses import dataclass


@dataclass
class InputVariable:
    """
    Class to generate code related input variable and it's default value

    :param variable_name: variable name
    :param value: variable value
    :param value_type: variable objec type

    Attributes:
        default_args: ex: ``a = 1``
        parser_body: ex: ``parser.add_arguemnt('--a', default=1, type=int)``
        parser_args: ex: ``a = args.a``

    """

    def __init__(
        self, variable_name, value, value_type, typing_info=None
    ) -> None:
        self.variable_name = variable_name
        self.value = value
        self.value_type = value_type.__name__
        # placeholder for future support to allow user passing typing info
        self.typing_info = typing_info
        self.default_args = f"{self.variable_name} = {repr(self.value)}"
        self.parser_body = f"parser.add_argument('--{self.variable_name}', type={self.value_type}, default={repr(self.value)})"
        self.parser_args = f"{self.variable_name} = args.{self.variable_name}"
