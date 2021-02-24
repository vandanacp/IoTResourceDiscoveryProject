import math
import distance

def euclidean(p, q):
    return math.dist(p, q)

def levenshtein(p, q):
    return distance.levenshtein(p, q)


def get_distance(e, e_type, p, q, thr):
    if (e_type == "int"):
        return 1 if abs(e[p] - e[q]) > thr else 0
    elif (e_type == "str"):
        return  1 if levenshtein(e[p], e[q]) > thr else 0
    else:
        assert(0)

def update_diff(i, d, diff, e, e_type, thr):
    # update exact
    diff[i-1][i] = d
    diff[i][i-1] = d

    r = 0
    while r < i - 1:
        if d == 0:
            diff[r][i] = diff[r][i-1]
        else:
            diff[r][i] = get_distance(e, e_type, i, r, thr)
        r = r + 1
    c = 0
    while c < i - 1:
        if d == 0:
            diff[i][c] = diff[i-1][c]
        else:
             diff[i][c] = get_distance(e, e_type, i, c, thr)
        c = c + 1 

def score(e, e_type, thr):
    rows, cols = (len(e), len(e))
    diff = [[0 for i in range(cols)] for j in range(rows)]

    i = 0
    while i < (len(e) - 1):
        #if e[i] == e[i+1]:
            #print(" M %u %u" %(i, i+1))
        #else:
            #print("NM %u %u" %(i, i+1))
        #d = e[i] - e[i+1] if e[i] > e[i+1] else e[i+1] - e[i]
        d = get_distance(e, e_type, i, i+1, thr)
        update_diff(i+1, d, diff, e, e_type, thr)
        i = i + 1

    score = 0
    for i in range(rows):
        x = []
        for j in range(cols):
            x.append("%04d" %(diff[i][j]))
            if (diff[i][j]):
                score = score + 1
        print(x)
    print("score %u" %score)
    return score

