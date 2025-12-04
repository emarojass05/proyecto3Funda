        ADDI x1, x0, 3          # contador = 3 (número de elementos)
        ADDI x2, x0, 0          # base de memoria = 0
        ADDI x3, x0, 1          # valor 1
        ADDI x4, x0, 2          # valor 2
        ADDI x5, x0, 3          # valor 3

        SW   x3, 0(x2)          # Mem[0]  = 1
        SW   x4, 4(x2)          # Mem[4]  = 2
        SW   x5, 8(x2)          # Mem[8]  = 3

        ADDI x6, x0, 0          # acumulador = 0
        ADDI x7, x0, 0          # puntero   = 0

loop:   LW   x8, 0(x2)          # carga desde Mem[x2 + 0]
        ADD  x6, x6, x8         # suma acumulador += valor
        ADDI x2, x2, 4          # avanza a siguiente dirección
        ADDI x1, x1, -1         # decrementa contador
        BNE  x1, x0, loop       # si contador ≠ 0, repetir

        SW   x6, 12(x2)         # guarda suma final
        HALT                    # fin del programa
