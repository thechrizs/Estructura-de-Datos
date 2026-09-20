import os

# Códigos de color ANSI para la terminal
COLOR_BLANCO = "\033[94m"   # Azul para fichas blancas
COLOR_ROJO = "\033[91m"     # Rojo para fichas rojas
COLOR_RESET = "\033[0m"     
COLOR_TABLERO = "\033[90m"  # Gris bordes

class TableroDamas:
    def __init__(self):
        self.tablero = [
            ['.', 'R', '.', 'R', '.', 'R', '.', 'R'], 
            ['R', '.', 'R', '.', 'R', '.', 'R', '.'], 
            ['.', '.', '.', '.', '.', '.', '.', '.'], 
            ['.', '.', '.', '.', '.', '.', '.', '.'], 
            ['.', '.', '.', '.', '.', '.', '.', '.'], # Filas
            ['.', '.', '.', '.', '.', '.', '.', '.'], 
            ['.', 'B', '.', 'B', '.', 'B', '.', 'B'], 
            ['B', '.', 'B', '.', 'B', '.', 'B', '.']  
        ]
        self.turno = 'B'
        self.ficha_encadenada = None

    def mostrar_tablero(self):
        print(f"{COLOR_TABLERO}\n  +---+---+---+---+---+---+---+---+{COLOR_RESET}")
        for i, fila in enumerate(self.tablero):
            num_fila = 8 - i
            linea = f"{COLOR_TABLERO}{num_fila} |{COLOR_RESET}"
            
            for char in fila:
                if 'B' in char:
                    linea += f"{COLOR_BLANCO}{char:^3}{COLOR_RESET}{COLOR_TABLERO}|{COLOR_RESET}"
                elif 'R' in char:
                    linea += f"{COLOR_ROJO}{char:^3}{COLOR_RESET}{COLOR_TABLERO}|{COLOR_RESET}"
                else:
                    linea += f" . {COLOR_TABLERO}|{COLOR_RESET}"
            
            print(linea)
            print(f"{COLOR_TABLERO}  +---+---+---+---+---+---+---+---+{COLOR_RESET}")
        print("    A   B   C   D   E   F   G   H\n")

    def notacion_a_coordenadas(self, notacion):
        if len(notacion) != 2:
            return None
        col_char, fila_char = notacion[0].upper(), notacion[1]
        cols = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
        
        if col_char in cols and fila_char.isdigit():
            fila = 8 - int(fila_char)
            col = cols[col_char]
            if 0 <= fila <= 7:
                return fila, col
        return None

    def es_enemigo(self, pieza_origen, pieza_destino):
        if pieza_destino == '.':
            return False
        # Es enemigo si la ultima letra (B o R) es diferente
        return pieza_origen[-1] != pieza_destino[-1]

    def obtener_capturas_posibles(self, f, c):
        pieza = self.tablero[f][c]
        if pieza == '.' or not pieza.endswith(self.turno):
            return []

        capturas = []
        direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for df, dc in direcciones:
            f_inter, c_inter = f + df, c + dc
            f_dest, c_dest = f + (df * 2), c + (dc * 2)

            if 0 <= f_dest <= 7 and 0 <= c_dest <= 7:
                pieza_inter = self.tablero[f_inter][c_inter]
                pieza_dest = self.tablero[f_dest][c_dest]
                if self.es_enemigo(pieza, pieza_inter) and pieza_dest == '.':
                    capturas.append((df, dc))
        return capturas

    def existe_alguna_captura_global(self):
        if self.ficha_encadenada:
            f, c = self.ficha_encadenada
            return len(self.obtener_capturas_posibles(f, c)) > 0

        for f in range(8):
            for c in range(8):
                if self.tablero[f][c].endswith(self.turno):
                    if len(self.obtener_capturas_posibles(f, c)) > 0:
                        return True
        return False

    def obtener_movimientos_legales_ficha(self, f, c):
        pieza = self.tablero[f][c]
        if pieza == '.' or not pieza.endswith(self.turno):
            return []

        es_dama = 'D' in pieza
        movimientos = []
        direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for df, dc in direcciones:
            es_adelante = (df == -1 if self.turno == 'B' else df == 1)

            if es_dama or es_adelante:
                f_dest, c_dest = f + df, c + dc
                if 0 <= f_dest <= 7 and 0 <= c_dest <= 7:
                    if self.tablero[f_dest][c_dest] == '.':
                        movimientos.append((df, dc, False))

            f_inter, c_inter = f + df, c + dc
            f_dest, c_dest = f + (df * 2), c + (dc * 2)
            if 0 <= f_dest <= 7 and 0 <= c_dest <= 7:
                if self.es_enemigo(pieza, self.tablero[f_inter][c_inter]) and self.tablero[f_dest][c_dest] == '.':
                    movimientos.append((df, dc, True))

        return movimientos

    def tiene_movimientos_disponibles(self):
        for f in range(8):
            for c in range(8):
                if self.tablero[f][c].endswith(self.turno):
                    if len(self.obtener_movimientos_legales_ficha(f, c)) > 0:
                        return True
        return False

    def verificar_coronacion(self, f, c):
        pieza = self.tablero[f][c]
        if pieza == 'B' and f == 0:
            self.tablero[f][c] = 'DB'
            print("👑 ¡Ficha Blanca coronada como REINA (DB)!")
        elif pieza == 'R' and f == 7:
            self.tablero[f][c] = 'DR'
            print("👑 ¡Ficha Roja coronada como REINA (DR)!")

    def contar_fichas(self):
        blancas = sum(sum(1 for c in fila if 'B' in c) for fila in self.tablero)
        rojas = sum(sum(1 for c in fila if 'R' in c) for fila in self.tablero)
        return blancas, rojas

    def mover(self, origen_str, direccion_str):
        coor_origen = self.notacion_a_coordenadas(origen_str)
        if not coor_origen:
            print(" Coordenada inválida. Usa el formato 'B2', 'C3', etc.")
            return False

        f_orig, c_orig = coor_origen

        if self.ficha_encadenada and (f_orig, c_orig) != self.ficha_encadenada:
            pos_str = f"{chr(65+self.ficha_encadenada[1])}{8-self.ficha_encadenada[0]}"
            print(f" Debes seguir moviendo la ficha en {pos_str} para completar la captura.")
            return False

        pieza = self.tablero[f_orig][c_orig]
        if not pieza.endswith(self.turno):
            print(f" Es el turno de las fichas '{self.turno}'. Selecciona una pieza válida.")
            return False

        dir_map = {
            'izq': (-1 if self.turno == 'B' else 1, -1),
            'der': (-1 if self.turno == 'B' else 1, 1),
            'a-izq': (1 if self.turno == 'B' else -1, -1),
            'a-der': (1 if self.turno == 'B' else -1, 1)
        }

        dir_lower = direccion_str.lower()
        if dir_lower not in dir_map:
            print(" Dirección inválida. Usa: 'izq', 'der', 'a-izq' (atrás izq) o 'a-der' (atrás der).")
            return False

        df_paso, dc_paso = dir_map[dir_lower]

        if c_orig + dc_paso < 0:
            print(" Estás en el límite izquierdo del tablero.")
            return False
        if c_orig + dc_paso > 7:
            print(" Estás en el límite derecho del tablero.")
            return False

        es_dama = 'D' in pieza
        hay_captura_obligatoria = self.existe_alguna_captura_global()

        # Probar Captura (2 casillas)
        f_dest_c, c_dest_c = f_orig + (df_paso * 2), c_orig + (dc_paso * 2)
        f_inter, c_inter = f_orig + df_paso, c_orig + dc_paso

        if 0 <= f_dest_c <= 7 and 0 <= c_dest_c <= 7:
            if self.es_enemigo(pieza, self.tablero[f_inter][c_inter]) and self.tablero[f_dest_c][c_dest_c] == '.':
                self.tablero[f_dest_c][c_dest_c] = pieza
                self.tablero[f_orig][c_orig] = '.'
                self.tablero[f_inter][c_inter] = '.'
                
                print(f"¡Captura realizada en ({chr(65+c_inter)}{8-f_inter})!")
                self.verificar_coronacion(f_dest_c, c_dest_c)

                if len(self.obtener_capturas_posibles(f_dest_c, c_dest_c)) > 0:
                    self.ficha_encadenada = (f_dest_c, c_dest_c)
                    print(f" ¡Captura múltiple disponible! Vuelve a mover la ficha en {chr(65+c_dest_c)}{8-f_dest_c}.")
                else:
                    self.ficha_encadenada = None
                    self.cambiar_turno()
                return True

        # Probar Movimiento Simple (1 casilla)
        if hay_captura_obligatoria:
            print(" ¡Regla de captura obligatoria! Tienes una captura disponible en el tablero.")
            return False

        es_retroceso = (df_paso == 1 if self.turno == 'B' else df_paso == -1)
        if es_retroceso and not es_dama:
            print(" Las fichas normales no pueden retroceder en un movimiento simple.")
            return False

        f_dest, c_dest = f_orig + df_paso, c_orig + dc_paso
        if 0 <= f_dest <= 7 and 0 <= c_dest <= 7:
            if self.tablero[f_dest][c_dest] == '.':
                self.tablero[f_dest][c_dest] = pieza
                self.tablero[f_orig][c_orig] = '.'
                self.verificar_coronacion(f_dest, c_dest)
                self.cambiar_turno()
                return True

        print(" Movimiento no permitido. Casilla de destino ocupada o bloqueada.")
        return False

    def cambiar_turno(self):
        self.turno = 'R' if self.turno == 'B' else 'B'

def jugar():
    juego = TableroDamas()
    print("=== JUEGO DE DAMAS EN TERMINAL ===")
    
    while True:
        juego.mostrar_tablero()
        blancas, rojas = juego.contar_fichas()

        if blancas == 0:
            print(f" Las fichas rojas ({COLOR_ROJO}R{COLOR_RESET}) han ganado!")
            break
        elif rojas == 0:
            print(f" Las fichas blancas ({COLOR_BLANCO}B{COLOR_RESET}) han ganado!")
            break

        if not juego.tiene_movimientos_disponibles():
            ganador = f"Rojas ({COLOR_ROJO}R{COLOR_RESET})" if juego.turno == 'B' else f"Blancas ({COLOR_BLANCO}B{COLOR_RESET})"
            perdedor = "Blancas" if juego.turno == 'B' else "Rojas"
            print(f" Las fichas {ganador} han ganado. Las {perdedor} no tienen movimientos válidos disponibles.")
            break

        turno_str = f"{COLOR_BLANCO}Blancas (B){COLOR_RESET}" if juego.turno == 'B' else f"{COLOR_ROJO}Rojas (R){COLOR_RESET}"
        print(f"Turno de las fichas: {turno_str}")
        print("Comandos: 'izq', 'der', 'a-izq' (atrás izq), 'a-der' (atrás der)")
        
        entrada = input("Ingresa movimiento (ej. 'B2 izq' o 'C3 a-der') o 'salir': ").strip().split()
        
        if len(entrada) > 0 and entrada[0].lower() == 'salir':
            print("¡Gracias por jugar!")
            break

        if len(entrada) == 2:
            juego.mover(entrada[0], entrada[1])
        else:
            print("Entrada inválida. Ingresa la casilla y la dirección (ejemplo: B2 izq).")

if __name__ == "__main__":
    jugar()