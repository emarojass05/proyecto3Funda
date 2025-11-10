ADDI x1, x0, 10
ADDI x2, x0, 5
ADD  x3, x1, x2
SW   x3, 0(x0)
SUB  x4, x3, x2
SW   x4, 4(x0)
ADDI x5, x4, 2
SW   x5, 8(x0)
LW   x6, 0(x0)
LW   x7, 4(x0)
LW   x8, 8(x0)
ADD  x9, x6, x7
SUB  x10, x9, x8
SW   x10, 12(x0)
HALT
