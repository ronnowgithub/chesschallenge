This is for demonstration only.

This is some code to solve a problem I was asked for before a job interview.
Problem is to place a number of chess pieces on a MxN chessboard so no one can capture another. Pawns not included. Colors can be disregarded. Find the number of unique solutions given M, N and some pieces.

The original excercise: make a python program that solves for 6x9 QRBNKK 

Run chesscalc.py:
python chesscalc.py -- will run with the 6x9 QRBNKK
Takes a while depending on your HW (like 9 minutes on a 10+ years old laptop)

python chesscalc.py M N pieces will run with the specified e.g 3 3 RRR

The algorithm/implementation can be seriously optimized, but that was not the excercise.
However, the (almost) extreme way is to do it in c.

--- 

You can run the faster.py
Yes it's still (ish) a python program :)
It uses the implemention in chesscalc.c - you need to compile it something like this:

On Linux:
cc -shared -fPIC -o chesscalc.so chesscalc.c

On Win (using MingW):
gcc -shared -o chesscalc.dll chesscalc.c

Same input as the chesscalc.py
Takes a SHORT while depending on your HW (like 10 seconds on a 10+ years old laptop)

Feel free to be inspired... or comment
