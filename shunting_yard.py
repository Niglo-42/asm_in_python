def shunting_yard(toks: list[str], vars: dict) -> int:
    input = []
    value = {
        "+": 2,
        "-": 1,
        "*": 3,
        "/": 3,
        "(": 0,
        ")": 4
    }
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b
    }
    holding_stack = []
    solve_stack = []
    output = []
    nbrs = []

    for tok in toks:
        nbrs.append([])
        char = 0
        while char < len(tok):
            if tok in vars:
                try:
                    input.append(int(vars[tok]))
                except ValueError:
                    exit(1)
                break
            elif tok[char] in "*/-+()":
                input.append(tok[char])
                char += 1
            else:
                nbr = 0
                while char < len(tok) and tok[char].isdigit():
                    nbr = nbr * 10 + int(tok[char])
                    char += 1
                input.append(nbr)
    i = 0
    while i < len(input):
        if isinstance(input[i], int):
            output.append(input[i])
        elif input[i] == ")":
            while holding_stack[-1] != "(":
                output.append(holding_stack.pop())
            holding_stack.pop()
        else:
            while (holding_stack and value[holding_stack[-1]] > value[input[i]]
                   and input[i] != "("):
                output.append(holding_stack.pop())
            holding_stack.append(input[i])
        i += 1
    while holding_stack:
        output.append(holding_stack.pop())
    if len(output) < 2:
        return int(output[0])
    while output:
        while output and isinstance(output[0], int):
            solve_stack.append(output.pop(0))
        if len(solve_stack):
            b = solve_stack.pop()
        if len(solve_stack):
            a = solve_stack.pop()
        solve_stack.append(ops[output.pop(0)](a, b))
    return int(solve_stack[0])