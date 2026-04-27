

try:
    # import empro stuff for this specific sipro simulation
    import empro
    import empro.toolkit
    import empro.toolkit.analysis

except ImportError:
    print(
        'Cannot import empro module - this usually means you are not using the Python from EMPro.  Use it by launching emproenv.bat/.sh')
    raise

def getInstPinsOnNet(project, netName):
    instPinsOnNet = []
    for inst in project.layout.instances:
        for pin in inst.pins():
            if pin.netName == netName:
                instPinsOnNet.append((inst, pin))
    return instPinsOnNet
                   
def pinToPinDistance(pinPos1, pinPos2, precision = 8):
    import math
    return round(math.sqrt((pinPos1.x-pinPos2.x)**2 + (pinPos1.y-pinPos2.y)**2 + (pinPos1.z-pinPos2.z)**2), precision)

    
def getClosestRefPinOnGround(instAndInstPinPair, sameInstanceOnly, project):
    groundNetNames = { net.name for net in project.layout.nets if net.type == empro.geometry.Net.GROUND }
    inst = instAndInstPinPair[0]
    instPin = instAndInstPinPair[1]
    distDictionary = {}
    if sameInstanceOnly:
        for pin in inst.pins():
            if pin.netName in groundNetNames:
                dist = pinToPinDistance(instPin.dotPosition, pin.dotPosition)
                distDictionary.setdefault(dist,[]).append((inst,pin))
    else:
        for inst in project.layout.instances:
            for pin in inst.pins():
                if pin.netName in groundNetNames:
                    dist = pinToPinDistance(instPin.dotPosition, pin.dotPosition)
                    distDictionary.setdefault(dist,[]).append((inst,pin))
        
    if len(distDictionary) > 0:
        distDictionary = sorted(distDictionary.items(), key=lambda x:x[0])
        return distDictionary[0]
    return []    

# project = empro.activeProject(), targetNetName is net you care about
def main(project, targetNetName):


    allPins = []
    instPins = getInstPinsOnNet(project, targetNetName)


    findInSameInstanceOnly = False
    for instAndInstPinPair in instPins:
        plusPins = []
        minusPins = []
        dist, instAndInstPinPairGnds = getClosestRefPinOnGround(instAndInstPinPair, findInSameInstanceOnly, project)
        # print("{}.{}".format(instAndInstPinPair[0].name, instAndInstPinPair[1].name))
        plusPins.append(instAndInstPinPair[0].name+'.'+instAndInstPinPair[1].name)

        if len(instAndInstPinPairGnds) > 0:
            for instAndInstPinPairGnd in instAndInstPinPairGnds:
                # print("closest pin: dist={} {}.{}".format(dist, instAndInstPinPairGnd[0].name, instAndInstPinPairGnd[1].name))
                minusPins.append(instAndInstPinPairGnd[0].name+'.'+instAndInstPinPairGnd[1].name)
            allPins.append(plusPins)
            allPins.append(minusPins)

    return allPins


