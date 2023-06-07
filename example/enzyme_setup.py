import enzyme

p = enzyme.setup(
	# need a good amount of code cave space
	code_caves = ( (0xc7bb0, 0xc7c0c), (0xc7c14, 0xc7c58), (0xc7c74, 0xc7ca4), (0xc7e08, 0xc7e4c) ),
	# 28 bytes and 12 bytes respectively
	data_caves = (0x5ef041,0x5ef035),
	# 8 bytes of writable bss space
	bss_cave = 0x7cdb90,
	# address of the dlopen stub
	dlopen_stub = 0x5ae02c,
	# address of the dlsym stub
	dlsym_stub = 0x5ae038
)

# Hook example
p.hook(0x10df78, "CCScheduler_update")

# Patch example
p.patch(0x544078, "ret")

# Apply everything
enzyme.finish(p)