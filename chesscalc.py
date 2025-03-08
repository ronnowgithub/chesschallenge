'''
Created on Oct 27, 2020

@author: lars
'''
import time
import sys
from math import factorial
xrange = range

class UnavailableSquareException(BaseException):
    pass

# Definition of Chess Pieces and stuff. Truely overkill
# anywaym each piece knows it's own movement.
# movement is a list of indicated directions, and a bool to indicate if we need to follow directions
class Movement(object):
    def __init__(self, directions, restricted=False):
        self.directions = directions
        self.restricted = restricted #TODO better name e.g. indicate_directions
        
class Piece(object):
    def __init__(self):
        self.symbol = '4'
    def Moves(self):
        raise NotImplementedError("must override Moves method in subclass of Piece")
    def __str__(self):
        return self.symbol
    
class Knight(Piece):
    def __init__(self):
        self.symbol = "N"
    def Moves(self):
        knightmoves = [[1,2],[1,-2],[-1,2],[-1,-2],[2,1],[2,-1],[-2,1],[-2,-1]]
        return Movement(knightmoves, True)
    
class King(Piece):
    def __init__(self):
        self.symbol = "K"
    def Moves(self):
        kingmoves = [[1,0],[1,-1],[1,1],[0,-1],[0,1],[-1,0],[-1,-1],[-1,1]]
        return Movement(kingmoves, True)

class Queen(Piece):
    def __init__(self):
        self.symbol = "Q"
    def Moves(self):
        queenmoves = [[1,0],[1,-1],[1,1],[0,-1],[0,1],[-1,0],[-1,-1],[-1,1]]
        return Movement(queenmoves, False)

class Bishop(Piece):
    def __init__(self):
        self.symbol = "B"
    def Moves(self):
        bishopmoves = [[1,-1],[1,1],[-1,-1],[-1,1]]
        return Movement(bishopmoves, False)

class Rook(Piece):
    def __init__(self):
        self.symbol = "R"
    def Moves(self):
        rookmoves = [[1,0],[0,-1],[0,1],[-1,0]]
        return Movement(rookmoves, False)

# --------------------------
# This guy is important
# a square is always a tuple (row, column)
# if a solution is made, we only want to keep track of where pieces are plased
# bla bla
class BoardPiece(object):
    def __init__(self, piece, square):
        self.piece = piece
        self.square = square
#mostly for debugging - could be removed  
    def __str__(self):
        return self.piece.symbol + str(self.square)
    def __repr__(self):
        return self.__str__()

# --------------------------
# This guy is key
# a square is always a tuple (row, column)
#  - we have TryAddPiece, which will add a piece to the square if possible
#  - we have GetAvailSquares; returns a list of squares that is available for placing a piece
#  - And then RemoveLastPiece; if we need to move on, the last piece of a solution we have to rm
#  - and some helper funcs...
#  - attackmap is a map of the board indicating (how many) a squaare is attacked. Useful for calcullating avail squarres
class Board(object):
    def __init__(self, rows, columns, boardpieces=[]):
        self.pieces = []
        self.rows, self.columns = rows, columns
        self.attackmap = [[0] * columns for _ in xrange(rows)]
        for pcs in boardpieces:
            self.TryPlacePiece(pcs.piece, pcs.square)
    
    def _inbounds(self, square):
        if square[0] >= 0 and square[0] < self.rows and square[1] >= 0 and square[1] < self.columns:
            return True
        return False
    
    def _isSquareOccupied(self, square):
        for pcs in self.pieces:
            if pcs.square == square:
                return True
        return False
    
    def _isSquareAttacked(self, square):
        return self.attackmap[square[0]][square[1]] > 0
                

    def GetAvailSquares(self):
        res = []
        for row in xrange(self.rows):
            for col in xrange(self.columns):
                sq = (row, col)
                if self._isSquareAttacked(sq) or self._isSquareOccupied(sq):
                    continue
                res.append(sq)
        return res             
    
    def TryPlacePiece(self, piece, square):
        squares_to_check = self._getSquaresToCheck(piece, square)
#        if squares_to_check == [] or any(map(lambda sq: self._isSquareOccupied(sq), squares_to_check)):
        if any(map(lambda sq: self._isSquareOccupied(sq), squares_to_check)):
            raise UnavailableSquareException()
        else:
            self.pieces.append(BoardPiece(piece, square))
            for sq in squares_to_check:
                self.attackmap[sq[0]][sq[1]] += 1
                
    def RemoveLastPiece(self):
        bpcs = self.pieces.pop()
        for sq in self._getSquaresToCheck(bpcs.piece, bpcs.square):
            self.attackmap[sq[0]][sq[1]] -= 1     
        
    def _getSquaresToCheck(self, piece, square):
        res = []
        movement = piece.Moves()
        #sq = (square[0], square[1])
        for direction in movement.directions:
            sq = (square[0] + direction[0], square[1] + direction[1])
            while self._inbounds(sq):
                res.append(sq)
                if movement.restricted:
                    break
                else:
                    sq = (sq[0] + direction[0], sq[1] + direction[1])
        return res  
    def __str__(self):
        res = '\n'
        s = ", ".join(map(str, self.pieces))
        s+= '\n'
        res += s
        for r in self.attackmap:
            res +=  "|".join(map(str,r))
            res += '\n'
        return res
    def __repr__(self):
        return self.__str__()

    
# The main loop
# recursive, just place a piece on any free suare? Of course break out when we do have a solution
# it will return the number of results found - yep all results regardless of dup's
def CalcSolutionForPieces(curboard, pieces):
    results = 0
    if len(pieces) == 0:
        return 1
    else:
        avsq = curboard.GetAvailSquares()
        for sq in avsq:
            try:
                curboard.TryPlacePiece(pieces[0], sq)
                results += CalcSolutionForPieces(curboard, pieces[1:])
                curboard.RemoveLastPiece()
            except UnavailableSquareException: 
                continue
    return results


# from our "main loop" we will get ALL possible results. 
# this is only true if all pieces are of distinct kinds.
# So the number of results need to get adjusted for that,,,
# Doh! not to sure, but each piece of a kind will permute in the final solution set. So we divide for that!
# but that's the mutant factor
 
def main(rows, columns, pieces):
    def _calc_mutant_factor():
        mutantcalc = {}
        mutantfactor = 1
        for pcs in pieces:
            if pcs.symbol in mutantcalc:
                mutantcalc[pcs.symbol] += 1
            else:
                mutantcalc[pcs.symbol] = 1
        for m in mutantcalc:
            mutantfactor *= factorial(mutantcalc[m])
        return mutantfactor
    curboard = Board(rows, columns)
    results = CalcSolutionForPieces(curboard, pieces)
    return results / _calc_mutant_factor()
        
        

if __name__ == '__main__':
    def constructPiecesFromStr(pieces: str) -> list:
        rval = []
        constructorArr = {
            "K": King(),
            "Q": Queen(),
            "N": Knight(),
            "B": Bishop(),
            "R": Rook()
        }
        for piece in pieces:
            rval.append(constructorArr[piece])
        return rval

    rows = 6
    cols = 9
    pieces = "QRBNKK"

    try:
        args = sys.argv[1:]
        if 3 == len(args):
            rows = int(args[0])
            cols = int(args[1])
            pieces = args[2]
        elif 0 != len(args):
            raise Exception() 
    except(Exception):
        print("Input was wrong. Use either no args or rows cols pieces\n")
        exit (1)

    argsToMain = [rows, cols, constructPiecesFromStr(pieces)]
    starttime = time.time()

    res = main(*argsToMain)
    #res = main(4,4,[Rook(), Rook(), Knight(), Knight(), Knight(), Knight()])
    #res = main(4, 4, [Knight(), Rook()])
    #res = main(3, 3, [Knight(), Bishop()])
    #res = main(3, 3, [Queen()])
    #res = main(3, 3, [Rook(), Rook(), Rook()])
    #res = main(8, 8, [Queen(), Queen(), Queen(), Queen(), Queen(), Queen(), Queen(), Queen()])

    #org problem
    #res = main(6,9,[Queen(), Rook(), Bishop(), Knight(), King(), King()])
    
    endtime = time.time()
    print ("# unique solutions: %i" % res)
    print ("Time to compute: %s" % str(endtime-starttime))
    
    
    
