# # # run the 2 wrapper scripts that fire off jobs on ATLAS -- run this script from atlas head node.
import subprocess

# MINMAX VERSION OF DELTA
# RUN CRU first since it takes slightly longer with spatial interpolation
done = subprocess.call([ 'ipython', '/workspace/UA/malindgren/repos/downscale/snap_scripts/epscor_sc/wrap_downscaler_cru_slurm_epscor_sc_minmax.py' ])

# RUN CMIP5
done = subprocess.call([ 'ipython', '/workspace/UA/malindgren/repos/downscale/snap_scripts/epscor_sc/wrap_downscaler_cmip5_slurm_epscor_sc_minmax.py' ])