import csv
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value

# Step 1: Parse the CSV
sku_coverage = {}
components = []

with open('example_matrix.csv', 'r') as f:
    reader = csv.reader(f)
    headers = next(reader)  # Read the header row
    components = headers[1:]  # Components are all columns after 'Top_Lvl_SKU'

    for row in reader:
        sku = row[0]  # First column is the SKU
        # Map SKU to list of components it covers (where value is '1')
        covered_components = [comp for i, comp in enumerate(components) if row[i + 1] == '1']
        sku_coverage[sku] = covered_components

print(sku_coverage)

# Step 2: Set up the LP problem
prob = LpProblem("SKU_Set_Cover", LpMinimize)

# Binary variables: 1 if SKU is chosen, 0 otherwise
x = {sku: LpVariable(f"x_{sku}", 0, 1, cat="Binary") for sku in sku_coverage}

# Objective: Minimize the number of SKUs chosen
prob += lpSum(x[sku] for sku in sku_coverage), "Total_SKUs"

# Constraints: Each component must be covered by at least one chosen SKU
for comp in components:
    prob += lpSum(x[sku] for sku in sku_coverage if comp in sku_coverage[sku]) >= 1, f"Cover_{comp}"

# Step 3: Solve the problem
prob.solve()

# Step 4: Output results
print("Status:", prob.status)  # 1 means optimal
print("Minimal number of SKUs:", value(prob.objective))
print("Selected SKUs:")
for sku in sku_coverage:
    if value(x[sku]) == 1:
        print(f"- {sku} covering {sku_coverage[sku]}")

with open('result.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['SKU', 'Components'])
    for sku in sku_coverage:
        if value(x[sku]) == 1:
            writer.writerow([sku, sku_coverage[sku]])
