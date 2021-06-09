
import subprocess
import re

prod_re = re.compile("^([^:]+):")
prereq_re = re.compile(r"\s*(?!\\)\S+\s*")

"""
def c_makedeps(filename, **kwargs):

    show_syshdrs = kwargs.get("show_syshdrs", False)
    cc = kwargs.get("cc", "cc")
    inc = kwargs.get("inc", [])
    if not type(inc) is list:
        raise TypeError("inc should be a list")

    inc_cmd = map(lambda x: "-I"+ x, inc)
    opt = '-M' if show_system_headers else '-MM'
    try:
        cmd = [cc, opt, filename] + inc_list
        cmd.extend(inc_cmd)
        o = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        raise e
"""

def makedeps(filename, include_dirs=None, show_system_headers=False, compiler="cc"):

    if not include_dirs:
        include_dirs = []

    if isinstance(include_dirs, str):
        include_dirs = [include_dirs]

    inc_list = []
    for d in include_dirs:
        inc_list.append(f"-I{d}")

    opt = '-M' if show_system_headers else '-MM'

    try:
        cmd = [compiler, opt, filename] + inc_list
        o = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        raise e

    prod = prod_re.match(o)
    if not prod:
        raise ValueError("Failed to match the product!")
    product = prod.group(1)

    rest = o.split(product + ":")[1]
    stripped = [x.strip() for x in prereq_re.findall(rest) if x.strip()]

    return (product, stripped)


if __name__ == "__main__":
    print(makedeps("out/abba.c", "."))
