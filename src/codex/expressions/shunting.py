import operator
from codex.structures.stack import ArrayStack


_OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def evaluate_rpn(tokens: list[str]) -> float:
    stack: ArrayStack[float] = ArrayStack()
    for token in tokens:
        if token in _OPERATORS:
            b = stack.pop()
            a = stack.pop()
            stack.push(_OPERATORS[token](a, b))
        else:
            stack.push(float(token))
    return stack.pop()
def _precedence(op: str) -> int:
    if op in ("+", "-"):
        return 1
    if op in ("*", "/"):
        return 2
    return 0  # parentheses get the lowest precedence so they're never popped early
def shunting_yard(tokens: list[str]) -> list[str]:
    output: list[str] = []
    operators: ArrayStack[str] = ArrayStack()

    for token in tokens:
        if token in ("+", "-", "*", "/"):
            while (operators and operators.peek() != "("
                   and _precedence(operators.peek()) >= _precedence(token)):
                output.append(operators.pop())
            operators.push(token)
        elif token == "(":
            operators.push(token)
        elif token == ")":
            while operators.peek() != "(":
                output.append(operators.pop())
            operators.pop()  # discard the matching '('
        else:
            output.append(token)  # operand — flows straight to output

    while operators:
        output.append(operators.pop())

    return output
