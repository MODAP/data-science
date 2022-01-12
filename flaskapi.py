from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime, timedelta
import io

import xarray as xr
import matplotlib.pyplot as plt
import requests
import time
import subprocess

app = Flask(__name__)
api = Api(app)

hrrr_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_hrrr_2d.pl?file=hrrr.t00z.wrfsfcf00.grib2&lev_surface=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fhrrr.20220112%2Fconus'
r = requests.get(hrrr_url, allow_redirects=True)
open('hrrr.grib2', 'wb').write(r.content)

gfs_ds = xr.load_dataset("hrrr.grib2", engine="cfgrib")

class GeThing(Resource):
    def get(self, reqname):
        datestr = time.strftime('%Y%m%d')
        hrrr_value_list = []

        coord_str = '-lon '+ reqname.split("=")[0] + ' ' + reqname.split("=")[1]

        hrrr_tmp = "/usr/bin/wgrib2 %s -match '%s' %s" % ('hrrr.grib2', 'TMP', coord_str)
        hrrr_value = (str(subprocess.check_output(hrrr_tmp, shell=True))[:-3])
        hrrr_value = hrrr_value.split(':')
        for z in range (len(hrr_value)):
            current_value = hrrr_value[z]
            if 'val' in current_value:
                current_value = float((current_value.split(',')[2]).split('=')[1])
                hrrr_value_list.append(current_value)

        return {"data": hrrr_value_list[0]}

api.add_resource(GeThing, '/<string:reqname>')

if __name__ == '__main__':
    app.run(debug=False)

