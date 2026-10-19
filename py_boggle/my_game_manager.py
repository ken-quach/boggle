import copy
import random
from typing import List, Optional, Set, Tuple

from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.boggle_game import BoggleGame

"""
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************

If you worked in a group on this project, please type the EIDs of your groupmates below (do not include yourself).
Leave it as TODO otherwise.
Groupmate 1: TODO
Groupmate 2: TODO
"""

SHORT = 3
CUBE_SIDES = 6

class MyGameManager(BoggleGame):
    """Your implementation of `BoggleGame`
    """

    def __init__(self):
        """Constructs an empty Boggle Game.

        A newly-constructed game is unplayable.
        The `new_game` method will be called to initialize a playable game.
        Do not call `new_game` here.

        This method is provided for you, but feel free to change it.
        """

        self.board: List[List[str]] # current game board
        self.size: int # board size
        self.words: List[str] # player's current words
        self.dictionary: BoggleDictionary # the dictionary to use
        self.last_added_word: Optional[List[Tuple[int, int]]] # the position of the last added word, or None

    def new_game(self, size: int, cubefile: str, dictionary: BoggleDictionary) -> None:
        """This method is provided for you, but feel free to change it.
        """
        with open(cubefile, 'r') as infile:
            faces = [line.strip() for line in infile]
        cubes = [f.lower() for f in faces if len(f) == CUBE_SIDES]
        if size < 2 or len(cubes) < size*size:
            raise ValueError('ERROR: Invalid Dimensions (size, cubes)')
        random.shuffle(cubes)
        # Set all of the game parameters
        self.board =[[random.choice(cubes[r*size + c]) 
                    for r in range(size)] for c in range(size)]
        self.size = size
        self.words = []
        self.dictionary = dictionary
        self.last_added_word = None


    def get_board(self) -> List[List[str]]:
        """This method is provided for you, but feel free to change it.
        """
        return self.board

    def find_word_in_board(self, word: str) -> Optional[List[Tuple[int, int]]]:
        """Helper method called by add_word()
        Expected behavior:
        Returns an ordered list of coordinates of a word on the board in the same format as get_last_added_word()
        (see documentation in boggle_game.py).
        If `word` is not present on the board, return None.
        """
        word = word.lower()
        if not word:
            return None

        rows = len(self.board)
        cols = len(self.board[0])

        def dfs(row, col, index, visited, path):
            # Check board boundaries
            if row < 0 or row >= rows or col < 0 or col >= cols:
                return None

            # Cannot reuse a square
            if (row, col) in visited:
                return None

            # Letter must match
            if self.board[row][col].lower() != word[index]:
                return None

            visited.add((row, col))
            path.append((row, col))

            # Entire word found
            if index == len(word) - 1:
                return path.copy()

            # Search all eight neighbors
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue

                    result = dfs(
                        row + dr,
                        col + dc,
                        index + 1,
                        visited,
                        path
                    )

                    if result is not None:
                        return result

            # Backtrack if this path fails
            visited.remove((row, col))
            path.pop()

            return None

        # Try every square as the starting position
        for row in range(rows):
            for col in range(cols):
                result = dfs(row, col, 0, set(), [])

                if result is not None:
                    return result

        return None

    def add_word(self, word: str) -> int:
        """This method is provided for you, but feel free to change it.
        """
        word = word.lower()
        if (len(word) > SHORT and word not in self.words and self.dictionary.contains(word)):
            location = self.find_word_in_board(word)
            if location is not None:
                self.last_added_word = location
                self.words.append(word)
                return len(word) - SHORT
        return 0

    def get_last_added_word(self) -> Optional[List[Tuple[int, int]]]:
        """This method is provided for you, but feel free to change it.
        """
        return self.last_added_word

    def set_game(self, board: List[List[str]]) -> None:
        """This method is provided for you, but feel free to change it.
        """
        self.board = [[c.lower() for c in row] for row in board]

        self.size = len(board)
        self.words = set()
        self.last_added_word = []

    def get_score(self) -> int:
        """This method is provided for you, but feel free to change it.
        """
        return sum([len(word) - SHORT for word in self.words])

    def dictionary_driven_search(self) -> Set[str]:
        """Find all words using a dictionary-driven search.

        The dictionary-driven search attempts to find every word in the
        dictionary on the board.

        Returns:
            A set containing all words found on the board.
        """
        found_words = set()

        for word in self.dictionary:
            if len(word) < 4:
                continue

            if self.find_word_in_board(word) is not None:
                found_words.add(word)

        return found_words

    def board_driven_search(self) -> Set[str]:
        """Find all words using a board-driven search.

        The board-driven search constructs a string using every path on
        the board and checks whether each string is a valid word in the
        dictionary.

        Returns:
            A set containing all words found on the board.
        """
        found_words = set()

        rows = len(self.board)
        if rows == 0:
            return found_words

        cols = len(self.board[0])

        def dfs(row, col, current_word, visited):
            if (row, col) in visited:
                return

            word = current_word + self.board[row][col].lower()

            # Stop if no dictionary word starts with this prefix
            if not self.dictionary.is_prefix(word):
                return

            # Save complete words of at least four letters
            if len(word) >= 4 and self.dictionary.contains(word):
                found_words.add(word)

            visited.add((row, col))

            # Explore all eight neighboring cells
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue

                    next_row = row + dr
                    next_col = col + dc

                    if 0 <= next_row < rows and 0 <= next_col < cols:
                        dfs(next_row, next_col, word, visited)

            # Backtrack
            visited.remove((row, col))

        # Start searching from every cell
        for row in range(rows):
            for col in range(cols):
                dfs(row, col, "", set())

        return found_words
