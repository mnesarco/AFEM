from OCC.BRep import BRep_Builder, BRep_Tool
from OCC.BRepAdaptor import BRepAdaptor_Curve
from OCC.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, \
    BRepAlgoAPI_Fuse, BRepAlgoAPI_Section
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, \
    BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeVertex, BRepBuilderAPI_Sewing
from OCC.BRepCheck import BRepCheck_Analyzer
from OCC.BRepClass3d import brepclass3d
from OCC.BRepGProp import brepgprop_SurfaceProperties
from OCC.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace
from OCC.BRepTools import BRepTools_WireExplorer, breptools_OuterWire
from OCC.GCPnts import GCPnts_UniformAbscissa
from OCC.GProp import GProp_GProps
from OCC.GeomConvert import geomconvert
from OCC.ShapeAnalysis import ShapeAnalysis_Edge, ShapeAnalysis_ShapeTolerance
from OCC.ShapeFix import ShapeFix_Shape
from OCC.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCC.TopAbs import TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_EDGE, \
    TopAbs_FACE, TopAbs_REVERSED, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX, \
    TopAbs_WIRE
from OCC.TopExp import TopExp_Explorer
from OCC.TopoDS import TopoDS_CompSolid, TopoDS_Compound, TopoDS_Edge, \
    TopoDS_Face, TopoDS_Shape, TopoDS_Shell, TopoDS_Solid, TopoDS_Vertex, \
    TopoDS_Wire, topods_CompSolid, topods_Compound, topods_Edge, topods_Face, \
    topods_Shell, topods_Solid, topods_Vertex, topods_Wire

from ..config import Settings
from ..geometry import CheckGeom, CreateGeom
from ..geometry.methods.create import create_nurbs_surface_from_occ


class ShapeTools(object):
    """
    Shape tools.
    """

    @staticmethod
    def is_shape(shape):
        """
        Check if shape is a TopoDS_Shape.

        :param shape:

        :return:
        """
        return isinstance(shape, TopoDS_Shape)

    @staticmethod
    def to_shape(entity):
        """
        Convert the entity (shape or geometry) to a shape.

        :param entity:

        :return:
        """
        if not entity:
            return None

        # Shapes
        if isinstance(entity, TopoDS_Shape):
            if entity.ShapeType() == TopAbs_VERTEX:
                return topods_Vertex(entity)
            elif entity.ShapeType() == TopAbs_EDGE:
                return topods_Edge(entity)
            elif entity.ShapeType() == TopAbs_WIRE:
                return topods_Wire(entity)
            elif entity.ShapeType() == TopAbs_FACE:
                return topods_Face(entity)
            elif entity.ShapeType() == TopAbs_SHELL:
                return topods_Shell(entity)
            elif entity.ShapeType() == TopAbs_SOLID:
                return topods_Solid(entity)
            elif entity.ShapeType() == TopAbs_COMPSOLID:
                return topods_CompSolid(entity)
            elif entity.ShapeType() == TopAbs_COMPOUND:
                return topods_Compound(entity)
            else:
                return None

        # Geometry
        if CheckGeom.is_point_like(entity):
            return ShapeTools.to_vertex(entity)
        if CheckGeom.is_curve_like(entity):
            return ShapeTools.to_edge(entity)
        if CheckGeom.is_surface_like(entity):
            return ShapeTools.to_face(entity)

        return None

    @staticmethod
    def to_vertex(shape):
        """
        Convert a shape to a vertex.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Vertex):
            return shape

        if CheckGeom.is_point(shape):
            return BRepBuilderAPI_MakeVertex(shape).Vertex()

        if CheckGeom.is_point_like(shape):
            p = CreateGeom.point_by_xyz(*shape)
            return BRepBuilderAPI_MakeVertex(p).Vertex()

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_VERTEX:
            return topods_Vertex(shape)

        return None

    @staticmethod
    def to_edge(shape):
        """
        Convert a shape to an edge.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Edge):
            return shape

        if CheckGeom.is_curve_like(shape):
            return BRepBuilderAPI_MakeEdge(shape.GetHandle()).Edge()

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_EDGE:
            return topods_Edge(shape)

        return None

    @staticmethod
    def to_wire(shape):
        """
        Convert a shape to a wire.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Wire):
            return shape

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_WIRE:
            return topods_Wire(shape)

        return None

    @staticmethod
    def to_face(shape):
        """
        Convert a shape to a face.

        :param shape:
        :return:
        """
        if isinstance(shape, TopoDS_Face):
            return shape

        if CheckGeom.is_surface_like(shape):
            return BRepBuilderAPI_MakeFace(shape.GetHandle(), 0.).Face()

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_FACE:
            return topods_Face(shape)

        return None

    @staticmethod
    def to_shell(shape):
        """
        Convert a shape to a shell.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Shell):
            return shape

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_SHELL:
            return topods_Shell(shape)

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_FACE:
            shell = TopoDS_Shell()
            builder = BRep_Builder()
            builder.MakeShell(shell)
            builder.Add(shell, shape)
            return shell

        return None

    @staticmethod
    def to_solid(shape):
        """
        Convert a shape to a solid.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Solid):
            return shape

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_SOLID:
            return topods_Solid(shape)

        return None

    @staticmethod
    def to_compsolid(shape):
        """
        Convert a shape to a compsolid.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_CompSolid):
            return shape

        if (ShapeTools.is_shape(shape) and
                shape.ShapeType() == TopAbs_COMPSOLID):
            return topods_CompSolid(shape)

        return None

    @staticmethod
    def to_compound(shape):
        """
        Convert a shape to a compound.

        :param shape:

        :return:
        """
        if isinstance(shape, TopoDS_Compound):
            return shape

        if ShapeTools.is_shape(shape) and shape.ShapeType() == TopAbs_COMPOUND:
            return topods_Compound(shape)

        return None

    @staticmethod
    def get_vertices(shape):
        """
        Get vertices from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Vertex):
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_VERTEX)
        vertices = []
        while exp.More():
            vi = exp.Current()
            vertex = topods_Vertex(vi)
            vertices.append(vertex)
            exp.Next()
        return vertices

    @staticmethod
    def get_edges(shape, unique=True):
        """
        Get edges from a shape.

        :param shape:
        :param bool unique: Unique edges based on TShape and Location.

        :return:
        """
        if isinstance(shape, TopoDS_Edge):
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_EDGE)
        edges = []
        while exp.More():
            ei = exp.Current()
            edge = topods_Edge(ei)
            if unique:
                is_unique = True
                for e in edges:
                    if e.IsSame(edge):
                        is_unique = False
                        break
                if is_unique:
                    edges.append(edge)
            else:
                edges.append(edge)
            exp.Next()
        return edges

    @staticmethod
    def get_wires(shape):
        """
        Get wires from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Wire):
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_WIRE)
        wires = []
        while exp.More():
            wi = exp.Current()
            wire = topods_Wire(wi)
            wires.append(wire)
            exp.Next()
        return wires

    @staticmethod
    def get_faces(shape):
        """
        Get faces from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Face):
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_FACE)
        faces = []
        while exp.More():
            fi = exp.Current()
            face = topods_Face(fi)
            faces.append(face)
            exp.Next()
        return faces

    @staticmethod
    def get_solids(shape):
        """
        Get solids from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Solid):
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_SOLID)
        solids = []
        while exp.More():
            si = exp.Current()
            solid = topods_Solid(si)
            solids.append(solid)
            exp.Next()
        return solids

    @staticmethod
    def get_compounds(shape):
        """
        Get compounds from a shape.

        :return:
        """
        if isinstance(shape, TopoDS_Compound):
            return [shape]

        exp = TopExp_Explorer(shape, TopAbs_COMPOUND)
        compounds = []
        while exp.More():
            ci = exp.Current()
            compound = topods_Compound(ci)
            compounds.append(compound)
            exp.Next()
        return compounds

    @staticmethod
    def outer_wire(face):
        """
        Get outer wire of face.

        :param face:

        :return:
        """
        face = ShapeTools.to_face(face)
        if not face:
            return None
        return breptools_OuterWire(face)

    @staticmethod
    def outer_shell(solid):
        """
        Get the outer shell of the solid.

        :param solid:

        :return:
        """
        return brepclass3d.OuterShell(solid)

    @staticmethod
    def make_compound(shapes):
        """
        Create a compound from a list of shapes.

        :param shapes:

        :return:
        """
        compound = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(compound)
        for shape in shapes:
            if not isinstance(shape, TopoDS_Shape):
                continue
            builder.Add(compound, shape)
        return compound

    # @staticmethod
    # def curve_of_edge(edge):
    #     """
    #     Get the curve of the edge.
    #
    #     :param edge:
    #
    #     :return:
    #     """
    #     hcrv, u1, u2 = BRep_Tool.Curve(edge)
    #     try:
    #         occ_crv = geomconvert.CurveToBSplineCurve(hcrv).GetObject()
    #         return create_nurbs_curve_from_occ(occ_crv)
    #     except (RuntimeError, TypeError):
    #         return hcrv.GetObject()

    @staticmethod
    def surface_of_face(face):
        """
        Get the surface of the face.

        :param face:

        :return:
        """
        hsrf = BRep_Tool.Surface(face)
        try:
            occ_srf = geomconvert.SurfaceToBSplineSurface(hsrf).GetObject()
            return create_nurbs_surface_from_occ(occ_srf)
        except (RuntimeError, TypeError):
            return hsrf.GetObject()

    @staticmethod
    def sew_faces(faces, tol=None):
        """
        Sew faces to make shell.

        :param faces:
        :param tol:

        :return:
        """
        if tol is None:
            tol = Settings.gtol

        shell = TopoDS_Shell()
        builder = BRep_Builder()
        builder.MakeShell(shell)
        for f in faces:
            builder.Add(shell, f)

        if len(faces) == 1:
            return shell

        sew = BRepBuilderAPI_Sewing(tol)
        sew.Load(shell)
        sew.Perform()
        sewn_shape = sew.SewedShape()

        return sewn_shape

    @staticmethod
    def unify_shape(shape, edges=True, faces=True, concat_bsplines=False):
        """
        Attempt to unify a shape.

        :param shape:
        :param edges:
        :param faces:
        :param concat_bsplines:

        :return:
        """
        if not ShapeTools.is_shape(shape):
            return None

        unify = ShapeUpgrade_UnifySameDomain(shape, edges, faces,
                                             concat_bsplines)
        unify.Build()
        return ShapeTools.to_shape(unify.Shape())

    @staticmethod
    def bfuse(shape1, shape2, rtype=None):
        """
        Perform BOP Fuse operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Fuse(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        shape = bop.Shape()

        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def bcommon(shape1, shape2, rtype=None):
        """
        Perform BOP Common operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Common(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        shape = bop.Shape()

        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def bsection(shape1, shape2, rtype=None):
        """
        Perform BOP Section operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Section(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        shape = bop.Shape()

        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def bcut(shape1, shape2, rtype=None):
        """
        Perform BOP Cut operation between two shapes.

        :param shape1:
        :param shape2:
        :param str rtype: Type of shape to return from the resulting shape.

        :return:
        """
        shape1 = ShapeTools.to_shape(shape1)
        shape2 = ShapeTools.to_shape(shape2)

        bop = BRepAlgoAPI_Cut(shape1, shape2)
        if bop.ErrorStatus() != 0:
            return []
        shape = bop.Shape()

        if not rtype:
            return shape

        rtype = rtype.lower()
        shape = ShapeTools.to_shape(shape)
        if rtype in ['v', 'vertex']:
            return ShapeTools.get_vertices(shape)
        if rtype in ['e', 'edge']:
            return ShapeTools.get_edges(shape)
        if rtype in ['f', 'face']:
            return ShapeTools.get_faces(shape)
        if rtype in ['s', 'solid']:
            return ShapeTools.get_solids(shape)

        return []

    @staticmethod
    def create_halfspace(shape, pref):
        """
        Create a half-space.

        :param shape:
        :param pref:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        pref = CheckGeom.to_point(pref)
        if not isinstance(shape, (TopoDS_Face, TopoDS_Shell)):
            return None
        if not CheckGeom.is_point(pref):
            return None

        return BRepPrimAPI_MakeHalfSpace(shape, pref).Solid()

    @staticmethod
    def wire_explorer(wire, face=None):
        """
        Create a wire explorer.

        :param wire:
        :param face:

        :return:
        """
        wire = ShapeTools.to_wire(wire)
        face = ShapeTools.to_face(face)
        if not wire:
            return None

        if not face:
            return BRepTools_WireExplorer(wire)
        else:
            return BRepTools_WireExplorer(wire, face)

    @staticmethod
    def is_seam(edge, face):
        """
        Check to see if the edge is a seam edge on the face.

        :param edge:
        :param face:

        :return:
        """
        return ShapeAnalysis_Edge.IsSeam(edge, face)

    @staticmethod
    def first_vertex(edge):
        """
        Return the first vertex of the edge considering orientation.

        :param edge:

        :return:
        """
        return ShapeAnalysis_Edge().FirstVertex(edge)

    @staticmethod
    def last_vertex(edge):
        """
        Return the last vertex of the edge considering orientation.

        :param edge:

        :return:
        """
        return ShapeAnalysis_Edge().LastVertex(edge)

    @staticmethod
    def vertices(edge):
        """
        Return the first and last vertex of the edge.

        :param edge:

        :return:
        """
        return ShapeTools.first_vertex(edge), ShapeTools.last_vertex(edge)

    @staticmethod
    def same_parameter(edge):
        """
        Returns the SameParameter flag for the edge.

        :param edge:

        :return:
        """
        return BRep_Tool.SameParameter(edge)

    @staticmethod
    def same_range(edge):
        """
        Returns the SameRange flag for the edge.

        :param edge:

        :return:
        """
        return BRep_Tool.SameRange(edge)

    @staticmethod
    def parameter(vertex, edge, face=None):
        """
        Return the parameter of the vertex on the edge.

        :param vertex:
        :param edge:
        :param face:

        :return:
        """
        vertex = ShapeTools.to_vertex(vertex)
        edge = ShapeTools.to_edge(edge)
        face = ShapeTools.to_face(face)
        if not vertex or not edge:
            return None
        if not face:
            return BRep_Tool.Parameter(vertex, edge)
        else:
            return BRep_Tool.Parameter(vertex, edge, face)

    @staticmethod
    def parameters(edge, face=None):
        """
        Return the first and last parameters on the edge.

        :param edge:
        :param face:

        :return:
        """
        v1, v2 = ShapeTools.vertices(edge)
        u1 = ShapeTools.parameter(v1, edge, face)
        u2 = ShapeTools.parameter(v2, edge, face)
        return u1, u2

    @staticmethod
    def is_valid(shape):
        """
        Check the shape for errors.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return False
        check_shp = BRepCheck_Analyzer(shape, True)
        return check_shp.IsValid()

    @staticmethod
    def fix_shape(shape, max_tol=None):
        """
        Attempt to fix the shape.

        :param shape:
        :param max_tol:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None
        fix = ShapeFix_Shape(shape)
        if max_tol is not None:
            fix.SetMaxTolerance(max_tol)
        fix.Perform()
        new_shape = fix.Shape()
        return ShapeTools.to_shape(new_shape)

    @staticmethod
    def get_tolerance(shape, mode=0):
        """
        Compute the global tolerance of the shape.

        :param shape:
        :param mode: Average (0), maximal (1), minimal (2)

        :return:
        """
        tol = ShapeAnalysis_ShapeTolerance()
        tol.AddTolerance(shape)
        return tol.GlobalTolerance(mode)

    @staticmethod
    def points_along_edge(edge, dx):
        """
        Create points along an edge.

        :param edge:
        :param dx:

        :return:
        """
        edge = ShapeTools.to_edge(edge)
        if not edge:
            return []

        adp_crv = BRepAdaptor_Curve(edge)
        pac = GCPnts_UniformAbscissa(adp_crv, dx, Settings.gtol)
        if not pac.IsDone():
            return []

        pnts = []
        for i in range(1, pac.NbPoints() + 1):
            u = pac.Parameter(i)
            gp_pnt = adp_crv.Value(u)
            pnts.append(CreateGeom.point_by_xyz(gp_pnt.X(), gp_pnt.Y(),
                                                gp_pnt.Z()))

        if edge.Orientation() == TopAbs_REVERSED:
            pnts.reverse()

        return pnts

    @staticmethod
    def center_of_mass(shape):
        """
        Calculate center of mass of shape.

        :param shape:

        :return:
        """
        shape = ShapeTools.to_shape(shape)
        if not shape:
            return None

        props = GProp_GProps()
        brepgprop_SurfaceProperties(shape, props, Settings.gtol)
        cg = props.CentreOfMass()
        return CreateGeom.point_by_xyz(cg.Y(), cg.Y(), cg.Z())
