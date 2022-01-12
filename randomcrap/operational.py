{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 409,
   "id": "7e0c5939-3495-46e4-b486-bb9834c90975",
   "metadata": {},
   "outputs": [],
   "source": [
    "data_url = ('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 410,
   "id": "22a56d6f-3fd9-4d24-995a-fe026e2c4997",
   "metadata": {},
   "outputs": [],
   "source": [
    "from datetime import datetime, timedelta\n",
    "import io\n",
    "\n",
    "from metpy.units import units\n",
    "from metpy.plots import ImagePlot, MapPanel, PanelContainer\n",
    "from siphon.catalog import TDSCatalog\n",
    "import xarray as xr\n",
    "\n",
    "%matplotlib inline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 411,
   "id": "012bf6b8-f52b-4fa8-90db-5aeac404c575",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "['Best GFS Quarter Degree Forecast Time Series']\n"
     ]
    }
   ],
   "source": [
    "best_gfs = TDSCatalog(data_url)\n",
    "print(list(best_gfs.datasets))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 412,
   "id": "e4c9c118-ac4f-40f1-b3bd-00fa16b91bb5",
   "metadata": {},
   "outputs": [],
   "source": [
    "best_ds = best_gfs.datasets[0]\n",
    "ncss = best_ds.subset()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 413,
   "id": "318f0e28-1dd0-43d9-a328-77e6be0718d4",
   "metadata": {},
   "outputs": [],
   "source": [
    "query = ncss.query()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 418,
   "id": "ca16666a-c23c-443d-9dc5-1f8ae1eeca21",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "time=2021-11-30T08%3A46%3A14.731567&west=-130&east=-60&south=25&north=50&accept=netcdf4\n"
     ]
    }
   ],
   "source": [
    "query.lonlat_box(north=50, south=25, east=-60, west=-130).time(datetime.utcnow() + timedelta(hours=12))\n",
    "query.accept('netcdf4')\n",
    "#query.variables('Temperature_surface')\n",
    "print(query)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "14fb8091-6596-4f3a-8014-bfcabfa96ddb",
   "metadata": {},
   "outputs": [],
   "source": [
    "data = ncss.get_data_raw(query)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8616545c-e95e-4b78-92c4-4313910a7f67",
   "metadata": {},
   "outputs": [],
   "source": [
    "gfs = xr.open_dataset(io.BytesIO(data))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4d2bdf30-762b-46db-a402-841b8e6875d9",
   "metadata": {},
   "outputs": [],
   "source": [
    "gfs"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5b00a4c1-2137-4b98-8553-7a06fab423ec",
   "metadata": {},
   "outputs": [],
   "source": [
    "img = ImagePlot()\n",
    "img.data = gfs\n",
    "#gfs.Temperature_surface[0][0][0] = float(gfs.Temperature_surface[0][0][0])\n",
    "#gfs.Temperature_surface[0][1][1] = 250.0\n",
    "#print(float(gfs.Temperature_surface[0][1][1]))\n",
    "#print(float(gfs.Temperature_surface[0][0][0]))\n",
    "img.field = 'Temperature_surface'\n",
    "img.colormap = 'coolwarm'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c0c2433a-c1db-44e4-a09b-a722dde0e761",
   "metadata": {},
   "outputs": [],
   "source": [
    "panel = MapPanel()\n",
    "panel.area = 'co'\n",
    "panel.layers = ['states']\n",
    "panel.title = 'GFS temperature forecast'\n",
    "panel.plots = [img]\n",
    "\n",
    "pc = PanelContainer()\n",
    "pc.size = (10, 8)\n",
    "pc.panels = [panel]\n",
    "pc.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f6f20b6c-2e30-4d49-96c1-c9af144576a8",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
