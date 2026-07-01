main:
addi ra, x0, #10 ;test
addi t0, x0, #1
loop:
sub ra, ra, t0
bne ra, t0 loop