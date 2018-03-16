import marshal

if __name__ == "__main__":		
		
	inf = open('aldata.dat', 'rb')
	al = marshal.load(inf)
	inf.close()
	
	for pt in al:
		print(pt[0],pt[1],pt[2])
