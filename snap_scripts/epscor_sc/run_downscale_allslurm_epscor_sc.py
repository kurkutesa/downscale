# # # run the 2 wrapper scripts that fire off jobs on ATLAS -- run this script from atlas head node.
import subprocess

# RUN CRU first since it takes longer
done = subprocess.call([ 'ipython', '/workspace/UA/malindgren/repos/downscale/snap_scripts/epscor_se/wrap_downscaler_cru_slurm_epscor_se.py' ])

# RUN CMIP5
done = subprocess.call([ 'ipython', '/workspace/UA/malindgren/repos/downscale/snap_scripts/epscor_se/wrap_downscaler_cmip5_slurm_epscor_se.py' ])