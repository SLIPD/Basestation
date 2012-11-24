from payload import *
p = PayloadNodePosition()
p.initialise(55.943721, -3.175135,0,0)
d = p.getPaddedBytes()
print d.encode('hex_codec')
