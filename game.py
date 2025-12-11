import os
import time
import random
import json
import sys

# === AI BRAIN ===
class AIBrain:
    def __init__(self, memory_file="ai_memory.json"):
        self.memory_file = memory_file
        self.memory = self.load_memory()
        self.match_history = [] 

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f)

    def get_state_key(self, board_cells):
        return "".join(board_cells)

    def record_move(self, board_cells, move):
        state = self.get_state_key(board_cells)
        self.match_history.append((state, move))

    def get_best_known_move(self, board_cells):
        state = self.get_state_key(board_cells)
        if state in self.memory:
            moves = self.memory[state]
            if moves:
                best_move = max(moves, key=moves.get)
                if moves[best_move] > 0:
                    return best_move
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
                cell_content = self.cells[i]
                if cell_content == " ": cell_content = "." # Space void
                if i in self.hazmat:
                    cell_content = "☢" 
                row_cells.append(cell_content)
            
            line = " | ".join(row_cells)
            print(f" {row+1}   {line}")
            if row < self.size - 1:
                print("    " + "+".join(["---"] * self.size))
        print("\n")

    def decay_hazmat(self):
        to_remove = []
        for idx in self.hazmat:
            self.hazmat[idx]['turns'] -= 1
            if self.hazmat[idx]['turns'] <= 0:
                to_remove.append(idx)
        for idx in to_remove:
            del self.hazmat[idx]

    def add_hazmat(self, index, owner_symbol):
        self.hazmat[index] = {'owner': owner_symbol, 'turns': 2}

    def update(self, position, symbol):
        if self.is_valid_move(position, symbol):
            self.cells[position] = symbol
            if position in self.hazmat:
                del self.hazmat[position]
            return True
        return False

    def is_valid_move(self, position, player_symbol):
        if not (0 <= position < (self.size * self.size)):
            return False
        if position in self.hazmat:
            if self.hazmat[position]['owner'] != player_symbol:
                return False
        return self.cells[position] == " "

    def is_full(self):
        return " " not in self.cells

    def check_winner(self, symbol):
        s = self.size
        # Rows
        for r in range(s):
            if all(self.cells[r*s + c] == symbol for c in range(s)): return True
        # Cols
        for c in range(s):
            if all(self.cells[r*s + c] == symbol for r in range(s)): return True
        # Diagonals
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
        self.powers = {"STRIKE": True, "HACK": True, "ASTEROID": True}

    def reset_powers(self):
        self.powers = {"STRIKE": True, "HACK": True, "ASTEROID": True}

    def show_powers(self):
        return [p for p, avail in self.powers.items() if avail]

class Game:
    def __init__(self):
        self.board = Board()
        # Symbols: Rocket vs UFO
        self.p1 = Player("Commander", "🚀", is_ai=False)
        self.p2 = None 
        self.current_player = None
        self.brain = AIBrain()
        self.mode = None 

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        while True:
            self.clear_screen()
            print("========================================")
            print("   🌌  GALACTIC CONQUEST (4x4)  🌌   ")
            print("========================================")
            print("1. Launch Mission (Start Game)")
            print("2. Tactical Briefing (Rules)")
            print("3. Abort (Exit)")
            print("========================================")
            choice = input("Select Option > ")

            if choice == '1':
                self.setup_match()
                self.game_loop()
            elif choice == '2':
                self.show_tutorial()
            elif choice == '3':
                print("Mission Aborted. Closing Comms.")
                sys.exit()

    def show_tutorial(self):
        self.clear_screen()
        print("=== TACTICAL BRIEFING ===")
        print("Objective: Align 4 Ships (🚀) to secure the sector.")
        print("\nARSENAL (One-time use):")
        print("1. STRIKE [Pos]   -> 'STRIKE 5'   (Orbital Strike: Clears cell, creates Radiation)")
        print("2. HACK [Pos]     -> 'HACK 9'     (Mind Control: Steals an enemy Asteroid)")
        print("3. ASTEROID [Pos] -> 'ASTEROID 2' (Deploy Blockade: Blocks a cell permanently)")
        print("\nCommands:")
        print("- Type a number '1-16' to move.")
        print("- Type Power Name + Number to use weapons.")
        print("- Type 'EXIT' to surrender sector.")
        input("\nPress Enter to return...")

    def setup_match(self):
        self.clear_screen()
        print("=== SELECT ENEMY ===")
        print("1. Training Sim (Human vs Human)")
        print("2. Live Combat (Human vs Alien AI)")
        choice = input("Option > ")
        
        self.mode = choice
        if choice == '2':
            self.p2 = Player("Alien Fleet", "🛸", is_ai=True)
        else:
            self.p2 = Player("Rival Fleet", "🛸", is_ai=False)
            
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
                self.post_game_menu()
            elif result == "EXIT":
                match_active = False

    def get_ai_move(self):
        print(f"📡 {self.current_player.name} calculating trajectory...")
        time.sleep(0.6)

        # 0. MEMORY CHECK
        if random.random() < 0.7:
            known_move = self.brain.get_best_known_move(self.board.cells)
            if known_move:
                cmd = known_move.split()
                is_valid = False
                if cmd[0].isdigit():
                    pos = int(cmd[0]) - 1
                    if self.board.is_valid_move(pos, self.current_player.symbol):
                        is_valid = True
                elif cmd[0] in ["STRIKE", "HACK", "ASTEROID"]:
                    if self.current_player.powers.get(cmd[0]): is_valid = True
                
                if is_valid:
                    print(f"AI utilizing combat memory!")
                    self.brain.record_move(self.board.cells, known_move)
                    return known_move

        move = self.calculate_heuristic_move()
        self.brain.record_move(self.board.cells, move)
        return move

    def calculate_heuristic_move(self):
        symbol = self.current_player.symbol
        opponent_symbol = "🚀" if symbol == "🛸" else "🛸"
        
        valid_empty = []
        for i in range(16):
            if self.board.is_valid_move(i, symbol): valid_empty.append(i)

        enemy_cells = [i for i, x in enumerate(self.board.cells) if x == opponent_symbol]
        block_cells = [i for i, x in enumerate(self.board.cells) if x == "☄️"]
        available_powers = self.current_player.show_powers()

        # 1. WIN NOW
        for cell in valid_empty:
            self.board.cells[cell] = symbol
            if self.board.check_winner(symbol):
                self.board.cells[cell] = " "
                return str(cell + 1)
            self.board.cells[cell] = " "

        # 2. HACK WIN (Convert Asteroid)
        if "HACK" in available_powers and block_cells:
            for cell in block_cells:
                self.board.cells[cell] = symbol
                if self.board.check_winner(symbol):
                    self.board.cells[cell] = "☄️"
                    return f"HACK {cell + 1}"
                self.board.cells[cell] = "☄️"

        # 3. BLOCK OPPONENT
        threat_cell = -1
        opponent_valid = []
        for i in range(16):
            if self.board.is_valid_move(i, opponent_symbol): opponent_valid.append(i)

        for cell in opponent_valid:
            self.board.cells[cell] = opponent_symbol
            if self.board.check_winner(opponent_symbol):
                threat_cell = cell
            self.board.cells[cell] = " "

        if threat_cell != -1:
            if "STRIKE" in available_powers and random.random() < 0.8:
                 return f"STRIKE {threat_cell + 1}"
            if threat_cell in valid_empty:
                return str(threat_cell + 1)

        # 4. TACTICAL STRIKE
        if "STRIKE" in available_powers and random.random() < 0.3 and enemy_cells:
            target = random.choice(enemy_cells)
            return f"STRIKE {target + 1}"

        # 5. RANDOM POWER
        if random.random() < 0.2 and available_powers:
            power = random.choice(available_powers)
            if power == "HACK" and block_cells:
                return f"HACK {random.choice(block_cells) + 1}"
            if power == "ASTEROID" and valid_empty:
                return f"ASTEROID {random.choice(valid_empty) + 1}"

        # 6. CENTER STRATEGY
        inner_core = [5, 6, 9, 10]
        for core in inner_core:
            if core in valid_empty: return str(core + 1)

        if valid_empty: return str(random.choice(valid_empty) + 1)
        return "1"

    def play_turn(self):
        self.clear_screen()
        print(f"=== SECTOR 4 CONTROL: {self.current_player.name} ===")
        print("Objective: Align 4 Units. (Type 'EXIT' to retreat)")
        self.board.display()
        print(f"Turn: {self.current_player.symbol}")
        
        powers = self.current_player.show_powers()
        print(f"Arsenal: {powers}")
        
        if self.current_player.is_ai:
            choice_str = self.get_ai_move()
        else:
            print("Command (1-16) OR Weapon (e.g. 'STRIKE 5') > ", end="")
            choice_str = input()

        choice = choice_str.upper().split()
        if not choice: return "CONTINUE"
        command = choice[0]

        if command == "EXIT": return "EXIT"

        # STANDARD MOVE
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
                    print("❌ Invalid Coordinates!")
                    time.sleep(1)

        # POWERS
        elif command in ["STRIKE", "HACK", "ASTEROID"] and len(choice) > 1:
            if self.use_power(command):
                pos = int(choice[1]) - 1
                success = False
                
                if command == "STRIKE" and 0 <= pos < 16:
                    self.board.cells[pos] = " "
                    self.board.add_hazmat(pos, self.current_player.symbol)
                    print(f"💥 ORBITAL STRIKE HIT SECTOR {pos+1}!")
                    success = True
                    
                elif command == "HACK" and 0 <= pos < 16 and self.board.cells[pos] == "☄️":
                    self.board.cells[pos] = self.current_player.symbol
                    print(f"👽 MIND CONTROL SUCCESSFUL AT {pos+1}!")
                    success = True

                elif command == "ASTEROID" and 0 <= pos < 16 and self.board.is_valid_move(pos, self.current_player.symbol):
                    self.board.cells[pos] = "☄️"
                    print(f"☄️ ASTEROID DEPLOYED AT {pos+1}!")
                    success = True

                if success:
                    time.sleep(2)
                    if self.board.check_winner(self.current_player.symbol):
                        return self.process_win(self.current_player)
                    self.switch_player()
                else:
                    print("❌ Target Invalid.")
                    self.refund_power(command)
                    time.sleep(1)
        
        return "CONTINUE"

    def use_power(self, power_name):
        if self.current_player.powers.get(power_name):
            self.current_player.powers[power_name] = False
            return True
        if not self.current_player.is_ai: print("❌ Weapon Depleted!")
        return False

    def refund_power(self, power_name):
        self.current_player.powers[power_name] = True

    def process_win(self, winner):
        self.clear_screen()
        self.board.display()
        print(f"\n🏆 {winner.name} CONQUERED THE SECTOR! 🏆\n")
        if self.p2.is_ai:
            if winner == self.p2: self.brain.learn('WIN')
            else: self.brain.learn('LOSS')
        input("Press Enter to debrief...")
        return "WIN"

    def process_draw(self):
        self.clear_screen()
        self.board.display()
        print("\n STALEMATE DETECTED. NO VICTOR. \n")
        if self.p2.is_ai: self.brain.learn('DRAW')
        input("Press Enter...")
        return "DRAW"

    def post_game_menu(self):
        while True:
            self.clear_screen()
            print("=== MISSION STATUS ===")
            print("1. Re-deploy (Restart)")
            print("2. Return to Base (Menu)")
            print("3. Dismiss (Exit)")
            choice = input("Option > ")

            if choice == '1':
                self.board.reset()
                self.p1.reset_powers()
                self.p2.reset_powers()
                self.current_player = self.p1
                self.game_loop() 
                break
            elif choice == '2': break 
            elif choice == '3': sys.exit()

if __name__ == "__main__":
    game = Game()
    game.main_menu()
