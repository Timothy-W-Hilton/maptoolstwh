"""Python tools for plotting data on maps

currently provides:

class Livermore_prj
class NA_124x124_satellite_prj
class mapper
class Livermore_Mapper
class NA_124x124_mapper
class CoastalSEES_WRF_Mapper
"""

from pkg_resources import resource_stream

from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap, to_rgba
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_pdf import FigureCanvasPdf

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pandas import read_csv
import numpy as np


class YatirForest(object):
    """container class to hold characteristics of Yatir Forest
    """
    def __init__(self):
        self.lat = 31.345315
        self.lon = 35.052224
        self.UTM_zone = ''


class Fig(Figure):
    """Subclass of matplotlib.figure.Figure; provides one-line saving

    matplotlib.figure.Figure requires some boilerplate to save a
    figure outside of matplotlib.pyplot.  Using pyplot often doesn't
    play well with detaching and reattaching screen sessions because
    screen loses its connection to $DISPLAY.  This class allows
    one-line figure saving independent of platform and $DISPLAY.
    """
    def savefig(self, dpi=150, fname="figure.pdf"):
        """save the object's map to an image file
        """
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.backends.backend_pdf import FigureCanvasPdf
        if fname.endswith((".pdf", ".PDF")):
            canvas = FigureCanvasPdf(self)
        elif fname.endswith((".png", ".PNG")):
            canvas = FigureCanvasAgg(self)
        else:
            raise(IOError(('unrecognized figure type.'
                           '  pdf or png are supported')))
        # The size * the dpi gives the final image sys.getsizeof()
        #   a4"x4" image * 80 dpi ==> 320x320 pixel image
        canvas.print_figure(fname, dpi=dpi)


class Livermore_prj(ccrs.AlbersEqualArea):
    """projection centered over Livermore, California, USA.

    shows most of the San Francisco Bay Area.
    """
    def __init__(self):
        """constructor
        """
        # center the projection at Livermore, California, USA (37.681873
        # N, 118.0353 W)
        super(Livermore_prj, self).__init__(central_latitude=37.681873,
                                            central_longitude=-118.0353)


class CoastalSEES_WRF_prj(ccrs.AlbersEqualArea):
    """projection centered over USA west coast
    """
    def __init__(self):
        """constructor
        """
        # center the projection at Arcadia, California, USA (34.1297
        # N, -118.0353 W)- this gets an East-West line to be roughly
        # horizontal at the center of the map
        super(CoastalSEES_WRF_prj, self).__init__(central_latitude=34.1297,
                                                  central_longitude=-118.0353)


class NA_124x124_satellite_prj(ccrs.NearsidePerspective):
    """projection with perspective of satellite over N America

    Provides a subclass of :class:`~cartopy.crs.NearsidePerspective`
    that simulates the perspective ot a satellite centered over the
    124x124 N American domain of Hilton et al. (2017).  The only
    differences from the parent class are centering the map on N
    America and lowering the simulated satellite height above Earth so
    that N America fills most of the figure.

    REFERENCES

    Hilton, T. W., M. E. Whelan, A. Zumkehr, S. Kulkarni, J. A. Berry,
    I. T. Baker, S. A. Montzka, C. Sweeney, B. R. Miller, and
    J. Elliott Campbell (2017), Peak growing season gross uptake of
    carbon in North America is largest in the Midwest USA, Nature
    Clim. Change, 7(6), 450

    """
    def __init__(self,
                 central_longitude=-87.561401,
                 central_latitude=50.98999,
                 satellite_height=1.5e7,
                 **kwargs):
        """the default arguments center the perspective over N America
        """
        super(NA_124x124_satellite_prj, self).__init__(
            central_longitude=central_longitude,
            central_latitude=central_latitude,
            satellite_height=satellite_height,
            **kwargs)


class Yatir_WRF_prj(ccrs.AlbersEqualArea):
    """projection centered over Yatir Forest, Isreal
    """
    def __init__(self):
        """constructor
        """
        super(Yatir_WRF_prj, self).__init__(central_latitude=31.345315,
                                            central_longitude=35.052224)


class mapper(object):
    """provides a figure, axes to plot data on a cartopy map

    SEE ALSO:
       `cartopy <http://scitools.org.uk/cartopy/>`_.
    """
    def __init__(self,
                 prj=None,
                 ax=None,
                 res='50m'):
        """define projection and axes for the map.

        ARGS:
           prj (:class:`~cartopy.crs.Projection` instance): the
              projection to use for the map.  Default is
              :class: `~cartopy.crs.PlateCarree` centered at (0.0 E,
              0.0 N)

           ax (:class: `~cartopy.mpl.geoaxes.GeoAxes` instance): the
              axes on which to plot the map.  Optional; if unspecified a
              figure and axes are created.

           res (string): ("110m" | {"50m"} | "10m")
        """
        if ax is None:
            if prj is None:
                self.prj = ccrs.PlateCarree()
            else:
                self.prj = prj
            self.fig = Figure(figsize=(4, 4))
            self.ax = self.fig.add_subplot(111, projection=self.prj)
        else:
            # TODO: check for type cartopy.mpl.geoaxes.GeoAxes
            self.ax = ax
            self.fig = ax.get_figure()
        self.ax.coastlines(res)
        self.ax.set_global()
        self.ax.gridlines(ylocs=range(0, 90, 15),
                          xlocs=range(-180, -50, 15),
                          zorder=5)

    def pcolormesh(self, lon, lat, data, zorder=1, **kwargs):
        """plot meshgrid visualizing data over the object's map instance

        ARGS:
        lon (array): 2D array of longitudes
        lat (array): 2D array of latitude
        data (array): 2D array of values to plot
        zorder (int): order (top to bottom) to plot the pcolormesh
        **kwargs: passed through to matplotlib.axes.Axes.pcolormesh
        """
        self.mappable = self.ax.pcolormesh(lon, lat, data,
                                           transform=ccrs.PlateCarree(),
                                           zorder=zorder,
                                           **kwargs)

    def contourf(self, lon, lat, data, zorder=1, **kwargs):
        """plot meshgrid visualizing data over the object's map instance

        ARGS:
        lon (array): 2D array of longitudes
        lat (array): 2D array of latitude
        data (array): 2D array of values to plot
        zorder (int): order (top to bottom) to plot the pcolormesh
        **kwargs: passed through to matplotlib.axes.Axes.pcolormesh
        """
        self.contour_mappable = self.ax.contourf(lon, lat, data,
                                                 transform=ccrs.PlateCarree(),
                                                 zorder=zorder,
                                                 **kwargs)

    def scatter(self, lon, lat, **kwargs):
        """plot points over the object's map instance
        """
        self.ax.scatter(lon, lat,
                        transform=ccrs.PlateCarree(),
                        **kwargs)

    def quiver(self, lon, lat, U, V, zorder=1, **kwargs):
        """plot vectors over the object's map instance

        Note: use the regrid_shape keyword to get a visually appealing
        density of vectors.

        ARGS:
        lon (array): 2D array of longitudes
        lat (array): 2D array of latitude
        U (array): 2D array of vector U component magnitudes
        V (array): 2D array of vector V component magnitudes
        zorder (int): order (top to bottom) to plot the pcolormesh
        **kwargs: passed through to matplotlib.axes.Axes.pcolormesh
        """
        self.quiv = self.ax.quiver(lon, lat, U, V,
                                   transform=ccrs.PlateCarree(),
                                   zorder=zorder,
                                   **kwargs)

    def colorbar(self,
                 cm=None,
                 norm=None,
                 cmap=None,
                 label_str=None,
                 **kwargs):
        """add a colorbar to the map

        ARGS:
        cm: mappable, as for
           :function:`~matplotlib.figure.Figure.colorbar`.  Default is
           the result of self.pcolormesh()
        norm: :class:`~colors.Normalize` instance, optional
        cmap: :class:`~colors.Colormap` instance, optional
        label_str (str): optional label for the colorbar
        **kwargs: passed on to `~matplotlib.figure.Figure.colorbar`
        """
        if cm is None:
            cm = self.mappable
        self.cb = self.fig.colorbar(cm, norm=norm, cmap=cmap,
                                    ax=self.ax,
                                    shrink=0.5,
                                    **kwargs)
        if label_str is not None:
            self.cb.set_label(label_str)

    def set_main_title(self, t_str):
        """set the axes main title string

        ARGS:
        t_str (str): the string to place in the title
        """
        self.ax.set_title(t_str, fontdict={'fontsize': 'small'})

    def get_ax(self):
        """return the object's :class:`~matplotlib.axes.Axes` instance
        """
        return(self.ax)

    def get_fig(self):
        """return the object's :class:`~matplotlib.figure.Figure` instance
        """
        return(self.fig)

    def savefig(self, dpi=150, fname="figure.pdf"):
        """save the object's map to an image file
        """
        if fname.endswith((".pdf", ".PDF")):
            canvas = FigureCanvasPdf(self.fig)
        elif fname.endswith((".png", ".PNG")):
            canvas = FigureCanvasAgg(self.fig)
        # The size * the dpi gives the final image sys.getsizeof()
        #   a4"x4" image * 80 dpi ==> 320x320 pixel image
        canvas.print_figure(fname, dpi=dpi)

    def set_extent(self, **kwargs):
        """set the axes "extent"

        All keywords are passed through to :class:
           ~cartopy.mpl.geoaxes.GeoAxes.set_extent()
        """
        super(self.ax, self).set_extent(**kwargs)


class Livermore_Mapper(mapper):
    """provides a figure, axes to plot data on the Livermore, CA, USA domain
    """
    def __init__(self,
                 prj=Livermore_prj(),
                 ax=None,
                 domain=2):
        super(Livermore_Mapper, self).__init__(prj=prj, ax=ax, res="10m")
        self.ax.set_extent((-125.03729, -118.61932, 35.113796, 40.192265))


class CoastalSEES_WRF_Mapper(mapper):
    """provides a figure, axes to plot data on the Coastal SEES domain
    """
    def __init__(self,
                 prj=CoastalSEES_WRF_prj(),
                 ax=None,
                 domain=2,
                 res='50m'):
        super(CoastalSEES_WRF_Mapper, self).__init__(prj=prj, ax=ax, res=res)
        if domain == 2:
            # OSU domain
            # self.ax.set_extent((-135.75792, -116.1489, 33.368294, 50.319572))
            # whole California domain (padded to nearest 1/2 degree)
            self.ax.set_extent((-134.0, -112.5, 31.0, 50.0))
        if domain == 1:
            self.ax.set_extent((-149.5, -82.5, 17.0, 58.5))
        if domain == "bigbasin":
            # zoom in on the San Francisco -- Monterey area
            # SF_lat = 37.7749
            # SF_lon = -122.4194
            # MontereyCA_lat = 36.6002
            # MontereyCA_lon = -121.8947
            self.ax.set_extent((-123.0, -121.0, 36.2, 38.0))
        if domain == "SoCal":
            # lon/lat bounding box for Southern California
            bbox_SoCal = (-120.0, -116.0, 32.0, 35.0)
            self.ax.set_extent(bbox_SoCal)
        if domain == "redwoods":
            # lon/lat bounding box for Sequioa Sempervirens range
            (-124.5, -114, 31.5, 42.5)
            bbox_redwoods = ((-124.5, -121, 35.7, 42.5))
            self.ax.set_extent(bbox_redwoods)


class NA_124x124_mapper(mapper):
    """provides a figure, axes to plot data on the 124x124 STEM domain

    Uses :class:`~cartopy.ccrs.NearsidePerspective` projection: this
    simulates the view from a satellite above Earth's surface.

    ARGS:


    optional kwargs include:
    satelite_height

    NOTES:
    The default satellite height is 1.5e7.  This zooms in nicely on N
       America.
    The cartopy default satellite height is 3.5785831e7.  This shows
       most (all) of a hemisphere.
    """
    def __init__(self,
                 prj=NA_124x124_satellite_prj(),
                 ax=None):
        """define projection and axes for the map.

        ARGS:
           prj (:class:`~cartopy.crs.Projection` instance): the
              projection to use for the map.  Default is
              :class:`~tim_map_tools.NA_124x124_satellite_prj`
           ax (:class: `~cartopy.mpl.geoaxes.GeoAxes` instance): the
              axes on which to plot the map.  Optional; if unspecified a
              figure and axes are created.
        """
        super(NA_124x124_mapper, self).__init__(prj=prj, ax=ax)


class Yatir_WRF_Mapper(mapper):
    """provides a figure, axes to plot data on the Coastal SEES domain
    """
    def __init__(self,
                 prj=Yatir_WRF_prj(),
                 ax=None,
                 domain=2,
                 res='50m'):
        super(Yatir_WRF_Mapper, self).__init__(prj=prj, ax=ax, res=res)

        borders = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_0_countries',
            scale='50m',
            facecolor='none')
        self.ax.add_feature(borders, edgecolor='black')
        if domain == 3:
            yf = YatirForest()
            self.ax.set_extent((yf.lon - 0.5, yf.lon + 0.5,
                                yf.lat - 0.5, yf.lat + 0.5))
        elif domain == 2:
            self.ax.set_extent((32.0, 38.0, 29.0, 34.0))
        else:
            self.ax.set_extent((20.0, 50.0, 21.0, 41.0))


def get_IGBP_modMODIS_21Category_PFTs_table():
    """get colors, names for 21-category IGBP modified MODIS land categories

    read color table from IGBP_modMODIS_veg_PFTs_table.dat (part of
    package data)
    """
    color_table = read_csv(resource_stream(
        __name__,
        'IGBP_modMODIS_veg_PFTs_table.dat'))
    return(color_table)


def get_IGBP_modMODIS_21Category_PFTs_cmap():
    """get colormap for 21-category IGBP modified MODIS land categories

    read color table from IGBP_modMODIS_veg_PFTs_table.dat (part of
    package data)

    """
    color_table = get_IGBP_modMODIS_21Category_PFTs_table()
    colors_rgba = np.array(list(map(to_rgba, color_table['color_hex'].values)))
    land_categories_cmap = ListedColormap(colors_rgba)
    return(land_categories_cmap)
