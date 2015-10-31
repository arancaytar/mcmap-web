import os
import re
import math
import subprocess

p = re.compile('^(-?[0-9]+)\,(-?[0-9]+)\.png$')
path = '.'

def rescale(src, target):
  a,b,c,d = 0,0,0,0
  coords = set()
  tcoords = set()
  for f in os.listdir(src):
    match = p.match(f)
    if match:
      x, z = int(match.group(1)), int(match.group(2))
      a, b, c, d = min(a, x), max(b, x), min(c, z), max(d, z)
      coords.add((x,z))
      tcoords.add((math.floor(x/2), math.floor(z/2)))
      
  for i,j in tcoords:
    pics = ['{src}/{i},{j}.png'.format(src=src,i=x,j=z) for x,z in ((i*2+(c&1), j*2+(c>>1)) for c in range(4))]
    t = '{target}/{i},{j}.png'.format(target=target, i=i, j=j)
    if os.path.isfile(t):
      newest_tile = max([os.path.getmtime(pic) if os.path.isfile(pic) else 0 for pic in pics])
      if newest_tile <= os.path.getmtime(t):
        print('Tile {i},{j}: -'.format(i=i,j=j))
        continue
    pics = [pic if os.path.isfile(pic) else 'null:' for pic in pics]
    print('Tile {i},{j}: Update'.format(i=i,j=j))
    subprocess.call(['montage', '-mode', 'concatenate', '-background', 'None', '-geometry', '256x256'] + pics + [t])

parent = '.'
src = parent

for i in range(7):
  next = parent + ('/z%d' % i)
  print("Scaling down by 2^%d" % i)
  rescale(src, next)
  src = next
