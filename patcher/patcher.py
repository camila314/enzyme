from keystone import *
from capstone import *
import io
import os
import re

template_part1 = """
extern int exists_{name};
inline long original_{name} = (getBase() + {addr} + exists_{name});
__attribute__((naked)) inline void final_{name}() {{
	__asm volatile (
        "{string}"
        "ldr x9, %[t]\\n"
        "mov x8, x10\\n"
        "br x9"
        :
        : [t] "m" (original_{name})
    );
}}

#define ${name}(...) \\
	sig_{name}(__VA_ARGS__); \\
	static cast_fn<decltype(sig_{name}), void(__VA_ARGS__)>::return_t real_{name}(__VA_ARGS__); \\
	static cast_fn<decltype(sig_{name}), void(__VA_ARGS__)>::fn_t* {name}; \\
	inline int exists_{name} = 8; \\
	__attribute__((constructor)) static void ctor_{name}() {{ \\
		if (hookDB == nullptr) {{ \\
			hookDB = new hookDB_t(); \\
		}} \\
		auto& entry = (*hookDB)[getBase() + {addr}]; \\
		if (entry.size() == 0) \\
			entry.push_back({{reinterpret_cast<long>(final_{name}), nullptr}}); \\
		entry.push_back({{reinterpret_cast<long>(&real_{name}), reinterpret_cast<long*>(&{name})}}); \\
	}} \\
	cast_fn<decltype(real_{name}), void(__VA_ARGS__)>::return_t real_{name}(__VA_ARGS__)
"""

template_part2 = """
		case {addr}:
			return Long_{name};
"""

template_whole = """
#pragma once

#include <mach-o/dyld.h>
#import <UIKit/UIKit.h>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <utility>

template <typename T, typename U>
struct cast_fn;

template <typename T, typename ...Args>
struct cast_fn<T(Args...), void(Args...)> {{
	using return_t = T;
	using fn_t = T(Args...);	
}};

template <typename T>
struct tuple_from_fn;

template <typename T, typename ...Args>
struct tuple_from_fn<T(Args...)> {{
	using value = std::tuple<Args...>;
}};

template <typename T>
using tuple_from_fn_t = typename tuple_from_fn<T>::value;

inline long getBase() {{
    return _dyld_get_image_vmaddr_slide(0)+0x100000000;
}}

// first = current, next = ref to next in chain
using hookDB_t = std::unordered_map<long, std::vector<std::pair<long, long*>>>;

inline hookDB_t* hookDB = nullptr;

{part1}

inline void error() {{
    UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Fatal error" 
                                                    message:@"Unable to find hook address" 
                                                    delegate:nil
                                                    cancelButtonTitle:@"OK" 
                                                    otherButtonTitles:nil];
    [alert show];
}}

__attribute__((used, visibility("default"), hot)) extern "C" inline long findthehook(long inp) {{
	static bool initialized = false;
	if (!initialized) {{
		for (auto [k, v] : *hookDB) {{
			for (int i = v.size() - 1; i > 0; --i) {{
				*v[i].second = v[i - 1].first;
			}}
		}}
	}}

	if (hookDB->count(inp)) {{
		return (*hookDB)[inp].back().first;
	}} else {{
		return reinterpret_cast<long>(error);
	}}
}}
"""

class Patcher(object):
	def __init__(self, src):
		self.src = open(src, 'rb').read()
		self.patches = []
		self.hooks = []

		self.bootstrap_addr = 0x0
		self.code_caves = []
		self.ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
		self.cs = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
	def patch(self, addr, new):
		try:
			self.patches.append((addr, bytes(self.ks.asm(new)[0])))
		except:
			print(new)
			raise
	def bin_patch(self, addr, new):
		self.patches.append((addr, new))
	def bootstrap(self, addr):
		self.bootstrap_addr = addr
	def hook(self, addr, name):
		self.hooks.append((addr, name))

		self.patch(addr, f"adr x13, #0x0\nb #{self.bootstrap_addr - addr}")
	def code_cave(self, start, end):
		if start % 4 != 0 or end % 4 != 0:
			raise "Bad boundary"
		self.code_caves.append([start, end])
	def inject_code(self, code):
		#remove comments
		code = re.sub(r"\s*;.*", "", code)

		# remove unnecessary newlines
		instructions = "".join(code.split("\n")).split("\n")

		labels = {}
		label_instructions = []
		code = re.sub(r"^(\w+):\n$", "", code)

		very_start = self.code_caves[0][0]
		for instruction in filter(lambda x: len(x), code.split("\n")):

			start = self.code_caves[0][0]
			if start == self.code_caves[0][1]:
				self.code_caves.pop(0)
				if not len(self.code_caves):
					raise "Ran out of code cave space"

				self.patch(start, f"b #{self.code_caves[0][0] - start}")
				start = self.code_caves[0][0]

			potential_label_def = re.search(r"^(\w+):$", instruction)
			if potential_label_def != None:
				labels[potential_label_def.group(1)] = start
				continue

			formatted = re.sub(r'adr@(0x[0-9a-fA-F]+)', lambda x: "#{}".format(int(x.group(1), 16) - (start - start % 4096)), instruction)
			formatted = re.sub(r'@(0x[0-9a-fA-F]+)', lambda x: "#{}".format(int(x.group(1), 16) - start), formatted)

			potential_label = re.search(r'\$(\w+)', formatted)
			if potential_label != None:
				label_instructions.append((formatted, start))
			else:
				self.patch(start, formatted)
			
			self.code_caves[0][0] += 4

		for instruction in label_instructions:
			formatted = re.sub(r'\$(\w+)', lambda x: "#{}".format(labels[x.group(1)] - instruction[1]), instruction[0])
			self.patch(instruction[1], formatted)

		return very_start
	def export_to(self, dest):
		out = io.BytesIO(self.src)

		for patch in self.patches:
			out.seek(patch[0])
			out.write(patch[1])

		out.seek(0)
		open(dest, "wb").write(out.read())
		os.chmod(dest, 0o777)

	def generate_header(self, dest):
		# hooks
		part1 = ""
		part2 = ""

		for hook in self.hooks:
			tramp_str = "".join([f"{i.mnemonic} {i.op_str}\\n" for i in self.cs.disasm(self.src[hook[0]:hook[0]+8], 0)])

			part1 += template_part1.format(name=hook[1], string=tramp_str, addr=hex(hook[0]))
			part2 += template_part2.format(name=hook[1], addr=hex(hook[0]))

		out = template_whole.format(part1=part1, part2=part2)

		text = ""
		try:
			text = open(dest, 'r').read()
		except:
			pass

		if text != out:
			open(dest, 'w').write(out)
