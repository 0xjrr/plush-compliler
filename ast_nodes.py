from dataclasses import dataclass, field
from typing import List, Optional, Union

Statement = Union['VariableDeclaration', 'IfStatement', 'WhileStatement', 'AssignmentStatement', 'ExpressionStatement', 'ReturnStatement']

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    global_variables: 'GlobalVariables'
    declarations: List[ASTNode]


@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: List['Parameter']
    return_type: str
    body: 'StatementBlock'

@dataclass
class MainFunctionDeclaration(ASTNode):
    parameters: List['Parameter']
    return_type: str
    body: 'StatementBlock'

@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List['Expression']

@dataclass
class VariableDeclaration(ASTNode):
    var_kind: str  # 'val' or 'var'
    name: str
    data_type: str
    value: Optional['Expression'] 

@dataclass
class ArrayDeclaration(ASTNode):
    var_kind: str  # 'var'
    name: str
    data_type: str
    size: int

@dataclass
class GlobalVariables:
    declarations: List[Union['VariableDeclaration', 'ArrayDeclaration']]

    def __repr__(self):
        return f"GlobalVariables({self.declarations})"

@dataclass
class Parameter(ASTNode):
    name: str
    type: str

@dataclass
class StatementBlock(ASTNode):
    statements: List['Statement']

@dataclass
class IfStatement(ASTNode):
    condition: 'Expression'
    then_block: StatementBlock
    else_block: Union[StatementBlock, None]

@dataclass
class WhileStatement(ASTNode):
    condition: 'Expression'
    body: StatementBlock

@dataclass
class DoWhileStatement(ASTNode):
    condition: 'Expression'
    body: StatementBlock

@dataclass
class AssignmentStatement(ASTNode):
    target: str
    value: 'Expression'

@dataclass
class ArrayAssignmentStatement(ASTNode):
    target: str
    index: 'Expression'
    value: 'Expression'

@dataclass
class ReturnStatement(ASTNode):
    value: Union['Expression', None]

@dataclass
class BinaryExpression(ASTNode):
    operator: str
    left: 'Expression'
    right: 'Expression'

@dataclass
class UnaryExpression(ASTNode):
    operator: str
    operand: 'Expression'

@dataclass
class Literal(ASTNode):
    value: Union[int, float, str, bool]

@dataclass
class VariableReference(ASTNode):
    name: str

@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List['Expression']

@dataclass
class ExpressionStatement(ASTNode):
    expression: 'Expression'

@dataclass
class ArrayAccess(ASTNode):
    name: str
    index: 'Expression'

@dataclass
class Expression(ASTNode):
    # Placeholder for expressions literals, binary expressions, etc.
    pass
