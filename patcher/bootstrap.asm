main:
	; Push to stack
	stp x29, x30, [sp, #-0x70]!
	stp x19, x20, [sp, #0x10]
	stp x21, x22, [sp, #0x20]
	stp x23, x24, [sp, #0x30]
	stp x25, x26, [sp, #0x40]
	stp x27, x28, [sp, #0x50]
	stp d8, d9, [sp, #0x60]
	add x29, sp, #0x60
	; Save all parameters
	mov x19, x0
	mov x20, x1
	mov x21, x2
	mov x22, x3
	mov x23, x4
	mov x24, x5
	mov x25, x6
	mov x27, x13
	fmov d8, d0

	; Get findthehook
	bl $getfindhook
	mov x10, x0
	; Call findthehook
	mov x0, x27
	blr x10
	mov x10, x0
	; Call function returned from findthehook
	mov x0, x19
	mov x1, x20
	mov x2, x21
	mov x3, x22
	mov x4, x23
	mov x5, x24
	mov x6, x25
	fmov d0, d8
	blr x10
	; Cleanup
	ldp d8, d9, [sp, #0x60]
	ldp x27, x28, [sp, #0x50]
	ldp x25, x26, [sp, #0x40]
	ldp x23, x24, [sp, #0x30]
	ldp x21, x22, [sp, #0x20]
	ldp x19, x20, [sp, #0x10]
	ldp x29, x30, [sp], #0x70
	ret
getfindhook:
	stp x29, x30, [sp, #-0x20]!
	stp x19, x20, [sp, #0x10]

	; Check if it's cached
	adrp x20, adr@{cache_page}
	ldr x0, [x20, #{cache_offset}]
	cbnz x0, $findhookend

	; Call dlopen
	adrp x0, adr@{data1_page}
	add x0, x0, #{data1_offset} ; "@executable_path/hook.dylib"
	mov w1, #0x2
	bl @{dlopen_stub} ; dlopen
	; Call dlsym
	adrp x1, adr@{data2_page}
	add x1, x1, #{data2_offset} ; "findthehook"
	bl @{dlsym_stub} ; dlsym
	; Store in cache
	str x0, [x20, #{cache_offset}]
findhookend:
	ldp x19, x20, [sp, #0x10]
	ldp x29, x30, [sp], #0x20
	ret
