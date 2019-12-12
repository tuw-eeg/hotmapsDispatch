"""
when running a package as a script with -m, Python executes the contents of the __main__.py file.
This acts as the entry point of our program and takes care of the main flow, calling other parts as needed

execute 
<python -m app >
from above folder 
"""
from app.modules.common.FEAT.F16.F_16_server import main as start_server

def main():
    flag = True
    while flag:
        try:
            start_server()
            flag = False
        except:
            pass

if __name__ == "__main__":
	main()