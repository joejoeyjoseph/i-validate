# 20200612 JLCY
# 577 files

from netCDF4 import Dataset
import glob
import wrf
import xarray as xr

target_height = [ 40.,  50.,  60.,  80., 100., 120., 140., 160., 180., 200.] # agl

lat_start, lat_end = 410, 560
lon_start, lon_end = 390, 510

wrf_target_dir = '/scratch/cdraxl/MWdata/'
output_dir = '/scratch/jlee/wfip_wrf/'

wrf_file_list = glob.glob(wrf_target_dir+'*')
wrf_file_list.sort()

for file in wrf_file_list: 

    wrf_data = Dataset(file, 'r')

    ua = wrf.getvar(wrf_data, 'ua')
    va = wrf.getvar(wrf_data, 'va')
    ght = wrf.g_geoht.get_height(wrf_data, msl=False)

    ua_subset = ua[:, lat_start:lat_end, lon_start:lon_end]
    va_subset = va[:, lat_start:lat_end, lon_start:lon_end]
    ght_subset = ght[:, lat_start:lat_end, lon_start:lon_end]

    ua_ght = wrf.interplevel(ua_subset, ght_subset, target_height)
    va_ght = wrf.interplevel(va_subset, ght_subset, target_height)

    del ua_ght.attrs['projection']
    del va_ght.attrs['projection']

    ds = xr.Dataset({'u': ua_ght, 'v': va_ght})
    ds.to_netcdf(output_dir+file.split('/')[-1]+'.nc')