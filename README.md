# **Galactic Conquest (AI & Web Edition)**

A strategic space combat game featuring tactical power-ups and self-learning alien AI.

---

## **Implementation**:

- **Python Engine**: The core logic demostrating OOP, State Management , and Q-Learning logic.

- **Web Mission**: A JavaScript port for instant play in the browser.

---

Play Instantly! **[Click Here to Launch Mission](https://lushosly.github.io/tactical-tic-tac-toe/)**

**_Tip: Cmd ⌘ + Click (macOS) or Ctrl + Click (Windows/Linux) to open in a new tab._**

---

## **The "Alien" CPU** 

The Python source code (game.py) implements a reinforcement learning loop:

- **Serialization**: The battlefield state is serialized to a JSON hash map (ai_memory.json).

- **Experience**: The AI tracks every maneuver made during a battle.

- **Reinforcement**: Victory (+3) The AI "upvotes" successful tactics. ||
                   Defeat (-2) The AI "Downvotes" mistakes.
                   
- **Exploitation**: In future battles, the AI recognizes patterns and deploys the statistically best counter-attack. ---

---

## **Power Card** 

Commanders have a hand of 3 one-time-use weapons to disrupt the sector:

- **Orbital Strike**: Destroys any unit and leaves *radiation* (unplayable zone) for 1 turn. 

- **Mind Control**: Hacks an enemy *Asteroid* and converts it to your fleet. 

- **Asteroid** Deploys a permanent blockade that changes the map topology. 

---

## **Tech Stack** 

- **Language**: Python 3.10+ (OOP, JSON Persistence) 

- **Web Port**: HTML5, CSS3 (Grid Layout), JavaScript 

- **AI Concept**: Heuristic Search + Simplified Q-Learning 

=================================== **Developer** =================================

Luis J. Rodriguez Espinal

Software Engineer | AI & Automation
