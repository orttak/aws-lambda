from shapely.geometry import Polygon,MultiPolygon
import numpy as np
from shapely.affinity import affine_transform 
import geopandas
import sys
import os
import numpy as np
import json
import pandas as pd


def jsonToGeojson(input_json,):
    #read input json
    json_file=input_json
    inv_map = {}
    for c in json_file['categories']: 
        inv_map[c['id']] = c['name']

    ### affine inverse transform 
    A_est_inv = [1.0, 0.0, -0.0, -1.0, -0.5, -0.5]

    ### empty list 
    polygons_list = []

    ### empty class name list 
    class_name_list= []

    ### temp matrix to hold info
    temp_matrix = np.zeros((4,2))
    temp_matrix.shape

    ## for each annotation in json file 
    for ann in json_file['annotations']:
        ### put invalid annotations in catagory 901 
        if np.sum(np.asarray(list(inv_map.keys()))==ann['category_id'])== 0:
            ann['category_id'] = 901

        ### get bounding box of ann 
        x,y,h,w = ann['bbox']

        ### find all corner point of bbox 
        x1 = x 
        x2 = x +  h
        y1 = y 
        y2 = y + w

        ann['M_BBOX'] =  [x1,y1,x2,y1,x2,y2,x1,y2]

        ## define them as array 
        bbox_array = np.asarray( ann['M_BBOX'] )
        bbox_array = np.squeeze(bbox_array)
        bbox_array.shape
        bbox_array[0::2,]
        bbox_array[1::2,]
        temp_matrix[:,0]= bbox_array[0::2,]
        temp_matrix[:,1]= bbox_array[1::2,]
        bbox_array = temp_matrix.copy()
        ### define them as polygon 
        polygon_bbox = Polygon(bbox_array)
        ## affine transrom to see them in QGIS 
        affine_object = affine_transform(polygon_bbox,A_est_inv )
        #print(AT)
        ## add polygon to the list 
        polygons_list.append(affine_object )
        ### add the class name 
        class_name_list.append(inv_map[ann['category_id']])

    ## creat dataframe 
    df = pd.DataFrame({'geometry':polygons_list,'TagName':class_name_list})
    ### creat geopandas dataframe 
    geo_dataframe = geopandas.GeoDataFrame(df)
    ### define projection  and project dataframe 
    geo_dataframe.crs = 'EPSG:4326'
    geo_dataframe= geo_dataframe.to_crs('EPSG:4326')

    #geojson_result=json.dumps(geo_dataframe.to_json())
    geojson_result=geo_dataframe.to_json()

    return geojson_result


def lambda_handler(event, context):
    payload = event['data']
    data_json=json.loads(json.dumps(payload))
    result=jsonToGeojson(input_json=data_json)
    
    result_json=json.loads(result)
    
    
    response = {
        "statusCode": 200,
        "headers": {
          "Content-Type": "application/json"
        },
        "body": result_json
    }
    
    return response

