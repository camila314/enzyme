import patcher
import sys
import os

p = patcher.Patcher(sys.argv[1])

# Bootstrapper

p.bin_patch(0x5ef035, b"findthehook")
p.bin_patch(0x5ef041, b"@executable_path/hook.dylib")

p.code_cave(0xc7bb0, 0xc7c0c)
p.code_cave(0xc7c14, 0xc7c58)
p.code_cave(0xc7c74, 0xc7ca4)
p.code_cave(0xc7e08, 0xc7e4c)

boot_addr = p.inject_code(open(os.path.dirname(__file__) + "/bootstrap.asm", "r").read())

entry_addr = p.inject_code(f"""
stp x29, x30, [sp, #-0x10]!
bl @{hex(boot_addr)}
ldp x29, x30, [sp], #0x10
ret
""")

p.bootstrap(entry_addr)

## Hook example
p.hook(0x10df78, "CCScheduler_update")

## iOS 15 crash fix
p.patch(0x544078, "ret")

p.generate_header(sys.argv[2] + "/bootloader.hpp")
p.export_to(sys.argv[2] + "/GeometryJump")