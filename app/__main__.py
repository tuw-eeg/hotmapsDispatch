"""
when running a package as a script with -m, Python executes the contents of the __main__.py file.
This acts as the entry point of our program and takes care of the main flow, calling other parts as needed

execute 
<python -m app >
from above folder 
"""
from app.modules.common.FEAT.F16.F_16_server import check_modules,main as start_server
import argparse




def main(solver):
    flag = check_modules(solver)
    while flag:
        try:
            start_server(solver)
            flag = False
        except:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the HotMaps Dispatch Server')
    parser.add_argument('--solver', type=str,default="gurobi",help='specify which  solver to use (i.e.: gurobi,glpk...')
    args = parser.parse_args()
    print(f"Start HotMaps Dispatch Server using {args.solver.upper()}")
    main(args.solver)