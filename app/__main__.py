"""
when running a package as a script with -m, Python executes the contents of the __main__.py file.
This acts as the entry point of our program and takes care of the main flow, calling other parts as needed

execute 
<python -m app >
from above folder 
"""
from app.modules.common.FEAT.F16.F_16_server import check_modules,main
import argparse,sys

def start_app(solver,openbrowser,port,num_procs):
    flag = check_modules(solver)
    while flag:
        try:
            main(solver,openbrowser=openbrowser,port=port,num_procs=num_procs)
            flag = False
        except KeyboardInterrupt:
            sys.exit()
        except:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the HotMaps Dispatch Server')
    parser.add_argument('--solver', type=str,default="gurobi",help='specify which solver to use (i.e.: gurobi,glpk...')
    parser.add_argument('--openbrowser', type=bool,default=True,help="specify if the web user interface should open automatically with your default browser, default is True")
    parser.add_argument('--port', type=int,default=-1,help="specify the port which should be open, default port is a random free port")
    parser.add_argument('--num_procs', type=int,default=0,help="specify the number of cpus used, 0 is auto")

    args = parser.parse_args()
    print(f"Start HotMaps Dispatch Server using {args.solver.upper()}")
    solver=args.solver
    openbrowser=args.openbrowser
    port=args.port
    num_procs=args.num_procs
    start_app(solver,openbrowser,port,num_procs)
