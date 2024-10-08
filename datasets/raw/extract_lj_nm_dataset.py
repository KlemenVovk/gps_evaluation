# This script was used to extract the GPS data from EXIF metadata in the mimages we collected for LJ and NM datasets.
# We keep it here only as reference, as we will not be uploading all the images to the VCS.

# from PIL import Image, ExifTags

import cv2 as cv
import os
import matplotlib.pyplot as plt
import exif
import pandas as pd

def load_images_from_folder(folder):
    df = pd.DataFrame(columns=["datetime","point","precise","lat","lng","ghpe"])
    for filename in os.listdir(folder):
        print(filename)
        
        
        for point_ in ["P1","P2","P3","SPOT"]:
            if point_ in filename:
                point = point_
        
        if "bad" in filename:
            precise = "off"
        else:
            precise = "on"
                
            
        path = os.path.join(folder,filename)
        im_org = exif.Image(path)
        print(dir(im_org))
        lat_d, lat_m, lat_s = im_org.get('gps_latitude')
        lat = lat_d+lat_m/60+lat_s/60/60
        lon_d, lon_m, lon_s = im_org.get('gps_longitude')
        lon = lon_d+lon_m/60+lon_s/60/60
        ghpe = im_org.get('gps_horizontal_positioning_error') # v metrih
        print(lat,lon)
        datetime = im_org.get("datetime")
        df.loc[len(df.index)] = [datetime,point, precise, lat, lon, ghpe] 
            
    return df

df = load_images_from_folder("/home/lema/Documents/forenzika/slike df2/slike df")
df.to_csv("points.csv")


# img = Image.open("/home/lema/Documents/forenzika/lovecnabiralec.jpg")
# exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
# print(exif['GPSInfo'])


