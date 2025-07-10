import pulp as pl

# The python code of the GRA
def GRA(Q, L, conflict_matrix=None):
    row = len(Q)
    col = len(Q[0])
    La = [1] * row # can only pick same exercise once

    # build a optimal problem
    pro = pl.LpProblem('Maximize the effectiveness of the assignments', pl.LpMaximize)# maximize
    # build variables for the optimal problem
    lpvars = [[pl.LpVariable("x"+str(i)+"y"+str(j), lowBound = 0, upBound = 1, cat='Integer') for j in range(col)] for i in range(row)]


        # Build the objective function
    all_effectiveness = pl.LpAffineExpression()
    for i in range(row):
        for j in range(col):
            all_effectiveness += Q[i][j] * lpvars[i][j]

    pro += all_effectiveness

    # Build constraint for each role
    for j in range(col):
        pro += pl.lpSum(lpvars[i][j] for i in range(row)) == L[j], f"L{j}"

    # Build constraint for each agent
    for i in range(row):
        pro += pl.lpSum(lpvars[i][j] for j in range(col)) <= La[i], f"La{i}"

     # Conflict constraints
    if conflict_matrix:
        for i1 in range(row):
            for i2 in range(i1 + 1, row):  # ensure each pair only appears once
                if conflict_matrix[i1][i2] == 1:
                    for j in range(col):
                        pro += (
                            lpvars[i1][j] + lpvars[i2][j] <= 1,
                            f"agent_conflict_{i1}_{i2}_role{j}"
                        )


    # solve optimal problem
    status = pro.solve()
    
    # get the result of T matrix
    if pl.LpStatus[status] != "Optimal":
        return None

    # Extract matrix
    T_matrix = [[lpvars[i][j].varValue for j in range(col)] for i in range(row)]
    return T_matrix

def GMRA(Q, L, La, conflict_matrix=None):
    row = len(Q)
    col = len(Q[0])

    # Build an optimization problem
    pro = pl.LpProblem('Maximize assignment score', pl.LpMaximize)

    # Variables
    lpvars = [[pl.LpVariable(f"x{i}y{j}", lowBound=0, upBound=1, cat='Binary') for j in range(col)] for i in range(row)]
    agent_used = [pl.LpVariable(f"agent_used_{i}", lowBound=0, upBound=1, cat='Binary') for i in range(row)]

    # Objective
    pro += pl.lpSum(Q[i][j] * lpvars[i][j] for i in range(row) for j in range(col))

    # Constraints: roles
    for j in range(col):
        pro += pl.lpSum(lpvars[i][j] for i in range(row)) == L[j], f"L{j}"

    # Constraints: agent capacity and usage
    for i in range(row):
        pro += pl.lpSum(lpvars[i][j] for j in range(col)) <= La[i], f"La{i}"
        pro += pl.lpSum(lpvars[i][j] for j in range(col)) <= La[i] * agent_used[i], f"AgentUsed_{i}"

    # Conflict constraints
    if conflict_matrix:
        for i1 in range(row):
            for i2 in range(i1 + 1, row):
                if conflict_matrix[i1][i2] == 1:
                    for j in range(col):
                        pro += lpvars[i1][j] + lpvars[i2][j] <= 1, f"Conflict_{i1}_{i2}_role{j}"

    # Solve
    status = pro.solve(pl.PULP_CBC_CMD(msg=False))

    if pl.LpStatus[status] != "Optimal":
        return None

    # Extract matrix
    T_matrix = [[lpvars[i][j].varValue for j in range(col)] for i in range(row)]
    return T_matrix


def GRACCF(Q, L, M=None):
    row = len(Q)
    col = len(Q[0])
    La = [1] * row  # Each agent can do at most one role

    pro = pl.LpProblem('Maximize_Effectiveness_with_Conflicts', pl.LpMaximize)

    # Define binary assignment variables
    lpvars = [
        [pl.LpVariable(f"x{i}y{j}", cat='Binary') for j in range(col)]
        for i in range(row)
    ]

    # Objective: effectiveness
    objective = pl.lpSum(Q[i][j] * lpvars[i][j] for i in range(row) for j in range(col))

    # If conflict/cooperation matrix M is provided, add pairwise interactions
    if M is not None:
        for i in range(row):
            for k in range(i + 1, row):
                if M[i][k] != 0:
                    # Define the sum of assignment variables for agents i and k
                    assigned_i = pl.lpSum(lpvars[i][j] for j in range(col))
                    assigned_k = pl.lpSum(lpvars[k][j] for j in range(col))
                    # Add cooperation or conflict to the objective
                    objective += 0.1 * M[i][k] * (assigned_i + assigned_k)  # scale factor

    pro += objective

    # Role constraints: exactly L[j] agents per role
    for j in range(col):
        pro += pl.lpSum(lpvars[i][j] for i in range(row)) == L[j], f"Role_{j}"

    # Agent constraints: each agent gets at most 1 role
    for i in range(row):
        pro += pl.lpSum(lpvars[i][j] for j in range(col)) <= La[i], f"Agent_{i}"

    # Solve
    status = pro.solve()

    if pl.LpStatus[status] != "Optimal":
        return None

    # Extract binary assignment matrix
    T_matrix = [[lpvars[i][j].varValue for j in range(col)] for i in range(row)]
    return T_matrix

def GMRACCF(Q, L, La, conflict_matrix=None):
    row = len(Q)      # number of agents
    col = len(Q[0])   # number of roles

    pro = pl.LpProblem('Maximize_assignment_with_conflicts', pl.LpMaximize)

    # Assignment variables: agent i assigned to role j
    lpvars = [[pl.LpVariable(f"x{i}y{j}", cat='Binary') for j in range(col)] for i in range(row)]

    # Agent usage binary variables
    agent_used = [pl.LpVariable(f"agent_used_{i}", cat='Binary') for i in range(row)]

    # Conflict variables: conflict indicator between agent pairs for roles
    conflict_vars = None
    if conflict_matrix is not None:
        conflict_vars = [[[pl.LpVariable(f"c_{i1}_{i2}_{j}", cat='Binary') 
                           for j in range(col)] for i2 in range(row)] for i1 in range(row)]

    # Objective: sum of assignments + sum of conflicts (if provided)
    assignment_obj = pl.lpSum(Q[i][j] * lpvars[i][j] for i in range(row) for j in range(col))

    if conflict_matrix is not None:
        conflict_obj = pl.lpSum(conflict_vars[i1][i2][j] * conflict_matrix[i1][i2] 
                                for i1 in range(row) for i2 in range(row) for j in range(col))
        pro += assignment_obj + conflict_obj
    else:
        pro += assignment_obj

    # Role constraints: exactly L[j] agents assigned per role
    for j in range(col):
        pro += pl.lpSum(lpvars[i][j] for i in range(row)) == L[j], f"Role_{j}"

    # Agent capacity and usage constraints
    for i in range(row):
        pro += pl.lpSum(lpvars[i][j] for j in range(col)) <= La[i], f"Capacity_{i}"
        pro += pl.lpSum(lpvars[i][j] for j in range(col)) <= La[i] * agent_used[i], f"AgentUsedLink_{i}"

    # Linking conflict_vars with assignments if conflicts provided
    if conflict_matrix is not None:
        for i1 in range(row):
            for i2 in range(row):
                for j in range(col):
                    pro += conflict_vars[i1][i2][j] * 2 <= lpvars[i1][j] + lpvars[i2][j], f"ConflictLink1_{i1}_{i2}_{j}"
                    pro += lpvars[i1][j] + lpvars[i2][j] <= conflict_vars[i1][i2][j] + 1, f"ConflictLink2_{i1}_{i2}_{j}"

    # Solve quietly
    status = pro.solve(pl.PULP_CBC_CMD(msg=False))

    if pl.LpStatus[status] != "Optimal":
        return None

    # Extract assignment matrix
    T_matrix = [[lpvars[i][j].varValue for j in range(col)] for i in range(row)]
    return T_matrix

def CRACCF(Q, L, conflict_matrix=None):
    m = len(Q)    # number of agents
    n = len(Q[0]) # number of roles
    
    pro = pl.LpProblem("GRA_Model", pl.LpMaximize)

    # Decision variables
    vars = [[pl.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(n)] for i in range(m)]
    
    # vars1 conflict variables still needed for constraints and objective
    vars1 = [[[pl.LpVariable(f"c_{i1}_{i2}_{j}", cat="Binary") for j in range(n)] for i2 in range(m)] for i1 in range(m)]
    
    # Objective
    assignment_sum = pl.lpSum(vars[i][j] * Q[i][j] for i in range(m) for j in range(n))
    conflict_sum = pl.lpSum(vars1[i1][i2][j] * conflict_matrix[i1][i2] for i1 in range(m) for i2 in range(m) for j in range(n))
    
    pro += assignment_sum + conflict_sum

    # Constraints
    for j in range(n):
        pro += pl.lpSum(vars[i][j] for i in range(m)) == L[j], f"Role_{j}_assignment"

    for i in range(m):
        pro += pl.lpSum(vars[i][j] for j in range(n)) <= 1, f"Agent_{i}_assignment"

    for i1 in range(m):
        for i2 in range(m):
            for j in range(n):
                pro += vars1[i1][i2][j] * 2 <= vars[i1][j] + vars[i2][j], f"conflict_link1_{i1}_{i2}_{j}"
                pro += vars[i1][j] + vars[i2][j] <= vars1[i1][i2][j] + 1, f"conflict_link2_{i1}_{i2}_{j}"

    pro.solve()

    # Extract T as 2D matrix [m x n]
    T_matrix = [[0] * n for _ in range(m)]

    for v in pro.variables():
        name = v.name
        val = v.varValue if v.varValue is not None else 0
        if name.startswith("x_"):
            _, i, j = name.split("_")
            i, j = int(i), int(j)
            T_matrix[i][j] = 1 if abs(val - 1) < 1e-4 else 0

    return T_matrix
