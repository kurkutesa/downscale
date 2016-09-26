# -*- coding: utf8 -*-
# # #
# Downscale PCMDI AR5 data to a pre-processed climatology
#  extent, resolution, reference system
#
#  ::NOTE:: this version of DeltaDownscale is built for tmin/tmax
#	data where our old method causes for the mins and max and means to 
# 	cross each other in non-normal ways.
#
# Author: Michael Lindgren (malindgren@alaska.edu)
# # #

from downscale import DeltaDownscale, utils
import os
import numpy as np
import xarray as xr

def delta_mm( fn, mean_fn, variable, mean_variable='tas' ):
	'''
	simple way to compute extreme - mean deltas as 
	native model resolution and write to NetCDF4 on disk
	'''
	ds = xr.open_dataset( fn )[ variable ]
	ds_mean = xr.open_dataset( mean_fn )[ mean_variable ]
	delta = ds - ds_mean
	return delta.to_dataset( name=variable )

class DeltaDownscaleMinMax( DeltaDownscale ):
	def __init__( self, mean_ds=None, mean_variable=None, *args, **kwargs ): 
		'''
			note here that all data falls into the 'historical' category, because we no longer need to 
			have the 1961-1990 climatology period for the futures as this version of DeltaDownscale computes
			deltas by removing the mean in time instead of removing the climatology.
		'''
		# setup new args
		self.mean_ds = mean_ds
		self.mean_variable = mean_variable

		super( DeltaDownscaleMinMax, self ).__init__( *args, **kwargs )
		
		# if there is no mean dataset to work with --> party's over
		if mean_ds == None:
			raise Exception( 'you must include the mean variable in the raw resolution \
								as arg `mean_ds`=downscale.Dataset object or use `DeltaDownscale`' )
	def _calc_climatolgy( self ):
		''' MASK THIS FOR MINMAX slice / aggregate to climatology using mean'''
		pass
	def _calc_anomalies( self ):
		''' calculate deltas but call them anomalies to fit the `downscale` pkg methods '''			
		self.anomalies = (self.historical.ds[ self.historical.variable ] - self.mean_ds.ds[ self.mean_variable ] ) #.to_dataset( name=variable )
	@staticmethod
	def interp_ds( anom, base, src_crs, src_nodata, dst_nodata, src_transform, resample_type='bilinear',*args, **kwargs ):
		'''	
		anom = [numpy.ndarray] 2-d array representing a single monthly timestep of the data to be downscaled. 
								Must also be representative of anomalies.
		base = [str] filename of the corresponding baseline monthly file to use as template and downscale 
								baseline for combining with anomalies.
		src_transform = [affine.affine] 6 element affine transform of the input anomalies. [should be greenwich-centered]
		resample_type = [str] one of ['bilinear', 'count', 'nearest', 'mode', 'cubic', 'index', 'average', 'lanczos', 'cubic_spline']
		'''	
		import rasterio
		from rasterio.warp import reproject, RESAMPLING
		from affine import Affine

		resampling = {'average':RESAMPLING.average,
					'cubic':RESAMPLING.cubic,
					'lanczos':RESAMPLING.lanczos,
					'bilinear':RESAMPLING.bilinear,
					'cubic_spline':RESAMPLING.cubic_spline,
					'mode':RESAMPLING.mode,
					'count':RESAMPLING.count,
					'index':RESAMPLING.index,
					'nearest':RESAMPLING.nearest }
		
		# lets try to flip the data and affine and do this right.
		a,b,c,d,e,f,g,h,i = src_transform
		src_transform = Affine( a, b, c, d, -(e), np.abs(f) ) # DANGEROUS
		anom = np.flipud( anom )
		# end new stuff for flipping... <-- this should happen before the anoms and the src_transform get to this point.

		base = rasterio.open( base )
		baseline_arr = base.read( 1 )
		baseline_meta = base.meta
		baseline_meta.update( compress='lzw' )
		output_arr = np.empty_like( baseline_arr )

		reproject( anom, output_arr, src_transform=src_transform, src_crs=src_crs, src_nodata=src_nodata,
					dst_transform=baseline_meta['affine'], dst_crs=baseline_meta['crs'],
					dst_nodata=dst_nodata, resampling=resampling[ resample_type ], SOURCE_EXTRA=1000 )
		
		return output_arr

# def sort_files( files, split_on='_', elem_month=-2, elem_year=-1 ):
# 	'''
# 	sort a list of files properly using the month and year parsed
# 	from the filename.  This is useful with SNAP data since the standard
# 	is to name files like '<prefix>_MM_YYYY.tif'.  If sorted using base
# 	Pythons sort/sorted functions, things will be sorted by the first char
# 	of the month, which makes thing go 1, 11, ... which sucks for timeseries
# 	this sorts it properly following SNAP standards as the default settings.
# 	ARGUMENTS:
# 	----------
# 	files = [list] list of `str` pathnames to be sorted by month and year. usually from glob.glob.
# 	split_on = [str] `str` character to split the filename on.  default:'_', SNAP standard.
# 	elem_month = [int] slice element from resultant split filename list.  Follows Python slicing syntax.
# 		default:-2. For SNAP standard.
# 	elem_year = [int] slice element from resultant split filename list.  Follows Python slicing syntax.
# 		default:-1. For SNAP standard.
# 	RETURNS:
# 	--------
# 	sorted `list` by month and year ascending. 
# 	'''
# 	import pandas as pd
# 	months = [ int(fn.split('.')[0].split( split_on )[elem_month]) for fn in files ]
# 	years = [ int(fn.split('.')[0].split( split_on )[elem_year]) for fn in files ]
# 	df = pd.DataFrame( {'fn':files, 'month':months, 'year':years} )
# 	df_sorted = df.sort_values( ['year', 'month' ] )
# 	return df_sorted.fn.tolist()

# def only_years( files, begin=1901, end=2100, split_on='_', elem_year=-1 ):
# 	'''
# 	return new list of filenames where they are truncated to begin:end
# 	ARGUMENTS:
# 	----------
# 	files = [list] list of `str` pathnames to be sorted by month and year. usually from glob.glob.
# 	begin = [int] four digit integer year of the begin time default:1901
# 	end = [int] four digit integer year of the end time default:2100
# 	split_on = [str] `str` character to split the filename on.  default:'_', SNAP standard.
# 	elem_year = [int] slice element from resultant split filename list.  Follows Python slicing syntax.
# 		default:-1. For SNAP standard.
# 	RETURNS:
# 	--------
# 	sliced `list` to begin and end year.
# 	'''
# 	import pandas as pd
# 	years = [ int(fn.split('.')[0].split( split_on )[elem_year]) for fn in files ]
# 	df = pd.DataFrame( { 'fn':files, 'year':years } )
# 	df_slice = df[ (df.year >= begin ) & (df.year <= end ) ]
# 	return df_slice.fn.tolist()