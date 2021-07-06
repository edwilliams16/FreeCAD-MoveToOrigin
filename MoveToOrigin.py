__Title__    = "MoveToOrigin"
__Author__   = "edwilliams16"
__Version__  = "00.01"
__Date__     = "2021.6.15"
debug = False
'''Usage:
This macro will adjust the placement of a shape to place a selected feature at the origin.
One vertex:  - to origin
One line segment - midpoint to origin
One circle - center to origin
One arc of circle - center to origin
One face - CG of face to origin
Three vertices - center of circle through vertices to origin
Shape - CG of shape to origin

If the shape is a BaseFeature inside a body, the base feature's placement in the body is adjusted.
'''

def circumcenter(A, B, C):
    '''Return the circumcenter of three 3D vertices'''
    a2 = (B - C).Length**2
    b2 = (C - A).Length**2
    c2 = (A - B).Length**2
    if a2 * b2 * c2 == 0.0:
        print('Three vertices must be distinct')
        return
    alpha = a2 * (b2 + c2 - a2)
    beta = b2 * (c2 + a2 - b2)
    gamma = c2 * (a2 + b2 - c2)
    return (alpha*A + beta * B + gamma * C)/(alpha + beta + gamma)

def centerofmass(subshapes):
    mass =0.0
    moment = App.Vector(0, 0, 0)
    for sh in subshapes:
        mass += sh.Volume
        moment += sh.Volume * sh.CenterOfMass
    return moment/mass    

selt = Gui.Selection.getSelectionEx()
if len(selt) != 1:
    print('Select one vertex, edge or object\nor three vertices for center of circle')
    shift = App.Vector(0, 0, 0)  # bail and do nothing  
else:
    sel = selt[0]
    if sel.HasSubObjects:
        vv = sel.SubObjects
        if len(vv) ==3 and vv[0].ShapeType == 'Vertex' and   vv[1].ShapeType == 'Vertex' and vv[2].ShapeType == 'Vertex':
            shift = circumcenter(vv[0].Point, vv[1].Point, vv[2].Point)
            if debug: print('Three Vertices')
        elif len(vv) == 1: 
            selected = sel.SubObjects[0]
            if selected.ShapeType == 'Vertex':
                shift = selected.Point
                if debug: print('One vertex')
            elif selected.ShapeType == 'Edge':
                if selected.Curve.TypeId == 'Part::GeomCircle':    #circles and arcs
                     shift = selected.Curve.Center
                     if debug: print('One arc')      
                elif selected.Curve.TypeId == 'Part::GeomLine':
                    shift = (selected.valueAt(selected.FirstParameter) + selected.valueAt(selected.LastParameter))/2 # mid-point
                    if debug: print('One line')
                else:
                    print(f'edge is {selected.Curve.TypeId} not handled')
                    shift = App.Vector(0, 0, 0)  # bail and do nothing
            elif selected.ShapeType == 'Face':
                shift = selected.CenterOfMass #center of face
                if debug: print('One face')
            else:
                print(f'ShapeType {selected.ShapeType} not handled')
                shift = App.Vector(0, 0, 0)  # bail and do nothing
        else:
            print('Wrong number of Selections')
            shift = App.Vector(0, 0, 0)  # bail and do nothing
    else:
        if debug: print(f'ObjectName is {sel.ObjectName}')
        #if sel.ObjectName[0:11] == 'BaseFeature':
        if hasattr(sel.Object, 'Shape'):
            if debug: print('One solid')
            shape = sel.Object.Shape
            if shape.ShapeType == 'Solid' or shape.ShapeType == 'Shell':
                shift = shape.CenterOfMass
            elif shape.ShapeType == 'Compound' or shape.ShapeType == 'CompSolid':
                shift = centerofmass(shape.SubShapes)
            #more cases?
            else:
                print(f'Object ShapeType {sel.Object.Shape.ShapeType} not handled')
                shift = App.Vector(0, 0, 0)  # bail and do nothing                
        else:
            print(f'{sel.ObjectName} is not a shape')
            shift = App.Vector(0, 0, 0)  # bail and do nothing
            
print(f'Shift = {shift}')
base = App.ActiveDocument.getObject(sel.ObjectName).Placement
App.ActiveDocument.openTransaction('Undo Move to Origin')
base.move(-shift)
App.ActiveDocument.commitTransaction()
App.ActiveDocument.recompute()