'''
Created on Oct 27, 2020

@author: lars
'''
import copy
import abc
import time
import gc

#debug_stuff
copy_time = 0
try_place_piece_time = 0
square_creation_time = 0
check_uniqueness_time = 0

class UnavailableSquareException(BaseException):
    pass

class Movement(object):
    def __init__(self, directions, restricted=False):
        self.directions = directions
        self.restricted = restricted #TODO better name e.g. indicate_directions
    
class Square(object):
    def __init__(self, row, column):
        global square_creation_time
        t0 = time.time()
        self.row, self.column = row, column
        t1 = time.time()
        square_creation_time += t1-t0
    def __add__(self, direction_list): #TODO not __add__ this is not proper here
        return Square(self.row + direction_list[0], self.column + direction_list[1])
    def __str__(self):
        return "(%i,%i)" % (self.row, self.column)
    def __repr__(self):
        return self.__str__()

        
class Piece(object):
    def __init__(self):
        self.symbol = '4'
    def Moves(self):
        raise NotImplementedError("must override Moves method in subclass of Piece")
    def __str__(self):
        return self.symbol

class EmptySquare(object):
    def __init__(self):
        self.symbol = '.'
    def __str__(self):
        return self.symbol
              
class AttackedSquare(object):
    def __init__(self):
        self.symbol = '*'
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

class Board(object):
    def _inbounds(self, square):
#        return 0 <= square.row < self.rows and 0 <= square.column < self.colums:
            
        if square.row >= 0 and square.row < self.rows and square.column >= 0 and square.column < self.columns:
            return True
        return False
    def _setSquare(self, square, obj):
        #TODO - maybe raise if not empty?
        self.board[square.row][square.column] = obj
    def _getSquare(self, square):
        return self.board[square.row][square.column]
        
    def __init__(self, rows, columns):
        self.board = [[EmptySquare()] * columns for _ in xrange(rows)]
        self.rows, self.columns = rows, columns
    
    def Copy(self):
        global copy_time
        t0 = time.time()
        #res = copy.deepcopy(self)
        res = Board(0,0)
        res.rows = self.rows
        res.columns = self.columns
        for r in xrange(self.rows):
            res.board.append(list(self.board[r]))
        t1 = time.time()
        copy_time += t1-t0
        return res
        
    def GetAvailSquares(self):
        res = []
        for row in xrange(self.rows):
            for column in xrange(self.columns):
                if isinstance(self._getSquare(Square(row, column)), EmptySquare):
                    res.append(Square(row, column))
        return res
    
    def TryPlacePiece(self, piece, square):
        squares_to_check = self._getSquaresToCheck(piece, square)
        if squares_to_check == [] or any(map(lambda sq: isinstance(self._getSquare(sq), Piece), squares_to_check)):
            raise UnavailableSquareException()
        else:
            self._setSquare(square, piece)
            for sq in squares_to_check:
                self._setSquare(sq, AttackedSquare())
                
        
    def _getSquaresToCheck(self, piece, square):
        #TODO We can already abandon search if we find a piece - obvious place to optimize
        res = []
        movement = piece.Moves()
        for direction in movement.directions:
            sq = square + direction
            while self._inbounds(sq):
                if isinstance(self._getSquare(sq), Piece):
                    return []
                res.append(sq)
                if movement.restricted:
                    break
                else:
                    sq = sq + direction
        return res
    
    def __eq__(self, other):
        for row in xrange(self.rows):
            for col in xrange(self.columns):
                if isinstance(self._getSquare(Square(row, col)), Piece):
                    if type(self._getSquare(Square(row, col))) is not type(other._getSquare(Square(row, col))):
                        return False  
        return True
                
    
    def __str__(self):
        res = '\n'
        for r in self.board:
            res +=  "|".join(map(str,r))
            res += '\n'
        return res
    def __repr__(self):
        return self.__str__()

def CheckIfAlreadyASolution(results, board):
        for b in results:
            if b == board:
                return True
        return False

def CalcSolutionForPieces(curboard, pieces, results=[]):
    
    if len(pieces) == 0:
        #gc.collect()

        global check_uniqueness_time
        t0 = time.time()

        if True or not CheckIfAlreadyASolution(results, curboard):
            results.append(curboard.Copy())
            #print "added solution #%i\n" %len(results)
        t1 = time.time()
        check_uniqueness_time += t1-t0
    else:
        avsq = curboard.GetAvailSquares()
        for sq in avsq:
            board = curboard.Copy()
            if len(pieces) == 6:
                print "try first piece sq: %s" % sq
            try:
                #board = curboard.Copy()
                global try_place_piece_time
                t0 = time.time()
                board.TryPlacePiece(pieces[0], sq)
                
                t1 = time.time()
                try_place_piece_time += (t1-t0)
                #piece = pieces[0]
                #remainingPieces = pieces[1:]
                CalcSolutionForPieces(board, pieces[1:], results)
                #board = curboard.Copy()          
            except UnavailableSquareException: 
                continue
    

def main(rows, columns, pieces):
    result_boards = []
    curboard = Board(rows, columns)
    CalcSolutionForPieces(curboard, pieces, result_boards)
    return result_boards
        
        

if __name__ == '__main__':
    starttime = time.time()
    #res = main(3,3,[King(), King(), Rook()])
    #res = main(4,4,[Rook(), Rook(), Knight(), Knight(), Knight(), Knight()])
    #res = main(6,9,[Queen(), Rook(), Bishop(), Knight(), King(), King()])
    res = main(5,5,[King(), King(), Queen(), Bishop(), Knight(), Rook()])
    endtime = time.time()
    for b in res:
        print b  
    print "# unique solutions: %i" % len(res)
    print "Time to compute: %s" % str(endtime-starttime)
    print "copy_time %s" % str(copy_time)
    print "try_place_piece in loop %s" % str(try_place_piece_time)
    print "square_creation_time %s" % str(square_creation_time)
    print "check_uniqueness_time %s" % str(check_uniqueness_time)
    
    
    