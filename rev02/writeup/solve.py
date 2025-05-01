from z3 import *

lines = []
with open ("disassembly.c","r") as f:
    lines = f.readlines()

i = 0
index_lines = []
multipliers = []
results = []

for line in lines:
    if "i32_load8_u" in line:
        index_lines.append(line)
        if "*" in lines[i+16]: #normal multiplication
            multipliers.append(lines[i+12])
        else:
            multipliers.append("POW|"+lines[i+12]) #power of 2
    i+=1

#the first line is the function definition and the last 2 lines are used for the lenght of the flag
index_lines = index_lines[1:-2]
multipliers = multipliers[1:-2]

#get the results
i = 0
for line in lines:
    if "var_i0 = var_i0 == var_i1;" in line:
        results.append(lines[i-8]) #always 8 lines up this check
    i+=1


#first one is for check0,last 2 are for another function
results = results[1:-2]

#A single equation is an array of tuples (multiplier,index)
equations = []
for i in  range(41):
    equations.append([])
    for z in range(41):
        number = -1
        if "+" in index_lines[i*41+z]:
            number = index_lines[i*41+z].split('+')[1][:-4] # remove u)\n;
            number = int(number)
        else:
            number = 0
        
        multiplier = multipliers[i*41+z].split('=')[1][1:-3]
        multiplier = int(multiplier)

        if "POW|" in multipliers[i*41+z]: #powers of 2
            multiplier=2**(multiplier)

        if multiplier > 2**31-1: #negative numbers
            multiplier-=4294967296
        equations[i].append((multiplier,number))



#get right side
right_side = []
for r in results:
    number = r.split('=')[1][1:-3]
    number = int(number)
    if number > 2**31-1:
        number-=4294967296
    right_side.append(number)



#solve with z3 :)
solver = Solver()

x = [Real(f"x{i}") for i in range(41)]

for eq, rhs in zip(equations, right_side):
    equation = Sum([z * x[j] for z, j in eq])  # Correct multiplication
    solver.add(equation == rhs)

if  solver.check() == sat:
    model = solver.model()
    solution = [model[x[i]] for i in range(41)]
    solution = ''.join(chr(int(val.as_string())) for val in solution)
    print("Solution:", solution)
else:
    print("No solution found.")