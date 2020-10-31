'''
Created on Oct 30, 2020

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

PiecesAndMovement = {
    "N": ([[1,2],[1,-2],[-1,2],[-1,-2],[2,1],[2,-1],[-2,1],[-2,-1]], False),
    "Q": ([[1,0],[1,-1],[1,1],[0,-1],[0,1],[-1,0],[-1,-1],[-1,1]], True),
    "K": ([[1,0],[1,-1],[1,1],[0,-1],[0,1],[-1,0],[-1,-1],[-1,1]], False),
    "R": ([[1,0],[0,-1],[0,1],[-1,0]], True),
    "B": ([[1,-1],[1,1],[-1,-1],[-1,1]], True)   
    }


class Board(object):
    def _inbounds(self, square):
#        return 0 <= square.row < self.rows and 0 <= square.column < self.colums:
            
        if square[0] >= 0 and square[0] < self.rows and square[1] >= 0 and square[1] < self.columns:
            return True
        return False
    def _setSquare(self, square, obj):
        #TODO - maybe raise if not empty?
        self.board[square[0]][square[1]] = obj
    def _getSquare(self, square):
        return self.board[square[0]][square[1]]
        
    def __init__(self, rows, columns):
        self.board = [['.'] * columns for _ in xrange(rows)]
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
                if '.' == self._getSquare((row, column)):
                    res.append([row, column])
        return res
    
    def TryPlacePiece(self, piece, direction_input, square):
        directions, move_along = direction_input
        for direction in directions:
            sq = list(square)
            sq[0] += direction[0]
            sq[1] += direction[1]
            while self._inbounds(sq):
                if self._getSquare(sq) not in '.*':
                    raise UnavailableSquareException()
                self._setSquare(sq, '*')
                if not move_along:
                    break
                sq[0] += direction[0]
                sq[1] += direction[1]

        self._setSquare(square, piece)
    
#    def __eq__(self, other):
#        for row in xrange(self.rows):
#            for col in xrange(self.columns):
#                if isinstance(self._getSquare(Square(row, col)), Piece):
#                    if type(self._getSquare(Square(row, col))) is not type(other._getSquare(Square(row, col))):
#                        return False  
#        return True
                
    
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
                board.TryPlacePiece(pieces[0], PiecesAndMovement[pieces[0]], sq)
                
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
    #res = main(5,6,[King(), Knight(), Rook()])
    #res = main(3,3, "KKR")
    res = main(6,6, "QRBNKK")
    endtime = time.time()
    #for b in res:
    #    print b  
    print "# unique solutions: %i" % len(res)
    print "Time to compute: %s" % str(endtime-starttime)
    print "copy_time %s" % str(copy_time)
    print "try_place_piece in loop %s" % str(try_place_piece_time)
    print "square_creation_time %s" % str(square_creation_time)
    print "check_uniqueness_time %s" % str(check_uniqueness_time)
    
    
    