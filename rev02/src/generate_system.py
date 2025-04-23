import random
import sys

if len(sys.argv) != 2:
    print("usage: generate_system.py flag")
    exit(1)


flag = sys.argv[1]
solutions = [(ord(flag[i]), i) for i in range(len(flag))]

print("arg1=" + flag)

random.shuffle(solutions)
coeffic = []
right_side = []
str_eq = ""

for i in range(len(flag)):
    random.shuffle(solutions)
    # generate L linear equations
    r = 0
    eq = []
    for z in range(len(flag)):
        coeff = 0
        while coeff == 0:
            coeff = random.randint(-50, 50)
        eq.append((coeff, solutions[z][1]))
        r += coeff * solutions[z][0]
        if coeff < 0 and z > 0:
            str_eq += str(coeff) + f"x{solutions[z][1]}" + " + "
        else:
            str_eq += str(coeff) + f"x{solutions[z][1]}" + " + "

    str_eq += " = "
    str_eq += str(r)
    str_eq += "\n"
    coeffic.append(eq)
    right_side.append(r)

print(str_eq)
print(coeffic)
print(right_side)
print("system generated")


# generating the C file
def create_cond(index):
    cond = ""
    for i in range(len(coeffic[index])):
        cond += f" {coeffic[index][i][0]} * inp[{coeffic[index][i][1]}]"
        if i == len(coeffic[index]) - 1:
            cond += " == "
        else:
            cond += " + "
    cond += f"{right_side[index]}"
    return cond


def build_cond(indexes):
    conds = ""
    for i in range(len(indexes)):
        conds += create_cond(indexes[i])
        if i == len(indexes) - 1:
            conds += ";"
        else:
            conds += " && "
    return conds


with open("check.c", "w") as f:
    # base includes
    f.writelines(["#include <stdio.h>", "\n\n"])
    f.writelines(["#include <string.h>", "\n\n"])
    f.writelines(["#include <emscripten.h>", "\n\n\n"])

    # check0 function for flag lenght
    f.writelines(
        [
            "EMSCRIPTEN_KEEPALIVE\n",
            "int check0(char* inp){\n",
            f"\x09return strlen(inp)=={len(flag)};\n",
            "}\n",
        ]
    )

    # generating conditions
    i = 0
    nCheck = 1
    while i < len(flag):
        n = random.randint(1, min(4, len(flag) - i))
        indexes = []
        for z in range(i, i + n):
            indexes.append(z)
        cond = build_cond(indexes)
        f.writelines(
            [
                "EMSCRIPTEN_KEEPALIVE\n",
                "int check" + str(nCheck) + "(char* inp){\n",
                "\x09return " + cond + "\n",
                "}\n",
            ]
        )
        i += n
        nCheck += 1

    # check password function
    f.writelines(
        [
            "EMSCRIPTEN_KEEPALIVE\n",
            "int password_check(char* inp){\n",
            "if(!check0(inp))return 0;\n",
        ]
    )
    for i in range(1, nCheck):
        f.writelines([f"if(!check{i}(inp)) return 0;\n"])
    f.writelines(["return 1;\n", "}\n"])
