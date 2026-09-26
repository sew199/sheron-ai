import ast
import operator


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def calculate(expression):

    try:
        expression = expression.strip()

        if not expression:
            return None

        # Normal mathematical symbols
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")
        expression = expression.replace("–", "-")

        tree = ast.parse(
            expression,
            mode="eval"
        )

        def solve(node):

            # Numbers
            if isinstance(node, ast.Constant):

                if isinstance(
                    node.value,
                    (int, float)
                ):
                    return node.value

                raise ValueError

            # + - * / % **
            if isinstance(node, ast.BinOp):

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError

                left = solve(node.left)
                right = solve(node.right)

                # Prevent huge powers
                if (
                    isinstance(node.op, ast.Pow)
                    and abs(right) > 100
                ):
                    raise ValueError

                return operation(
                    left,
                    right
                )

            # Positive / negative
            if isinstance(node, ast.UnaryOp):

                value = solve(node.operand)

                if isinstance(
                    node.op,
                    ast.USub
                ):
                    return -value

                if isinstance(
                    node.op,
                    ast.UAdd
                ):
                    return value

                raise ValueError

            raise ValueError

        result = solve(tree.body)

        if isinstance(result, float):

            if result == float("inf"):
                return None

            if result == float("-inf"):
                return None

            if result.is_integer():
                return int(result)

        return result

    except (
        SyntaxError,
        ValueError,
        TypeError,
        ZeroDivisionError,
        OverflowError
    ):
        return None
