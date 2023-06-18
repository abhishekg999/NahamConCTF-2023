# **Just One More** (455 pts, 96 solves)

## **Description**
Just one more?


## **Solution**
We are provided with 2 files, `jom.py` and `output.txt`.

```py
import random

OUT = open('output.txt', 'w')
FLAG = open('flag.txt', 'r').read().strip()
N = 64

l = len(FLAG)
arr = [random.randint(1,pow(2, N)) for _ in range(l)]
OUT.write(f'{arr}\n')

s_arr = []
for i in range(len(FLAG) - 1):
    s_i = sum([arr[j]*ord(FLAG[j]) for j in range(l)])
    s_arr.append(s_i)
    arr = [arr[-1]] + arr[:-1]

OUT.write(f'{s_arr}\n')
```

This program first creates an array of length `l = len(FLAG)` of random integers between `1` and `2^64`. It then generates this new array called `s_arr`, which has `len(FLAG) - 1` elements, where each element is computed as,

```py
sum([arr[j]*ord(FLAG[j]) for j in range(l)])
arr = [arr[-1]] + arr[:-1]
```

The first line is a pretty standard matrix multiplication. The second line cycles the array `arr`, moving the last element to the front of the original list. We are then given the list `s_arr` and `arr` and need to figure out `FLAG`.

Formally then, we are trying to solve for the vector `x`.
```
Mx = b
M.shape = (37, 38)
b.shape = (37,)
x.shape = (38,)
```

Now this challenge would be extremely simple, if `s_arr` was the same length as `arr`, however (as the challenge name hints), we are one dimension short. There is the psudeo inverse, which is an approximation that can be taken, however when I tried it, i did not get anything meaningful.
```
[103.50277289 104.28815045  92.01539196  99.33305222 119.53760578
  95.69239214  98.24784392  97.47758191  56.82679394 102.46099092
  96.27276221  55.35480505  99.04643181  55.4487917  103.43582709
 103.76982282 105.15635642  99.14829275  52.04425515 102.02207454
  98.3893674   56.38072757 103.60699322  51.71142126  97.18678301
  51.66688815 103.6533361   47.86540404  55.53968092 100.285898
  46.54772727 101.06219622 100.59949572  98.27478386  98.89090558
  95.63621179  94.64791337 123.43676773]
Output vector as characters:
gh\cw_ba8f`7c7ggic4fb8g3a3g/7d.edbb_^{
```

However one thing about this CTF in specific, is the flag structure, and more specifically the **limited character set**. We know that the flag is of the form, `flag\{[0-9a-f]{32}\}.` Due to this, I decided to write a solver using `z3`.


```py
from z3 import *

arr = [12407953253235233563, 3098214620796127593, 18025934049184131586, ...]
out = [35605255015866358705679, 36416918378456831329741, 35315503903088182809184, ...]

solver = Solver()

x = [Int(f"x_{i}") for i in range(38)]

for i in range(38):
    if i <= 4 or i == 37:
        continue
    
    # ascii constraints we know for the flag body
    solver.add(Or(And(x[i] >= ord('a'), x[i] <= ord('f')), And(x[i] >= ord('0'), x[i] <= ord('9'))))

for i in range(37):
    solver.add(out[i] == Sum([arr[j] * x[j] for j in range(38)]))
    arr = [arr[-1]] + arr[:-1]

solver.add(x[0] == ord('f'))  
solver.add(x[1] == ord('l'))  
solver.add(x[2] == ord('a'))  
solver.add(x[3] == ord('g')) 
solver.add(x[4] == ord('{')) 
solver.add(x[37] == ord('}'))

print(solver)

if solver.check() == sat:
    model = solver.model()
    solution = [chr(model[x[i]].as_long()) for i in range(38)]
    print("Solution x:")
    print("".join(solution))
else:
    print("No solution found.")
```

Z3 finds the solution pretty quickly.
```
Solution x:
flag{aad9ba9b3fdfa4cc6f7e2e18d0dcbbab}
```


## **Flag**: *`flag{aad9ba9b3fdfa4cc6f7e2e18d0dcbbab}`*
