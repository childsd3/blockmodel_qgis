import math

def prettyHeader(array):
	removeBlanks = filter(None,array)
	outputList = list()
	for item in removeBlanks:
		outputList.append(item.rstrip())
	return outputList

def prettyArray(array):
	removeBlanks = filter(None,array)
	outputList = list()
	for item in removeBlanks:
		stripped = item.rstrip()
		outputList.append(float(stripped))
	return outputList

def make2dList(rows, cols):
	a=[]
	for row in range(rows): 
		a += [[None]*cols]
	return a

def make3dList(rows, cols, lvls):
	a=[[[None for _ in range(lvls)] for _ in range(cols)] for _ in range(rows)]
	return a

def xyz2index (x,y,z,xllcorner,yllcorner,zllcorner,colsize,rowsize,lvlsize):
	icol = int(round((x-xllcorner)/colsize))
	irow = int(round((y-yllcorner)/rowsize))
	ilvl = int(round((z-zllcorner)/lvlsize))
	return icol,irow,ilvl
	
def index2xyz (icol,irow,xllcorner,yllcorner,colsize,rowsize,lvlsize):
	x = xllcorner + colsize*icol+0.5*colsize
	y = yllcorner + rowsize*irow+0.5*rowsize
	z = zllcorner + lvlsize*ilvl+0.5*lvlsize
	return x,y,z

def xy2index (x,y,xllcorner,yllcorner,cellsize):
	icol = int(round((x-xllcorner)/cellsize))
	irow = int(round((y-yllcorner)/cellsize))
	return icol,irow
	
def index2xy (icol,irow,xllcorner,yllcorner,cellsize):
	x = xllcorner + cellsize*icol+0.5*cellsize
	y = yllcorner + cellsize*irow+0.5*cellsize
	return x,y

def flip2dList(array):
	newList = make2dList(len(array[0]),len(array))
	for i in range(len(array)):
			for j in range(len(array[0])):
				newList[j][i] = array[i][j]
	return newList

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def percentStatus(num,total):
	value = (float(num)/float(total))*100
	return int(value)

def blockModelLimits(filename,statusBar):
	fileLength = file_len(filename)
	with open(filename, 'r') as f:
		counter = 0
		status = 0
		ncols,nrows,xllcorner,yllcorner,cellsize,NODATA_value = 0,0,0,0,0,0
		xArray = list()
		yArray = list()
		zArray = list()
		for line in f:
			counter += 1
			if counter == 1:
				continue
			incStatus = percentStatus(counter,fileLength)
			if incStatus > status:
				status = incStatus
				statusBar.setValue(status)
			lineArray = line.split(",")
			xArray.append(float(lineArray[0]))
			yArray.append(float(lineArray[1]))
			zArray.append(float(lineArray[2]))
		maxX = max(xArray)
		minX = min(xArray)
		maxY = max(yArray)
		minY = min(yArray)
		maxZ = max(zArray)
		minZ = min(zArray)
		nCols = len(list(set(xArray)))
		nRows = len(list(set(yArray)))
		nLvls = len(list(set(zArray)))
		colSize = math.fabs(maxX-minX)/(nCols-1)
		rowSize = math.fabs(maxY-minY)/(nRows-1)
		lvlSize = math.fabs(maxZ-minZ)/(nLvls-1)
		return minX,minY,minZ,nCols,nRows,nLvls,colSize,rowSize,lvlSize

def loadASC (filename):
	with open(filename, 'r') as f:
		counter = 0
		ncols,nrows,xllcorner,yllcorner,cellsize,NODATA_value = 0,0,0,0,0,0
		data = list()
		for line in f:
			lineArray = line.split(" ")
			#ncols
			if counter == 0:
				ncols = int(prettyHeader(lineArray)[1])
			#nrows
			if counter == 1:
				nrows = int(prettyHeader(lineArray)[1])
			#xllcorner
			if counter == 2:
				xllcorner = float(prettyHeader(lineArray)[1])
			#yllcorner
			if counter == 3:
				yllcorner = float(prettyHeader(lineArray)[1])
			#cellsize
			if counter == 4:
				cellsize = float(prettyHeader(lineArray)[1])
			#NODATA_value
			if counter == 5:
				NODATA_value = float(prettyHeader(lineArray)[1])
			if counter > 5:
				data.append(prettyArray(lineArray))
			counter += 1
		reversedData = list(reversed(data))
		ascModel = flip2dList(reversedData)
		ascBlank = make2dList(len(data[0]),len(data))
		return ascModel,ascBlank,ncols,nrows,xllcorner,yllcorner,cellsize,NODATA_value

def generateASC (ascModel,ncols,nrows,xllcorner,yllcorner,cellsize,NODATA_value):
	outputString = 'ncols        '+str(ncols)+'\n'
	outputString += 'nrows        '+str(nrows)+'\n'
	outputString += 'xllcorner    '+str(xllcorner)+'\n'
	outputString += 'yllcorner    '+str(yllcorner)+'\n'
	outputString += 'cellsize     '+str(cellsize)+'\n'
	outputString += 'NODATA_value  '+str(NODATA_value)+'\n'
	rowcolList = flip2dList(ascModel)
	invertedList = list(reversed(rowcolList))
	for i in range(len(invertedList)):
		line = ''
		for j in range(len(invertedList[i])):
			if invertedList[i][j] == None:
				line += ' '+str(NODATA_value)
			else:
				line += ' '+str(invertedList[i][j])
		outputString += line+'\n'
	return outputString
	
def dtmProperties(layer):
	numCol = layer.width()
	numRow = layer.height()
	extents = layer.extent().toString().strip('u').replace(':',',').replace(' ','')
	splitExtents = extents.split(',')
	formattedOutput = list()
	for item in splitExtents:
		formattedOutput.append(float(item))
	xllcorner = formattedOutput[0]
	yllcorner = formattedOutput[1]
	cellsize = layer.rasterUnitsPerPixelX()
	return numCol,numRow,xllcorner,yllcorner,cellsize

def guessEasting(values):
	count = 0
	for item in values:
		pretty = item.replace(" ", "").lower()
		print(pretty)
		if pretty == 'easting' or pretty == 'east' or pretty == 'x' or pretty == 'lon' or pretty == 'longitude':
			return count
		count += 1
	return 0

def guessNorthing(values):
	count = 0
	for item in values:
		pretty = item.replace(" ", "").lower()
		print(pretty)
		if pretty == 'northing' or pretty == 'north' or pretty == 'y' or pretty == 'lat' or pretty == 'latitude':
			return count
		count += 1
	return 1

def guessElevation(values):
	count = 0
	for item in values:
		pretty = item.replace(" ", "").lower()
		print(pretty)
		if pretty == 'elevation' or pretty == 'elev' or pretty == 'z':
			return count
		count += 1
	return 2
