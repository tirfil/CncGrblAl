import sys
import os
import re
import marshal

re_x = re.compile("X([0-9\.-]+)")
re_y = re.compile("Y([0-9\.-]+)")
re_z = re.compile("Z([0-9\.-]+)")
re_zz = re.compile("(Z[0-9\.-]+)")
re_comment = re.compile("(\([^\)]+\))")

class track:
	def __init__(self):
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
	def get(self):
		return (self.x,self.y,self.z)
	def process(self,line):
		mx = re_x.search(line)
		my = re_y.search(line)
		mz = re_z.search(line)
		change = False
		if mx:
			self.x = float(mx.group(1))
			change = True
		if my:
			self.y = float(my.group(1))
			change = True
		if mz:
			self.z = float(mz.group(1))
			change = True
		print "(%f,%f,%f)" % (self.x,self.y,self.z)	
		return change
		
def zcorr(pos,al):
	dist2 = float("inf")
	zc = 0
	for pt in al:
		dx = pos[0]-pt[0]
		dy = pos[1]-pt[1]
		d2 = dx*dx + dy*dy
		if d2 < dist2:
			dist2 = d2
			zc = pt[2]
	return zc
		
		
if __name__ == "__main__":		
		
	filename = sys.argv[1]

	if not(os.path.isfile(filename)):
		print("File %s doesn't exist -> exit" % filename)
		exit()
		
	inf = open('aldata.dat', 'rb')
	al = marshal.load(inf)
	inf.close()
	
	ouf = open('out.ngc', 'w')
		
	t = track()
		
	with open(filename,'r') as f: 
		for line in f:
			line = line.strip()
			print line
			if t.process(line):
				pt = t.get()
				zc = zcorr(pt,al)
				mzz = re_zz.search(line)
				mcomment = re_comment.search(line)
				if mcomment:
					line = line.replace(mcomment.group(1),"")
				if mzz:
					#print "\t\t\t" + line.replace(mzz.group(1),"Z%s"%str(pt[2]+zc))
					ouf.write(line.replace(mzz.group(1),"Z%s"%str(pt[2]+zc)+'\n'))
				else:
					#print "\t\t\t" + line + "Z%s"%str(pt[2]+zc)
					ouf.write(line + " Z%s"%str(pt[2]+zc)+'\n')
				
				pt=(pt[0],pt[1],pt[2]+zc)
				print "corr>",pt
			else:
				#print "\t\t\t" + line
				ouf.write(line + '\n')
	ouf.close()
				
		
