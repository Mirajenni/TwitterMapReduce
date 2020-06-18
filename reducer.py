import sys
import collections

counter = collections.Counter()

for line in sys.stdin:
    k, v = line.strip().split()

    counter[k] += int(v)

print (counter.most_common(50))