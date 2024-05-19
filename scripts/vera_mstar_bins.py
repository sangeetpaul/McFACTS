#!/usr/bin/env python3
######## Imports ########
import numpy as np
import os
from os.path import expanduser, join, isfile, isdir
from basil.relations import Neumayer_early_NSC_mass, Neumayer_late_NSC_mass
from basil.relations import SchrammSilvermanSMBH_mass_of_GSM as SMBH_mass_of_GSM

######## Arg ########
def arg():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mstar-min", default=1e9, type=float,
        help="Minimum galactic stellar mass")
    parser.add_argument("--mstar-max", default=1e13, type=float,
        help="Maximum galactic stellar mass")
    parser.add_argument("--nbins", default=9, type=int, help="Number of stellar mass bins")
    parser.add_argument("--wkdir", default='./run_many', help="top level working directory")
    parser.add_argument("--mcfacts-exe", default="./scripts/mcfacts_sim.py", help="Path to mcfacts exe")
    parser.add_argument("--vera-plots-exe", default="./scripts/vera_plots.py", help="Path to Vera plots script")
    parser.add_argument("--fname-nal", default=join(expanduser("~"), "Repos", "nal-data", "GWTC-2.nal.hdf5" ),
        help="Path to Vera's data from https://gitlab.com/xevra/nal-data")
    parser.add_argument("--max-nsc-mass", default=1.e8, type=float,
        help="Maximum NSC mass (solar mass)")
    parser.add_argument("--number_of_timesteps", default=100, type=int,
        help="Number of timesteps (10,000 yrs by default)")
    parser.add_argument("--dynamics", action='store_true',
        help="Dynamics flag")
    parser.add_argument("--n_iterations", default=2, type=int,
        help="Number of iterations per mass bin")
    # Handle top level working directory
    opts = parser.parse_args()
    if not isdir(opts.wkdir):
        os.mkdir(opts.wkdir)
    assert isdir(opts.wkdir)
    opts.wkdir=os.path.abspath(opts.wkdir)
    # Check exe
    assert isfile(opts.mcfacts_exe)
    return opts

######## Main ########
def main():
    # Load arguments
    opts = arg()
    # Get mstar array
    mstar_arr = np.logspace(np.log10(opts.mstar_min),np.log10(opts.mstar_max), opts.nbins)
    # Calculate SMBH and NSC mass 
    SMBH_arr = SMBH_mass_of_GSM(mstar_arr)
    NSC_early_arr = Neumayer_early_NSC_mass(mstar_arr)
    NSC_late_arr = Neumayer_late_NSC_mass(mstar_arr)
    # Limit NSC mass to maximum value
    NSC_early_arr[NSC_early_arr > opts.max_nsc_mass] = opts.max_nsc_mass
    NSC_late_arr[NSC_late_arr > opts.max_nsc_mass] = opts.max_nsc_mass
    # Create directories for early and late-type runs
    if not isdir(join(opts.wkdir, 'early')):
        os.mkdir(join(opts.wkdir, 'early'))
    if not isdir(join(opts.wkdir, 'late')):
        os.mkdir(join(opts.wkdir, 'late'))

    # Initialize mcfacts arguments dictionary
    mcfacts_arg_dict = {
                        "--number_of_timesteps" : opts.number_of_timesteps,
                        "--dynamic_enc"         : int(opts.dynamics),
                        "--n_iterations"        : opts.n_iterations,
                        "--n_bins_max"          : 10_000,
                        "--fname-log"           : "out.log",
                       }
    mcfacts_args = ""
    for item in mcfacts_arg_dict:
        mcfacts_args = mcfacts_args + "%s %s "%(item, str(mcfacts_arg_dict[item]))

    ## Loop early-type galaxies
    for i in range(opts.nbins):
        # Extract values for this set of galaxies
        mstar = mstar_arr[i]
        mass_smbh = SMBH_arr[i]
        early_mass = NSC_early_arr[i]
        late_mass = NSC_late_arr[i]
        # Generate label for this mass bin
        mstar_str = "%.8f"%np.log10(mstar)
        # Generate directories
        early_dir = join(opts.wkdir, 'early', mstar_str)
        if not isdir(early_dir):
            os.mkdir(early_dir)
        late_dir = join(opts.wkdir, 'late', mstar_str)
        if not isdir(late_dir):
            os.mkdir(late_dir)
        # Make early iterations
        cmd = "python3 %s %s --work-directory %s --mass_smbh %f --M_nsc %f"%(
            opts.mcfacts_exe, mcfacts_args, early_dir, mass_smbh, early_mass)
        print(cmd)
        os.system(cmd)
        # Make plots for early iterations
        cmd = "python3 %s --fname-mergers %s/output_mergers_population.dat --fname-nal %s --cdf chi_eff chi_p M gen1 gen2 t_merge"%(
            opts.vera_plots_exe, early_dir, opts.fname_nal)
        print(cmd)
        os.system(cmd)
        # Make late iterations
        cmd = "python3 %s %s --work-directory %s --mass_smbh %f --M_nsc %f"%(
            opts.mcfacts_exe, mcfacts_args, late_dir, mass_smbh, late_mass)
        print(cmd)
        os.system(cmd)
        # Make plots for late iterations
        cmd = "python3 %s --fname-mergers %s/output_mergers_population.dat --fname-nal %s --cdf chi_eff chi_p M gen1 gen2 t_merge"%(
            opts.vera_plots_exe, late_dir, opts.fname_nal)
        print(cmd)
        os.system(cmd)
        
    return

######## Execution ########
if __name__ == "__main__":
    main()
