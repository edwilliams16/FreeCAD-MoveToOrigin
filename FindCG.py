def globalCG(obj, removeLocalOffset=True):
    '''Find COM of object in global coordinates
      remove local offset per https://forum.freecadweb.org/viewtopic.php?t=27821'''
    gpl = obj.getGlobalPlacement()
    pl = obj.Placement
    rpl= gpl.multiply(pl.inverse())
    if removeLocalOffset:
        return rpl.multVec(obj.Shape.CenterOfMass)
    else:
        return gpl.multVec(obj.Shape.CenterOfMass)


def printGCM(obj):
    ''' Compute and print out global COM of an object hierarchy'''
    global volume, moment
    if hasattr(obj, 'Shape'):
        shape = obj.Shape
        if hasattr(shape, 'CenterOfMass'):
            print(f'{obj.Name}  {vectorRound(globalCG(obj, True), nDec)}')
            volume += shape.Volume
            moment += globalCG(obj, True).multiply(shape.Volume)
        else:
            for obj1 in obj.OutList:
                if hasattr(obj1, 'Shape'):
                    printGCM(obj1)

def vectorRound(v, n):
    '''Round the output of App.Vector v to n dec places'''
    return App.Vector(round(v.x, n), round(v.y, n), round(v.z, n))

volume = 0
moment = App.Vector(0., 0., 0.)
nDec = 3  #number of Decimal places in output

for sel in Gui.Selection.getSelectionEx():
        printGCM(sel.Object)

print(f'Total Volume = {round(volume,2)}  Total Moment = {vectorRound(moment, nDec)}  Global CG = {vectorRound(moment.multiply(1./volume), nDec)}')

