00300093    # ADDI x1, x0, 3
00000113    # ADDI x2, x0, 0
00100193    # ADDI x3, x0, 1
00200213    # ADDI x4, x0, 2
00300293    # ADDI x5, x0, 3
00312023    # SW   x3, 0(x2)
00412223    # SW   x4, 4(x2)
00512423    # SW   x5, 8(x2)
00000313    # ADDI x6, x0, 0
00000393    # ADDI x7, x0, 0
0003A403    # LW   x8, 0(x7)
00830333    # ADD  x6, x6, x8
00438393    # ADDI x7, x7, 4
FFF08093    # ADDI x1, x1, -1
FE0098E3    # BNE  x1, x0, loop
00612623    # SW   x6, 12(x2)
0000006F    # JAL  x0, 0  (bucle infinito; puedes cambiarlo por tu encoding de HALT)
