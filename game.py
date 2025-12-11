import os
import time
import random
import json
import sys

# === LOCALIZATION (I18N) ===
LANG = 'en' # Default

TEXT = {
    'en': {
        'menu_title': "🌌 GALACTIC CONQUEST (4x4) 🌌",
        'opt_start': "Launch Mission (Start Game)",
        'opt_rules': "Tactical Briefing (Rules)",
        'opt_exit': "Abort (Exit)",
        'opt_sel': "Select Option > ",
        'rules_title': "=== TACTICAL BRIEFING ===",
        'rules_obj': "Objective: Align 4 Ships (🚀) to secure the sector.",
        'rules_bomb': "1. STRIKE [Pos]   -> Clears cell, creates Radiation.",
        'rules_hack': "2. HACK [Pos]     -> Steals an enemy Asteroid (☄️).",
        'rules_block': "3. ASTEROID [Pos] -> Deploys a permanent blockade.",
        'rules_cmd': "Commands: Type number (1-16) or Power + Number (e.g., 'STRIKE 5').",
        'rules_ret': "\nPress Enter to return...",
        'bye': "Mission Aborted. Closing Comms.",
        'mode_title': "=== SELECT ENEMY ===",
        'mode_pvp': "1. Training Sim (Human vs Human)",
        'mode_pve': "2. Live Combat (Human vs Alien AI)",
        'p1': "Commander",
        'cpu': "Alien Fleet",
        'turn': "Turn",
        'arsenal': "Arsenal",
        'enter_cmd': "Command (1-16) OR Weapon > ",
        'thinking': "calculating trajectory...",
        'invalid': "❌ Invalid Coordinates! Sector occupied or radiated.",
        'win': "CONQUERED THE SECTOR!",
        'draw': "STALEMATE DETECTED.",
        'bomb_used': "ordered ORBITAL STRIKE on Sec-",
        'hack_used': "HACKED the asteroid at Sec-",
        'block_used': "dropped an ASTEROID on Sec-",
        'hack_fail': "❌ Mind Control only works on Asteroids (☄️)",
        'target_inv': "❌ Target Invalid.",
        'mem_used': "AI utilizing combat memory!",
        'weapon_empty': "❌ Weapon Depleted!"
    },
    'es': {
        'menu_title': "🌌 CONQUISTA GALÁCTICA (4x4) 🌌",
        'opt_start': "Iniciar Misión (Comenzar)",
        'opt_rules': "Informe Táctico (Reglas)",
        'opt_exit': "Abortar (Salir)",
        'opt_sel': "Seleccione Opción > ",
        'rules_title': "=== INFORME TÁCTICO ===",
        'rules_obj': "Objetivo: Alinear 4 Naves (🚀) para asegurar el sector.",
        'rules_bomb': "1. ATAQUE [Pos]   -> Limpia celda, crea Radiación.",
        'rules_hack': "2. HACK [Pos]     -> Roba un Asteroide (☄️) enemigo.",
        'rules_block': "3. ASTEROIDE [Pos] -> Despliega un bloqueo permanente.",
        'rules_cmd': "Comandos: Escribe número (1-16) o Poder + Número (ej. 'ATAQUE 5').",
        'rules_ret': "\nPresiona Enter para volver...",
        'bye': "Misión Abortada. Cerrando comunicación.",
        'mode_title': "=== SELECCIONAR ENEMIGO ===",
        'mode_pvp': "1. Simulación (Humano vs Humano)",
        'mode_pve': "2. Combate Real (Humano vs IA Alienígena)",
        'p1': "Comandante",
        'cpu': "Flota Alien",
        'turn': "Turno",
        'arsenal': "Arsenal",
        'enter_cmd': "Comando (1-16) O Arma > ",
        'thinking': "calculando trayectoria...",
        'invalid': "❌ ¡Coordenadas Inválidas! Sector ocupado o radiado.",
        'win': "¡CONQUISTÓ EL SECTOR!",
        'draw': "EMPATE DETECTADO.",
        'bomb_used': "ordenó ATAQUE ORBITAL en Sec-",
        'hack_used': "HACKEÓ el asteroide en Sec-",
        'block_used': "lanzó un ASTEROIDE en Sec-",
        'hack_fail': "❌ Hack solo funciona en Asteroides (☄️)",
        'target_inv': "❌ Objetivo Inválido.",
        'mem_used': "¡IA utilizando memoria de combate!",
        'weapon_empty': "❌ ¡Arma Agotada!"
    }
}

def t(key):
    return TEXT[LANG].get(key, key)

# === AI BRAIN ===
class AIBrain:
    def __init__(self, memory_file="ai_memory.json"):
        self.memory_file = memory_file
        self.memory = self.load_memory()
        self.match_history = [] 

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f: json.dump(self.memory, f)

    def get_state_key(self, board_cells): return "".join(board_cells)

    def record_move(self, board_cells, move):
        state = self.get_state_key(board_cells)
        self.match_history.append((state, move))

    def get_best_known_move(self, board_cells):
        state = self.get_state_key(board_cells)
        if state in self.memory:
            moves = self.memory[state]
            if moves:
                best_move = max(moves, key=moves.get)
                if moves[best_move] > 0: return best_move
        return None

    def learn(self, result):
        reward = 0
        if result == 'WIN': reward = 3
        elif result == 'LOSS': reward = -2
        elif result == 'DRAW': reward = 1
        for state, move in self.match_history:
            if state not in self.memory: self.memory[state] = {}
            if move not in self.memory[state]: self.memory[state][move] = 0
            self.memory[state][move] += reward
        self.save_memory()
        self.match_history = [] 

# === GAME LOGIC ===
class Board:
    def __init__(self):
        self.size = 4
        self.cells = [" " for _ in range(self.size * self.size)]
        self.hazmat = {} 

    def reset(self):
        self.cells = [" " for _ in range(self.size * self.size)]
        self.hazmat = {}

    def display(self):
        print("\n")
        print("     1   2   3   4")
        for row in range(self.size):
            start = row * self.size
            row_cells = []
            for i in range(start, start + self.size):
                c = self.cells[i]
                if c == " ": c = "."
                if i in self.hazmat: c = "☢"
                row_cells.append(c)
            line = " | ".join(row_cells)
            print(f" {row+1}   {line}")
            if row < self.size - 1: print("    " + "+".join(["---"] * self.size))
        print("\n")

    def decay_hazmat(self):
        to_remove = []
        for idx in self.hazmat:
            self.hazmat[idx]['turns'] -= 1
            if self.hazmat[idx]['turns'] <= 0: to_remove.append(idx)
        for idx in to_remove: del self.hazmat[idx]

    def add_hazmat(self, index, owner_symbol):
        self.hazmat[index] = {'owner': owner_symbol, 'turns': 2}

    def update(self, position, symbol):
        if self.is_valid_move(position, symbol):
            self.cells[position] = symbol
            if position in self.hazmat: del self.hazmat[position]
            return True
        return False

    def is_valid_move(self, position, player_symbol):
        if not (0 <= position < (self.size * self.size)): return False
        if position in self.hazmat:
            if self.hazmat[position]['owner'] != player_symbol: return False
        return self.cells[position] == " "

    def is_full(self): return " " not in self.cells

    def check_winner(self, symbol):
        s = self.size
        for r in range(s):
            if all(self.cells[r*s + c] == symbol for c in range(s)): return True
        for c in range(s):
            if all(self.cells[r*s + c] == symbol for r in range(s)): return True
        if all(self.cells[i * (s+1)] == symbol for i in range(s)): return True
        if all(self.cells[(i+1) * (s-1)] == symbol for i in range(s)): return True
        return False
    
    def get_empty_cells(self):
        return [i for i, x in enumerate(self.cells) if x == " "]

class Player:
    def __init__(self, name, symbol, is_ai=False):
        self.name = name
        self.symbol = symbol
        self.is_ai = is_ai
        # Powers keys remain English for logic, display is handled via print
        self.powers = {"STRIKE": True, "HACK": True, "ASTEROID": True}

    def reset_powers(self):
        self.powers = {"STRIKE": True, "HACK": True, "ASTEROID": True}

    def show_powers(self):
        # We translate the display logic in the game loop
        return [p for p, avail in self.powers.items() if avail]

class Game:
    def __init__(self):
        self.board = Board()
        self.p1 = None
        self.p2 = None 
        self.current_player = None
        self.brain = AIBrain()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def select_language(self):
        self.clear_screen()
        print("1. English")
        print("2. Español (Latinoamérica)")
        c = input("Select/Seleccione > ")
        global LANG
        if c == '2': LANG = 'es'
        else: LANG = 'en'

    def main_menu(self):
        self.select_language()
        while True:
            self.clear_screen()
            print("========================================")
            print(f"   {t('menu_title')}   ")
            print("========================================")
            print(f"1. {t('opt_start')}")
            print(f"2. {t('opt_rules')}")
            print(f"3. {t('opt_exit')}")
            print("========================================")
            choice = input(t('opt_sel'))

            if choice == '1':
                self.setup_match()
                self.game_loop()
            elif choice == '2':
                self.show_tutorial()
            elif choice == '3':
                print(t('bye'))
                sys.exit()

    def show_tutorial(self):
        self.clear_screen()
        print(t('rules_title'))
        print(t('rules_obj'))
        print("\n" + t('arsenal') + ":")
        print(t('rules_bomb'))
        print(t('rules_hack'))
        print(t('rules_block'))
        print("\n" + t('rules_cmd'))
        input(t('rules_ret'))

    def setup_match(self):
        self.clear_screen()
        print(t('mode_title'))
        print(t('mode_pvp'))
        print(t('mode_pve'))
        choice = input(t('opt_sel'))
        
        self.p1 = Player(t('p1'), "🚀", is_ai=False)
        
        if choice == '2':
            self.p2 = Player(t('cpu'), "🛸", is_ai=True)
        else:
            self.p2 = Player("Player 2", "🛸", is_ai=False)
            
        self.board.reset()
        self.p1.reset_powers()
        
        self.current_player = self.p1

    def switch_player(self):
        self.current_player = self.p2 if self.current_player == self.p1 else self.p1
        self.board.decay_hazmat()

    def game_loop(self):
        match_active = True
        while match_active:
            result = self.play_turn()
            if result == "WIN" or result == "DRAW":
                match_active = False
                # Simple pause then back to menu
                input(t('rules_ret'))
            elif result == "EXIT":
                match_active = False

    def get_ai_move(self):
        print(f"📡 {self.current_player.name} {t('thinking')}")
        time.sleep(0.6)

        if random.random() < 0.7:
            known_move = self.brain.get_best_known_move(self.board.cells)
            if known_move:
                cmd = known_move.split()
                is_valid = False
                if cmd[0].isdigit():
                    pos = int(cmd[0]) - 1
                    if self.board.is_valid_move(pos, self.current_player.symbol): is_valid = True
                elif cmd[0] in ["STRIKE", "HACK", "ASTEROID"]:
                    if self.current_player.powers.get(cmd[0]): is_valid = True
                
                if is_valid:
                    print(t('mem_used'))
                    self.brain.record_move(self.board.cells, known_move)
                    return known_move

        move = self.calculate_heuristic_move()
        self.brain.record_move(self.board.cells, move)
        return move

    def calculate_heuristic_move(self):
        # AI Logic Logic uses English keys "STRIKE", "HACK" etc internally
        symbol = self.current_player.symbol
        opponent_symbol = "🚀" if symbol == "🛸" else "🛸"
        valid_empty = []
        for i in range(16):
            if self.board.is_valid_move(i, symbol): valid_empty.append(i)

        enemy_cells = [i for i, x in enumerate(self.board.cells) if x == opponent_symbol]
        block_cells = [i for i, x in enumerate(self.board.cells) if x == "☄️"]
        available_powers = self.current_player.show_powers()

        # Win
        for cell in valid_empty:
            self.board.cells[cell] = symbol
            if self.board.check_winner(symbol):
                self.board.cells[cell] = " "
                return str(cell + 1)
            self.board.cells[cell] = " "

        # Hack
        if "HACK" in available_powers and block_cells:
            for cell in block_cells:
                self.board.cells[cell] = symbol
                if self.board.check_winner(symbol):
                    self.board.cells[cell] = "☄️"
                    return f"HACK {cell + 1}"
                self.board.cells[cell] = "☄️"

        # Block
        threat_cell = -1
        opponent_valid = []
        for i in range(16):
            if self.board.is_valid_move(i, opponent_symbol): opponent_valid.append(i)
        for cell in opponent_valid:
            self.board.cells[cell] = opponent_symbol
            if self.board.check_winner(opponent_symbol): threat_cell = cell
            self.board.cells[cell] = " "

        if threat_cell != -1:
            if "STRIKE" in available_powers and random.random() < 0.8: return f"STRIKE {threat_cell + 1}"
            if threat_cell in valid_empty: return str(threat_cell + 1)

        # Tactical
        if "STRIKE" in available_powers and random.random() < 0.3 and enemy_cells:
            target = random.choice(enemy_cells)
            return f"STRIKE {target + 1}"

        if random.random() < 0.2 and available_powers:
            power = random.choice(available_powers)
            if power == "HACK" and block_cells: return f"HACK {random.choice(block_cells) + 1}"
            if power == "ASTEROID" and valid_empty: return f"ASTEROID {random.choice(valid_empty) + 1}"

        inner_core = [5, 6, 9, 10]
        for core in inner_core:
            if core in valid_empty: return str(core + 1)

        if valid_empty: return str(random.choice(valid_empty) + 1)
        return "1"

    def play_turn(self):
        self.clear_screen()
        print(f"=== {t('menu_title')} ===")
        self.board.display()
        print(f"{t('turn')}: {self.current_player.name} ({self.current_player.symbol})")
        
        powers = self.current_player.show_powers()
        # Translate powers for display if ES
        display_powers = []
        if LANG == 'es':
            for p in powers:
                if p == 'STRIKE': display_powers.append("ATAQUE")
                elif p == 'HACK': display_powers.append("HACK")
                elif p == 'ASTEROID': display_powers.append("ASTEROIDE")
        else:
            display_powers = powers

        print(f"{t('arsenal')}: {display_powers}")
        
        if self.current_player.is_ai:
            choice_str = self.get_ai_move()
        else:
            print(t('enter_cmd'), end="")
            choice_str = input()

        choice = choice_str.upper().split()
        if not choice: return "CONTINUE"
        
        # Translate Spanish commands to English Keys for logic
        cmd_map = {'ATAQUE': 'STRIKE', 'HACK': 'HACK', 'ASTEROIDE': 'ASTEROID'}
        raw_cmd = choice[0]
        command = cmd_map.get(raw_cmd, raw_cmd) # defaults to English or Number

        if command == "EXIT": return "EXIT"

        if command.isdigit():
            pos = int(command) - 1
            if self.board.update(pos, self.current_player.symbol):
                if self.board.check_winner(self.current_player.symbol):
                    return self.process_win(self.current_player)
                elif self.board.is_full():
                    return self.process_draw()
                else:
                    self.switch_player()
            else:
                if not self.current_player.is_ai:
                    print(t('invalid'))
                    time.sleep(1)

        elif command in ["STRIKE", "HACK", "ASTEROID"] and len(choice) > 1:
            if self.use_power(command):
                pos = int(choice[1]) - 1
                success = False
                
                if command == "STRIKE" and 0 <= pos < 16:
                    self.board.cells[pos] = " "
                    self.board.add_hazmat(pos, self.current_player.symbol)
                    print(f"💥 {self.current_player.name} {t('bomb_used')}{pos+1}!")
                    success = True
                    
                elif command == "HACK" and 0 <= pos < 16 and self.board.cells[pos] == "☄️":
                    self.board.cells[pos] = self.current_player.symbol
                    print(f"👽 {self.current_player.name} {t('hack_used')}{pos+1}!")
                    success = True

                elif command == "ASTEROID" and 0 <= pos < 16 and self.board.is_valid_move(pos, self.current_player.symbol):
                    self.board.cells[pos] = "☄️"
                    print(f"☄️ {self.current_player.name} {t('block_used')}{pos+1}!")
                    success = True

                if success:
                    time.sleep(2)
                    if self.board.check_winner(self.current_player.symbol):
                        return self.process_win(self.current_player)
                    self.switch_player()
                else:
                    print(t('target_inv'))
                    self.refund_power(command)
                    time.sleep(1)
        
        return "CONTINUE"

    def use_power(self, power_name):
        if self.current_player.powers.get(power_name):
            self.current_player.powers[power_name] = False
            return True
        if not self.current_player.is_ai: print(t('weapon_empty'))
        return False

    def refund_power(self, power_name):
        self.current_player.powers[power_name] = True

    def process_win(self, winner):
        self.clear_screen()
        self.board.display()
        print(f"\n🏆 {winner.name} {t('win')} 🏆\n")
        if self.p2.is_ai:
            if winner == self.p2: self.brain.learn('WIN')
            else: self.brain.learn('LOSS')
        return "WIN"

    def process_draw(self):
        self.clear_screen()
        self.board.display()
        print(f"\n {t('draw')} \n")
        if self.p2.is_ai: self.brain.learn('DRAW')
        return "DRAW"

if __name__ == "__main__":
    game = Game()
    game.main_menu()
