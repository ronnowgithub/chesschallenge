#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#ifdef _WIN32 
    #define API __declspec(dllexport)
#else
    #define API
#endif

char RowColDiagMoves[][2] = {{0,-1}, {-1,0}, {0,1}, {1,0}, {1,-1}, {-1,-1}, {-1,1}, {1,1}};
char RowColMoves[][2] = {{0,-1}, {-1,0}, {0,1}, {1,0}};
char DiagMoves[][2] = {{1,-1}, {-1,-1}, {-1,1}, {1,1}};
char KnightMoves[][2] = {{1,-2}, {1,2}, {-1,-2}, {-1,2}, {2,-1}, {2,1}, {-2,-1}, {-2,1}};

const char* PossiblePieces = "NBRQK";

typedef char(*Directions)[2];

#define BOARD_SIZE(b) (b)->rows * (b)->columns
#define IDX(board, row, column) row * (board)->columns + column
#define ROW(board, idx) (int)idx / ((board)->columns)
#define COLUMN(board, idx) idx - ROW((board), idx) * (board)->columns
#define INBOUNDS(b, r, c) r >= 0 && r < b->rows && c >= 0 && c < b->columns

struct Board {
    int rows;
    int columns;
    char* board;
};

void initBoard(struct Board* board, int rows, int columns);
void deleteBoard(struct Board* b);
int placePiece(struct Board* b, char piece);
int placePieces(struct Board* b, char* pieces);
void printBoard(struct Board *b);

int fac(int x) {
    if(x < 1)
        return 1;
    return x*fac(x-1);
}

int calcPermutationFactor(const char* pieces) {
    int factor = 1;
    for(int i=0; i < strlen(PossiblePieces); i++) {
        int count = 0;
        char piece = PossiblePieces[i];
        for(int i=0; i < strlen(pieces); i++) {
            if(pieces[i] == piece) {
                count++;
            }
        }   
        factor *= fac(count);
    }
    return factor;
}

API int calcSolutions(int rows, int cols, char* pieces) {
    struct Board b;
    int rval = 0;
    //printf("rows %d, xols %d, pieces %s\n", rows, cols, pieces);
    initBoard(&b, rows, cols);
        rval = placePieces(&b, pieces);
    deleteBoard(&b);
    rval = rval / calcPermutationFactor(pieces);
    return rval;
};

void initBoard(struct Board* board, int rows, int columns) {
    board->rows = rows;
    board->columns = columns;
    board->board = (char*) malloc(rows*columns);
    for(int i=0; i<rows*columns; ++i) {
        board->board[i] = 0;
    }
};

void deleteBoard(struct Board* b) {
    free(b->board);    
};

void getDirections(char piece, Directions *p, int* repeat, int* size) {
    *repeat = 0;
    switch(piece) {
        case 'K':
            *p = RowColDiagMoves;
            *size = sizeof(RowColDiagMoves) / sizeof(RowColDiagMoves[0]);
            break;
        case 'Q':
            *repeat = 1;
            *p = RowColDiagMoves;
            *size = sizeof(RowColDiagMoves) / sizeof(RowColDiagMoves[0]);
            break;
        case 'R':
            *repeat = 1;
            *p = RowColMoves;
            *size = sizeof(RowColMoves) / sizeof(RowColMoves[0]);
            break;
        case 'B':
            *repeat = 1;
            *p = DiagMoves;
            *size = sizeof(DiagMoves) / sizeof(DiagMoves[0]);
            break;
        case 'N':
            *p = KnightMoves;
            *size = sizeof(KnightMoves) / sizeof(KnightMoves[0]);
            break;
        default:
            // error todo maybe
            return;
    }
};

int tryPlacePiece(struct Board* b, char piece, int idx) {
    if(b->board[idx] > 0)
        return 0;
    int pRow = ROW(b, idx);
    int pColumn = COLUMN(b, idx);

    Directions directions;
    int repeat;
    int size;
    getDirections(piece, &directions, &repeat, &size);
    char* tmpMap = (char*)malloc(BOARD_SIZE(b));
    memcpy(tmpMap, b->board ,BOARD_SIZE(b));
    tmpMap[idx] = piece;
    int success = 1;
 
    for(int i = 0; i < size; ++i) {
        char dx = directions[i][0];
        char dy = directions[i][1];
        int row = pRow + dx;
        int col = pColumn + dy;
        while(INBOUNDS(b, row, col)) {
            if(tmpMap[IDX(b, row, col)] < 0x20) {
                tmpMap[IDX(b, row, col)] += 1;
            }
            else {
                success = 0;
                break;
            }
            if(0 == repeat)
                break;
            row = row + dx;
            col = col + dy;
            }
    }
    if(success) {
        free(b->board);
        b->board = tmpMap;
        //printBoard(b);
    }
    else {
        free(tmpMap);
    }
    return success;
};

void removePiece(struct Board* b, int idx) {
    int pRow = ROW(b, idx);
    int pColumn = COLUMN(b, idx);
    Directions directions;
    int repeat;
    int size;
    char piece = b->board[idx];
    getDirections(piece, &directions, &repeat, &size);

    for(int i = 0; i < size; ++i) {
        char dx = directions[i][0];
        char dy = directions[i][1];
        int row = pRow + dx;
        int col = pColumn + dy;
        while(INBOUNDS(b, row, col)) {
            if(b->board[IDX(b, row, col)] < 0x20) {
                b->board[IDX(b, row, col)] -= 1;
            }
            if(0 == repeat)
                break;
            row = row + dx;
            col = col + dy;

        }
    }
    b->board[idx] = 0;
}

int placePieces(struct Board* b, char* pieces) {
    int solutions = 0;
    if(0 == strlen(pieces)) {
        //printBoard(b);
        return 1;
    }
    char piece = pieces[0];
    for(int idx = 0; idx < BOARD_SIZE(b); ++idx) {
        if(0 == b->board[idx] && tryPlacePiece(b, piece, idx)) {
            solutions += placePieces(b, pieces + 1);
            removePiece(b, idx); 

        }
    }
    return solutions;
};

void printBoard(struct Board *b) {
    printf("+");
    for(int i = 0; i < b->columns - 1; ++i)
        printf("--");
    printf("-+\n");

    for(int r = 0; r < b->rows; r++) {
        printf("|");
        for(int i = 0; i < b->columns; ++i) {
            char c = ' ';
            char val = (b->board[IDX(b, r, i)]);
            if (val >= 0x0A)
                c = val;
            else if (val > 0)
                c = '0' + val;
             printf("%c|", c);
        }
        printf("\n");     
    }

    printf("+");
    for(int i = 0; i < b->columns - 1; ++i)
        printf("--");
    printf("-+\n");
};

int main(int argc, char** argv) {
    int rows; 
    int cols;
    char* pieces;
    if(4 != argc) {
        rows = 3;
        cols = 3;
        pieces = "RRR";
        //pieces = "NB";
    }
    else {
        rows = atoi(argv[1]);
        cols = atoi(argv[2]);
        pieces = argv[3];
    }
    printf("rows %d, xols %d, pieces %s\n", rows, cols, pieces);
    int solutions = calcSolutions(rows, cols, pieces);
    printf("Done %d\n", solutions);

    return 0;
}
