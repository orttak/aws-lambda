import sys
import os
import numpy as np
import geopandas as gpd
import json
#https://github.com/aws/amazon-sagemaker-examples/issues/1773
#Install opencv-python-headless instead of opencv-python. Server (headless) environments do not have GUI packages installed which is why you are seeing the error. opencv-python depends on Qt which in turn depends on X11 related libraries
#important note for cv2 in aws env
import cv2 
import geopandas as gpd
import numpy as np 
import rasterio
import fiona
import geopandas as gpd
from shapely.geometry import Polygon

import urllib.request

def getBBOXfromShapely(feature):
    ##### get bounding box (in coco format) from shapely polygon object (x1,y1,h,w)
    return [feature.bounds[0],feature.bounds[1],feature.bounds[2]-feature.bounds[0],feature.bounds[3]- feature.bounds[1]]

def get_exterior_poly(input_poly):
    ### get the exterior of polygon (ignore this function)
    if str(type(input_poly)) == "<class 'shapely.geometry.multipolygon.MultiPolygon'>":
        input_poly = input_poly[0]
    lst = list(input_poly.exterior.coords)
    list_ = [e for l in lst for e in l]
    return list_

def getBBOXfromShapely2(feature):
    ## ger the bounding box in other format (for showing in HTML)(x1,y1,x2,y2,x3,y3,x4,y4)
    return [feature.bounds[0],feature.bounds[1],feature.bounds[2],feature.bounds[1],feature.bounds[2], feature.bounds[3],feature.bounds[0], feature.bounds[3]]
def get_inv_transform():
    ## get the affine transform (fixed for now)
    return [1.0, 0.0, -0.0, -1.0, -0.5, -0.5]

def get_json_from_geojson(url,vec_geojson):
    ##inputs: 
    ##url:url to image, vec_geojson:  geojson
    
    ## read image
    input_jpeg=urllib.request.urlretrieve(url)
    im=cv2.imread(input_jpeg[0])
    
    #imagename
    image_name=url.split('/')[-1]
    
    ## define projection (EPSG:4326)
    #CRC = rasterio.crs.CRS.from_string('EPSG:4326')
    
    ##get inverse transform  
    inv_transfrom = get_inv_transform()
    
    ## read the geojson as geoseries 
    #poly_gseries = gpd.GeoDataFrame.from_file(vec_geojson).dropna( inplace=False).reset_index()
    poly_gseries = gpd.GeoDataFrame.from_file(vec_geojson)#.dropna( inplace=False).reset_index()
    poly_gseries = poly_gseries[poly_gseries['geometry'].notna()].reset_index()
    
    ### project the geoseries to matrix coordinates 
    test_matcoor_w = poly_gseries.affine_transform(inv_transfrom)

    ## read reference class names and ids file and convetr them to coco format
    pth_json = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Doktar_Feromon_Referans_v06.json")

    with open(pth_json,encoding="utf-8") as json_file:
        ref_json = json.load(json_file) 
    mycat ={}
    for ref in ref_json: 
        mycat[ref["TagName"]] = int(ref["ClassId"])    
    
    mycat2 = []
    ### dictionary for all images in COCO format 
    bugs_coco = {"info": {},"licenses": [],"categories": [mycat2],"images": [], "annotations": []  }
    #print(bugs_coco)
    for i,k in enumerate(mycat.keys()):
        if(mycat[k]>0):
            mycat2.append({ "id":int(mycat[k])  ,"name": str(k),"supercategory": "bugs" })
        else: 
            mycat2.append({ "id": int(mycat[k]) ,"name":  str(k),"supercategory": "other" })   
   #################
    ### get size of the image
    X,Y,C = im.shape  

    ##start counter for images 
    k = 1
    
    ### temporary dictionary to hold the info of each image  
    temp = {}
    temp = {"id" : k ,"width": Y, "height":X, "file_name":image_name}#poly_gseries["ImageID"][0]


    ### append image info to main dictionary
    bugs_coco["images"].append(temp)
    
    ### start counter for objects 
    h = 0
    
    ### for each object in the geoseries 
    for i,g in enumerate(poly_gseries["TagName"]):
        ### temp2 to hold info og object g 
        #temp2 = {"id": h, "image_id": int(k) , "category_id": mycat[poly_gseries["TagName"][i]] ,"bbox":getBBOXfromShapely(test_matcoor_w[i]),"iscrowd": 0,"segmentation":get_exterior_poly(test_matcoor_w[i]),"M_BBOX": getBBOXfromShapely2(test_matcoor_w[i])}
        #remove segmentation part
        temp2 = {"id": h, "iscrowd": 0, "image_id": int(k) , "category_id": mycat[poly_gseries["TagName"][i]] ,"bbox":getBBOXfromShapely(test_matcoor_w[i]),"M_BBOX": getBBOXfromShapely2(test_matcoor_w[i])}

        
        ##increment object counter 
        h = h + 1
        
        ### add object to final dictionary
        bugs_coco["annotations"].append(temp2)
    
    #print(bugs_coco["categories"])
    bugs_coco["categories"] = bugs_coco["categories"][0]
    #print(bugs_coco)
    return bugs_coco


def lambda_handler(event, context):
    payload = event['data']
    img_url = event['url']
    
    data_json=json.dumps(payload)
    result=get_json_from_geojson(url=img_url,vec_geojson=data_json)
    
    result_json=json.loads(json.dumps(result))
    
    
    response = {"statusCode": 200,
    "headers": {
        "Content-Type": "application/json"
        },
        "body": result_json
        }
    
    return response

