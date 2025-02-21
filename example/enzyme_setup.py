import enzyme

p = enzyme.setup(
    code_caves = ( (0xc7bb0, 0xc7c0c), (0xc7c14, 0xc7c58), (0xc7c74, 0xc7ca4), (0xc7e08, 0xc7e4c) ),
    data_caves = (0x5ef041,0x5ef035),
    bss_cave = 0x7cdb90,
    dlopen_stub = 0x5ae02c,
    dlsym_stub = 0x5ae038
)

p.hook(0x10df78, "CCScheduler_update")

# Original patch
p.patch(0x544078, "ret")

enzyme.finish(p)