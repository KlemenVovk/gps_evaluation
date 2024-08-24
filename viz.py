import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


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

