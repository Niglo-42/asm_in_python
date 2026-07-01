const N 8

addi t2, x0, N
loop:
read_file t0, t1
beq t0, s1 end_loop; on comp avec \0
sw t2, t0
addi t2, t2, #1
addi t1, t1, #4
beq x0, x0 loop
end_loop:
jalr x0, N