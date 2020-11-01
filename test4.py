'''
Created on Oct 27, 2020

@author: lars
'''
import time
from math import factorial

class UnavailableSquareException(BaseException):
    pass

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

class BoardPiece(object):
    def __init__(self, piece, square):
        self.piece = piece
        self.square = square
        
    def SetSquare(self, square, bounds):
        pass
    def __str__(self):
        return self.piece.symbol + str(self.square)
    def __repr__(self):
        return self.__str__()
    
class Board(object):
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
                
    def __init__(self, rows, columns, boardpieces=[]):
        self.pieces = []
        self.rows, self.columns = rows, columns
        self.attackmap = [[0] * columns for _ in xrange(rows)]
        for pcs in boardpieces:
            self.TryPlacePiece(pcs.piece, pcs.square)
        
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
        if squares_to_check == [] or any(map(lambda sq: self._isSquareOccupied(sq), squares_to_check)):
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
        #TODO We can already abandon search if we find a piece - obvious place to optimize
        res = []
        movement = piece.Moves()
        #sq = (square[0], square[1])
        for direction in movement.directions:
            sq = (square[0] + direction[0], square[1] + direction[1])
            while self._inbounds(sq):
#                if isinstance(self._getSquare(sq), Piece):
#                    return []
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
    starttime = time.time()
    #res = main(3,3,[King(), King(), Rook()])
    #res = main(4,4,[Rook(), Rook(), Knight(), Knight(), Knight(), Knight()])
    #res = main(6,6,[Queen(), Queen(), King(), King(), Bishop(), Bishop(), Knight()])
    #res = res / (2*(4*2*3))
    res = main(6,9,[Queen(), Rook(), Bishop(), Knight(), King(), King()])
    #res = main(6,9,[Queen(), Rook(), Bishop(), Knight(), King(), King()])
    #res = main(5,5,[King(), King(), Queen(), Bishop(), Knight(), Rook()])
    endtime = time.time()
    #for b in res:
    #    print b  
    print "# unique solutions: %i" % res
    print "Time to compute: %s" % str(endtime-starttime)
    
    
    