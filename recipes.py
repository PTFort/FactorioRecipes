import os
from os import listdir
from os.path import isfile, join
import re
import pydot
import subprocess

def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)

def clean_recipe(r):
    recipe = {}

    ingred_bool = False
    ingreds = []

    results_bool = False
    results = []
    for token in r:


        if token in ["{", "}", "},", "data:extend(", ""]:
            continue

        #print(token)
        if "{" not in token:
            ingred_bool = False
            results_bool = False

        if ingred_bool:
            ingreds.append(token)
        elif results_bool:
            results.append(token)
        else:
            #print("Normal: " + token)

            s = token.split("=")
            key = s[0].strip()
            value = s[1].replace("\"", "").replace(",","").strip()
            #print(key + " : " + value)

            if key not in ["ingredients", "results"]:
                recipe[key] = value

        if token.startswith("ingredients"):
            ingred_bool = True

            if not token.endswith("="):
                ingreds.append(token.replace("ingredients =", ""))
                ingred_bool = False

        elif token.startswith("results"):
            results_bool = True


    recipe["ingredients"] = []
    for i in ingreds:
        i = i.replace("{", "").replace("}", "").replace(",", "")
        s = i.split()

        if len(s) == 2 or len(s) % 2 == 1:
            recipe["ingredients"].append(s)
        else:
            for a, b in pairwise(s):
                recipe["ingredients"].append([a, b])

    recipe["results"] = []
    for r in results:
        r = r.replace("{", "").replace("}", "").replace(",","")
        s = r.split()
        recipe["results"].append(s)

    # if recipe["name"] == "iron-axe":
    #     print(ingreds)
    #     for key in recipe.keys():
    #         print(key + " : " + str(recipe[key]))
    #     print("\n")
    return recipe

def main():
    recipe_directory = "../data/base/prototypes/recipe/"

    recipe_list = []

    file_list = [ f for f in listdir(recipe_directory) if isfile(join(recipe_directory,f)) ]
    for f in file_list:
        #print(f)

        if not f.endswith(".lua"):
            continue

        f_path = join(recipe_directory,f)
        print(f_path)

        f_in = open(f_path)

        raw_recipes = []

        raw_recipe = []
        start = False
        for line in f_in:

            if line.startswith("  {"):
                start = True
            elif line.startswith("  }"):
                start = False
                raw_recipes.append(raw_recipe)
                raw_recipe = []
            else:
                raw_recipe.append(line.strip())


        for r in raw_recipes:
            recipe_list.append(clean_recipe(r))



    g = pydot.Dot(graph_type='digraph', concentrate=True, ratio=0.4)

    edges = []

    for recipe in recipe_list:
        #print(recipe)

        name = recipe["name"]
        n = pydot.Node(name)
        g.add_node(n)


        #simple case
        ingreds = recipe["ingredients"]

        for ingred in ingreds:
            #print(ingred)
            if len(ingred) == 2:
                i = ingred[0].replace("\"", "")
                n = ingred[1]

            else:
                #print(ingred)
                i = ingred[1].replace("\"", "").replace("name=","")
                n = ingred[2].replace("amount=","")

            edges.append([name, i, n])



        # for r in recipe["results"]:
        #     print(r)

        # try:
        #     print(name + " : " + recipe["result"])
        #     edges.append([name, recipe["result"]])
        # except KeyError:
        #     pass


    for target, source, label in edges:
        g.add_edge(pydot.Edge(source, target, label=label))

    g.write_dot('factorio.dot')

    subprocess.call("dot -Tsvg factorio.dot -o factorio.svg", shell=True)


if __name__ == "__main__":
    main()