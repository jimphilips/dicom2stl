#! /usr/bin/env vtkpython

#
#  A collection of VTK functions for processing surfaces and volume.
#
#  Written by David T. Chen from the National Library of Medicine, dchen@mail.nih.gov.
#  It is covered by the Apache License, Version 2.0:
#  http://www.apache.org/licenses/LICENSE-2.0
#


import sys, time, gc
import traceback, vtk

#
#  timing knick knacks
#
def roundThousand(x):
    y = int(1000.0*x+0.5)
    return str(float(y)* .001)

def elapsedTime(start_time):
    dt = roundThousand(time.clock()-start_time)
    print "    ", dt, "seconds"

#
#  Isosurface extraction
#
def extractSurface(vol, isovalue=0.0):
    try:
        t = time.clock()
        iso = vtk.vtkContourFilter()
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            iso.SetInputData(vol)
        else:
            iso.SetInput(vol)
        iso.SetValue( 0, isovalue )
        iso.Update()
        print ("Surface extracted")
        mesh = iso.GetOutput()
        print "    ", mesh.GetNumberOfPolys(), "polygons"
        elapsedTime(t)
        iso = None
        return mesh
    except:
        print "Iso-surface extraction failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None


#
#  Mesh filtering
#
def cleanMesh(mesh, connectivityFilter=False):
    try:
        t = time.clock()
        connect = vtk.vtkPolyDataConnectivityFilter()
        clean = vtk.vtkCleanPolyData()

        if (connectivityFilter):
            if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
                connect.SetInputData( mesh )
            else:
                connect.SetInput( mesh )
            connect.SetExtractionModeToLargestRegion()
            clean.SetInputConnection( connect.GetOutputPort() )
        else:
            if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
                clean.SetInputData( mesh )
            else:
                clean.SetInput( mesh )

        clean.Update()
        print ("Surface cleaned")
        m2 = clean.GetOutput()
        print "    ", m2.GetNumberOfPolys(), "polygons"
        elapsedTime(t)
        clean = None
        connect = None
        return m2
    except:
        print "Surface cleaning failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

def smoothMesh(mesh, nIterations=10):
    try:
        t = time.clock()
        smooth = vtk.vtkWindowedSincPolyDataFilter()
        smooth.SetNumberOfIterations( nIterations )
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            smooth.SetInputData( mesh )
        else:
            smooth.SetInput( mesh )
        smooth.Update()
        print ("Surface smoothed")
        m2 = smooth.GetOutput()
        print "    ", m2.GetNumberOfPolys(), "polygons"
        elapsedTime(t)
        smooth = None
        return m2
    except:
        print "Surface smoothing failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

def rotateMesh(mesh, axis=1, angle=0):
    try:
        print "Rotating surface: axis=", axis, "angle=", angle
        matrix = vtk.vtkTransform();
        if axis==0:
            matrix.RotateX(angle)
        if axis==1:
            matrix.RotateY(angle)
        if axis==2:
            matrix.RotateZ(angle)
        tfilter = vtk.vtkTransformPolyDataFilter();
        tfilter.SetTransform(matrix);
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            tfilter.SetInputData( mesh )
        else:
            tfilter.SetInput( mesh )
        tfilter.Update()
        mesh2 = tfilter.GetOutput()
        return mesh2
    except:
        print "Surface rotating failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

#@profile
def reduceMesh(mymesh, reductionFactor):
    try:
        t = time.clock()
        deci = vtk.vtkQuadricDecimation()
        deci.SetTargetReduction( reductionFactor )
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            deci.SetInputData( mymesh )
        else:
            deci.SetInput( mymesh )
        deci.Update()
        print ("Surface reduced")
        m2 = deci.GetOutput()
        del deci
        deci = None
        print "    ", m2.GetNumberOfPolys(), "polygons"
        elapsedTime(t)
        return m2
    except:
        print "Surface reduction failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

#
#   Mesh I/O
#
def readMesh(name):
    if name.endswith(".vtk"):
        return readVTKMesh(name)
    if name.endswith(".ply"):
        return readPLY(name)
    if name.endswith(".stl"):
        return readSTL(name)
    print "Unknown file type: ", name
    return None

def readVTKMesh(name):
    try:
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName( name )
        reader.Update()
        print "Input mesh:", name
        mesh = reader.GetOutput()
        del reader
        reader = None
        return mesh
    except:
        print "VTK mesh reader failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

def readSTL(name):
    try:
        reader = vtk.vtkSTLReader()
        reader.SetFileName( name )
        reader.Update()
        print "Input mesh:", name
        mesh = reader.GetOutput()
        del reader
        reader = None
        return mesh
    except:
        print "STL Mesh reader failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

def readPLY(name):
    try:
        reader = vtk.vtkPLYReader()
        reader.SetFileName( name )
        reader.Update()
        print "Input mesh:", name
        mesh = reader.GetOutput()
        del reader
        reader = None
        return mesh
    except:
        print "PLY Mesh reader failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

def writeMesh(mesh, name):
    print "Writing", mesh.GetNumberOfPolys(), "polygons to", name
    if name.endswith(".vtk"):
        writeVTKMesh(mesh, name)
        return
    if name.endswith(".ply"):
        writePLY(mesh, name)
        return
    if name.endswith(".stl"):
        writeSTL(mesh, name)
        return
    print "Unknown file type: ", name

def writeVTKMesh(mesh, name):
    try:
        writer = vtk.vtkPolyDataWriter()
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            writer.SetInputData( mesh )
        else:
            writer.SetInput( mesh )
        writer.SetFileTypeToBinary()
        writer.SetFileName( name )
        writer.Write()
        print "Output mesh:", name
        writer = None
    except:
        print "VTK mesh writer failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

def writeSTL(mesh, name):
    try:
        writer = vtk.vtkSTLWriter()
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            print "writeSTL 1"
            writer.SetInputData( mesh )
        else:
            print "writeSTL 2"
            writer.SetInput( mesh )
        writer.SetFileTypeToBinary()
        writer.SetFileName( name )
        writer.Write()
        print "Output mesh:", name
        writer = None
    except:
        print "STL mesh writer failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

def writePLY(mesh, name):
    try:
        writer = vtk.vtkPLYWriter()
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            writer.SetInputData( mesh )
        else:
            writer.SetInput( mesh )
        writer.SetFileTypeToBinary()
        writer.SetFileName( name )
        writer.Write()
        print "Output mesh:", name
        writer = None
    except:
        print "PLY mesh writer failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

#
#  Volume I/O
#

def readVTKVolume(name):
    try:
        reader = vtk.vtkStructuredPointsReader()
        reader.SetFileName( name )
        reader.Update()
        print "Input volume:", name
        vol = reader.GetOutput()
        reader = None
        return vol
    except:
        print "VTK volume reader failed"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None

#@profile
def memquery1():
    print "Hiya 1"

#@profile
def memquery2():
    print "Hiya 2"

#@profile
def memquery3():
    print "Hiya 3"

#
#  Main (test code)
#
if __name__ == "__main__":
    print "vtkutils.py"

    print "VTK version:", vtk.vtkVersion.GetVTKVersion()
    print "VTK:", vtk

    mesh = readMesh("models/soft.stl")
#    mesh = cleanMesh(mesh, False)
#    mesh = smoothMesh(mesh)
    mesh2 = reduceMesh(mesh, .50)
    writeMesh(mesh2, "soft.ply")
