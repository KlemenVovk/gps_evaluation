import pandas as pd
import os
from geographiclib.geodesic import Geodesic
import math
from pprint import pprint

GEOLOCATION="unil"
GT_POINTS_CSV = f'datasets/raw/{GEOLOCATION}/gt_points.csv'
MEASUREMENTS_CSV = f'datasets/raw/{GEOLOCATION}/measurements.csv'
OUTPUT_COLUMNS = ['measured_from','lat', 'lng','distance', 'angle_rad', 'angle_deg']

def lat_lng2dist_ang(center_point_lat_lng, target_point_lat_lng):
    # center_point_lat_lng = [lat, lng] this is one of the ground truth proposal points (not the evidence point)
    # target_point_lat_lng = [lat, lng] this is one of the measured points for the proposal, can also be the evidence point
    # computes distance (in meters) between two points and azimuth (angle from north) of the line using WGS84 ellipsoid, line spins around center_point_lat_lng
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
    return distance, angle_rad, angle_deg

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
    pprint(df.groupby(proposal_col).size())
    # remove duplicates
    df = df[df['delete'] == False]
    df = df.drop(columns=['delete'])
    df = df.reset_index(drop=True)
    # After removing duplicates
    print(f"Number of measurements per proposal (after consecutive deduplication):")
    pprint(df.groupby(proposal_col).size())
    return df

def transform(measurements_df, gt_points_df, proposal_col="measured_from"):
    # add dist, angle and angle_deg columns to measurements_df for each proposal
    transformed_df = measurements_df.copy()
    transformed_df["distance"] = None
    transformed_df["angle_rad"] = None
    transformed_df["angle_deg"] = None

    # iterate over measurements and compute for each
    for i, row in transformed_df.iterrows():
        # get the proposal lat, lng
        proposal_name = row[proposal_col]
        proposal_lat_lng = gt_points_df[gt_points_df["name"] == proposal_name][["lat", "lng"]].values[0]
        dist, angle, angle_deg = lat_lng2dist_ang(proposal_lat_lng, [row["lat"], row["lng"]])
        transformed_df.at[i, "distance"] = dist
        transformed_df.at[i, "angle_rad"] = angle
        transformed_df.at[i, "angle_deg"] = angle_deg
    return transformed_df


if __name__ == "__main__":
    measurements_df = pd.read_csv(MEASUREMENTS_CSV, parse_dates=["datetime"])
    gt_points_df = pd.read_csv(GT_POINTS_CSV)

    transformed_df = remove_consecutive_duplicates(measurements_df)
    proposal_names = gt_points_df["name"].tolist()
    proposal_names.remove("E")

    transformed_df = transform(transformed_df, gt_points_df)
    os.makedirs(f'datasets/processed/{GEOLOCATION}', exist_ok=True)
    transformed_df = transformed_df[OUTPUT_COLUMNS]
    transformed_df.to_csv(f'datasets/processed/{GEOLOCATION}/transformed.csv', index=False)

    print(transformed_df.head())