from dataclasses import dataclass, field
from typing import List, Optional, Union

# Define the union for different types of statements
Statement = Union[
    'VariableDeclaration', 'ArrayDeclaration', 'IfStatement', 'WhileStatement', 
    'DoWhileStatement', 'AssignmentStatement', 'ArrayAssignmentStatement', 
    'ExpressionStatement', 'ReturnStatement'
]

# Base class for AST nodes
@dataclass
class ASTNode:
    pass

# Program structure to include global variables and function declarations
@dataclass
class Program(ASTNode):
    global_variables: 'GlobalVariables'
    declarations: List[ASTNode]

@dataclass
class FunctionStatement(ASTNode):
    name: str
    parameters: List['Parameter']
    return_type: str
    body: 'StatementBlock'

@dataclass
class MainFunctionStatement(ASTNode):
    parameters: List['Parameter']
    return_type: str
    body: 'StatementBlock'

@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: List['Parameter']
    return_type: str

@dataclass
class VariableDeclaration(ASTNode):
    var_kind: str  # 'val' or 'var'
    name: str
    data_type: str
    value: Optional['Expression']

# New class for array declarations
@dataclass
class ArrayDeclaration(ASTNode):
    var_kind: str  # 'var'
    name: str
    data_type: List[str]  # Nested types for multi-dimensional arrays
    value: List['Expression']

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
    else_block: Optional[StatementBlock]

@dataclass
class WhileStatement(ASTNode):
    condition: 'Expression'
    body: StatementBlock

@dataclass
class DoWhileStatement(ASTNode):
    condition: 'Expression'
    body: StatementBlock

@dataclass
class BreakStatement(ASTNode):
    pass

@dataclass
class ContinueStatement(ASTNode):
    pass

@dataclass
class AssignmentStatement(ASTNode):
    target: str
    value: 'Expression'

# New class for array assignments
@dataclass
class ArrayAssignmentStatement(ASTNode):
    target: str
    index: 'Expression'
    value: 'Expression'

@dataclass
class ArrayAllocation:
    var_kind: str
    name: str
    data_type: List[Union[str, tuple]]
    lengths: List[int] = field(default_factory=list)

    def __post_init__(self):
        self.extract_lengths()

    def extract_lengths(self):
        self.lengths = [dtype[1] for dtype in self.data_type if isinstance(dtype, tuple) and dtype[0] == 'array']

@dataclass
class ReturnStatement(ASTNode):
    value: Optional['Expression']

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
class PrintStatement:
    print_type: str
    expression: 'Expression'

@dataclass
class PrintfStatement:
    format_string: str
    arguments: List['Expression']
    
@dataclass
class ExpressionStatement(ASTNode):
    expression: 'Expression'

# New class for array access
@dataclass
class ArrayAccess(ASTNode):
    name: str
    index: 'Expression'

@dataclass
class Expression(ASTNode):
    pass
