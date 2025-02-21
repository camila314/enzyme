import patcher
import sys
import os

def setup(code_caves, data_caves, bss_cave, dlopen_stub, dlsym_stub):
    p = patcher.Patcher(sys.argv[1])

    p.bin_patch(data_caves[0], b"@executable_path/hook.dylib")
    p.bin_patch(data_caves[1], b"findthehook")

    for i in code_caves:
        p.code_cave(i[0], i[1])

    bootstrap_code = open(os.path.dirname(__file__) + "/bootstrap.asm", "r").read()
    bootstrap_code = bootstrap_code.replace("{cache_page}", hex(bss_cave - bss_cave % 4096))
    bootstrap_code = bootstrap_code.replace("{cache_offset}", hex(bss_cave % 4096))
    bootstrap_code = bootstrap_code.replace("{dlopen_stub}", hex(dlopen_stub))
    bootstrap_code = bootstrap_code.replace("{dlsym_stub}", hex(dlsym_stub))
    bootstrap_code = bootstrap_code.replace("{data1_page}", hex(data_caves[0] - data_caves[0] % 4096))
    bootstrap_code = bootstrap_code.replace("{data1_offset}", hex(data_caves[0] % 4096))
    bootstrap_code = bootstrap_code.replace("{data2_page}", hex(data_caves[1] - data_caves[1] % 4096))
    bootstrap_code = bootstrap_code.replace("{data2_offset}", hex(data_caves[1] % 4096))

    boot_addr = p.inject_code(bootstrap_code)

    p.bootstrap(p.inject_code(f"""
stp x29, x30, [sp, #-0x10]!
bl @{hex(boot_addr)}
ldp x29, x30, [sp], #0x10
ret
"""))

    return p

def finish(p):
    p.generate_header(sys.argv[2] + "/bootloader.hpp")
    p.export_to(sys.argv[2] + "/" + sys.argv[3])

sys.path.append(sys.argv[4])
import enzyme_setup