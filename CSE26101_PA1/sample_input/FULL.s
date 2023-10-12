	.data
point1:	.word	0
array1:	.word	3
	.word	123
	.word	4346
point2:	.word	0xff2d
array2:	.word	0x11111111
	.text
main:
	add	$1, $1, $0
rtypes:
	sll	$1, $1, 3
	srl	$1, $1, 2
	jr	$1
	add	$1, $1, $0
	addu	$1, $1, $0
	sub	$1, $1, $0
	subu	$1, $1, $0
	and	$1, $1, $0
	or	$1, $1, $0
	nor	$1, $1, $0
	slt	$1, $1, $0
	sltu	$1, $1, $0
itypes:
	beq	$1, $1, rtypes
	bne	$1, $1, jtypes
	addi	$1, $1, 2
	addi	$1, $1, -3
	addi	$1, $1, 0x3f
	addiu	$1, $1, 65535
	addiu	$1, $1, 0xfff0
	slti	$1, $1, 2
	slti	$1, $1, -3
	slti	$1, $1, 0x3f
	sltiu	$1, $1, 65535
	sltiu	$1, $1, 0xfff0
	andi	$1, $1, 2
	andi	$1, $1, 0x3f
	ori	$1, $1, 2
	ori	$1, $1, 0x3f
	lui	$1, 2
	lui	$1, -3
	lui	$1, 0x3f
	lw	$12, -4($3)
	lw	$13, 0($3)
	lw	$13, 0x3f($3)
	sw	$12, -4($3)
	sw	$13, 0($3)
	sw	$13, 0x3f($3)
jtypes:
	j	point2
	jal	array1
specialtypes:
	la	$1, rtypes
	la	$1, itypes
	la	$1, jtypes
	la	$1, point1
	la	$1, array1
	la	$1, point2
	la	$1, array2
	move	$1, $2
	blt	$1,	$2,	rtypes
	blt	$1,	$2, itypes
	blt	$1,	$2, jtypes
	blt	$1,	$2, point1
	blt	$1,	$2, array1
	blt	$1,	$2, point2
	blt	$1,	$2, array2
	push	$1
	pop	$2
