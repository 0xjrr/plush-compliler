from dataclasses import dataclass, field
from typing import List, Union

@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    declarations: List[Node]

@dataclass
class FunctionDeclaration(Node):
    name: str
    parameters: List['Parameter']
    return_type: str
    body: 'StatementBlock'

@dataclass
class VariableDeclaration(Node):
    var_type: str
    name: str
    var_kind: str  # 'val' or 'var'
    data_type: str
    value: 'Expression'

@dataclass
class Parameter(Node):
    name: str
    type: str

@dataclass
class StatementBlock(Node):
    statements: List['Statement']

@dataclass
class IfStatement(Node):
    condition: 'Expression'
    then_block: StatementBlock
    else_block: Union[StatementBlock, None]

@dataclass
class WhileStatement(Node):
    condition: 'Expression'
    body: StatementBlock

@dataclass
class AssignmentStatement(Node):
    target: str
    value: 'Expression'

@dataclass
class ReturnStatement(Node):
    value: 'Expression'

@dataclass
class BinaryExpression(Node):
    operator: str
    left: 'Expression'
    right: 'Expression'

@dataclass
class UnaryExpression(Node):
    operator: str
    operand: 'Expression'

@dataclass
class Literal(Node):
    value: Union[int, float, str, bool]

@dataclass
class FunctionCall(Node):
    name: str
    arguments: List['Expression']

@dataclass
class Expression(Node):
    # Placeholder for expressions literals, binary expressions, etc.
    pass
