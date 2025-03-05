import ctypes
import sys

if __name__ == "__main__":
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

    if sys.platform.lower() == "linux":
        chessCalcLib = "./chesscalc.so"
    elif sys.platform.lower() == "win32":
        chessCalcLib = "./chesscalc.dll"
    else:
        raise ValueError("Not supported OS")
        
    chesscalc = ctypes.CDLL(chessCalcLib);
    chesscalc.calcSolutions.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
    print (chesscalc.calcSolutions(rows, cols, pieces.encode("utf-8")))