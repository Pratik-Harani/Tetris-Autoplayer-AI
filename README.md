# Tetris Autoplayer AI


<img width="432" height="620" alt="Game in-progress with the autoplayer, random seed" src="https://github.com/user-attachments/assets/e6e78000-d4f4-4cab-a508-d018daa70eda" />

## Overview

A Python-based Tetris AI that evaluates board states to optimize for high-scoring 4-line clears. 

By relying on a carefully tuned multi-feature heuristic, this autoplayer ranked in the top 10% of a 200-student live leaderboard.




## The Heuristic Algorithm

The AI determines its next move by simulating all possible placements and rotations for the falling tetromino. It scores the resulting board state using a weighted sum of several heuristic features, executing the move that yields the optimal score.

| Heuristic Feature | Purpose in the Algorithm |
| --- | --- |
| **completedLines** | Rewards clearing rows, weighted heavily to setup and execute 4-line clears. |
| **holes** | Heavily penalizes empty spaces trapped beneath landed blocks. |
| **bumpiness** | Penalizes the height variation between adjacent columns to maintain a flat surface. |
| **aggregateHeight** | Penalizes the sum of all column heights to keep the overall stack low. |
| **maxHeight** | Penalizes the absolute highest point on the board to prevent the game from ending. |
| **rightmostCol** | Custom weight managing the rightmost column to preserve the I-piece drop zone. |

## Custom Game Variant

This specific Tetris variant features unique mechanics that added constraints to the autoplayer design:

* The game operates on a hard limit of exactly 400 tetrominos.
* Scoring is heavily biased toward multi-line clears (e.g., clearing 4 rows awards 1600 points).
* The player is given an inventory of 10 piece discards.
* The player is given 5 bombs that destroy immediately surrounding blocks.

## How to Run

The autoplayer requires Python 3. The Pygame interface is highly recommended as it performs the fastest during automated play.

1. Install the required Pygame module by running `pip install pygame`.
2. Launch the AI using the Pygame interface with `python visual-pygame.py`.
3. Alternatively, launch the standard visual interface with `python visual.py`.
4. To play the game manually, append the manual flag by running `python visual-pygame.py -m`.

> **Note:** Depending on your environment, you may need to substitute `python` and `pip` with `python3` and `pip3`.


## Acknowledgements
Based on game code from the UCL Design & Professional Skills module.
