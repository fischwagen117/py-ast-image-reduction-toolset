from sys import argv

def print_err(err_msg):
    print(f"\033[31mERROR\033[0m: {err_msg}")
    exit(1)

prg_name = argv[0]

help_msg="""Program to create master reduction files.
Usage: 
python3 {prg_name} --create_master_bias [bias files dir] [master bias file name]
python3 {prg_name} --create_master_dark [dark files dir] [master dark file name] [master bias file path (optional)]
python3 {prg_name} --create_master_flat [flat files dir] [master flat file name] [master bias file path (optional)] [master dark file path (optional)]
When creating master flat, insert paths for master bias and master dark or do not insert any!
"""

try:
    main_arg = argv[1]
except IndexError:
    print_err("Not enough arguments! Run python3 {prg_name} -h / --help to check for program usage")
    exit(69)

if main_arg == "-h" or main_arg == "--help":
    print(help_msg)
    exit(0)

arg_cnt = len(argv)
if arg_cnt < 4:
    print_err(f"Not enough arguments provided! Check help to see program usage: python3 {argv[0]} -h / --help")

from proc import create_bias, create_dark, create_flat

dir_path = argv[2]
out_name = argv[3]

if main_arg == "--create_master_bias":
    create_bias(dir_path, out_name)

elif main_arg == "--create_master_dark":
    try:
        bias_path = argv[4]
    except IndexError:
        create_dark(dir_path, out_name)
    else:
        create_dark(dir_path, out_name, bias_path)

elif main_arg == "--create_master_flat":
    try:
        bias_path = argv[4]
        dark_path = argv[5]
    except IndexError:
        create_flat(dir_path, out_name)
    else:
        create_flat(dir_path, out_name, bias_path, dark_path)

