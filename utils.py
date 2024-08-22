from geographiclib.geodesic import Geodesic
import math
import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pprint import pprint

def remove_consecutive_duplicates(df, time_col='datetime', proposal_col='measured_from'):
    # currently ignores precise as the unil dataset does not have imprecise...
    # sort first by proposal and then by datetime of measurement
    # identify duplicate rows (consecutive) and mark them for deletion
    COLUMNS_TO_COMPARE_FOR_DUPLICATE_ROW = [proposal_col, 'lat', 'lng']
    df = df.sort_values(by=[proposal_col, time_col], ascending=True, ignore_index=True)
    df["delete"] = False
    for i in range(1, df.shape[0]):
        if df.loc[i, COLUMNS_TO_COMPARE_FOR_DUPLICATE_ROW].equals(df.loc[i-1, COLUMNS_TO_COMPARE_FOR_DUPLICATE_ROW]):
            df.loc[i, 'delete'] = True
    # Before removing duplicates
    pprint(f"Number of measurements per proposal (before consecutive deduplication):")
    display(df.groupby(proposal_col).size())
    # remove duplicates
    df = df[df['delete'] == False]
    df = df.drop(columns=['delete'])
    df = df.reset_index(drop=True)
    # After removing duplicates
    print(f"Number of measurements per proposal (after consecutive deduplication):")
    pprint(df.groupby(proposal_col).size())
    return df

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
    # angle from -180 to 180 convert to 0 to 360
    if angle_deg < 0:
        angle_deg = 360 + angle_deg
    angle_rad = math.radians(angle_deg)
    # from -pi to pi convert to 0 to 2pi
    # if angle_rad < 0:
        # angle_rad = 2 * math.pi + angle_rad
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

