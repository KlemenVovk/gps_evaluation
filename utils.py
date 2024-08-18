from geographiclib.geodesic import Geodesic
import math
import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def lat_lng2dist_ang(center_point_lat_lng, target_point_lat_lng):
    # center_point_lat_lng = [lat, lng] this is one of the known proposal points (not the evidence point)
    # target_point_lat_lng = [lat, lng] this is one of the measured points for the proposal, can also be the evidence point
    # computes distance (in meters) between two points and azimuth (angle from north in radians) of the line using WGS84 ellipsoid, line spins around center_point_lat_lng
    # computes angle (in radians and degrees) between two points
    results = Geodesic.WGS84.Inverse(
        center_point_lat_lng[0],
        center_point_lat_lng[1],
        target_point_lat_lng[0],
        target_point_lat_lng[1],
    )
    distance = results["s12"]
    angle_deg = results["azi1"]
    angle_rad = math.radians(angle_deg)
    # from -pi to pi convert to 0 to 2pi
    if angle_rad < 0:
        angle_rad = 2 * math.pi + angle_rad
    return distance, angle_rad, angle_deg


def raster_evidence_geomap(
    gt_points_df: pd.DataFrame,
    measurements_df: pd.DataFrame,
    crs="epsg:4326", # CRS of the geographic data (by default assumes WGS84)
    source=ctx.providers.OpenStreetMap.Mapnik, # source of the basemap
    ax=None,
    gt_plot_label_col="plot_label",
    measurements_plot_label_col="plot_label",
    
):
    if ax is None:
        _, ax = plt.subplots()
    sns.scatterplot(
        data=measurements_df, x="lng", y="lat", hue=measurements_plot_label_col, ax=ax, marker="x"
    )
    sns.scatterplot(data=gt_points_df, x="lng", y="lat", hue=gt_plot_label_col, ax=ax, s=100)
    ctx.add_basemap(ax, crs=crs, source=source)
    ax.axis('off')
    #! save this as a raster image as the backround basemap is raster...
    return ax