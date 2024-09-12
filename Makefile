# Declarations
.PHONY: all clean

all: clean tests plots #vera_plots
tests: mcfacts_sim

######## Definitions ########
#### Package ####
# Version number for the repository
# This is where you change the version number by hand. Not anywhere else.
# Alpha begins at 0.1.0
# Feature-complete Alpha begins at 0.2.0
# Beta begins at 0.3.0
VERSION=0.0.0

### Should work for everyone ###
# Current directory
#HERE=$(shell pwd)
HERE=./

#### Scripts ####
MCFACTS_SIM_EXE = ${HERE}/scripts/mcfacts_sim.py
POPULATION_PLOTS_EXE = ${HERE}/scripts/population_plots.py
VERA_PLOTS_EXE = ${HERE}/scripts/vera_plots.py
MSTAR_RUNS_EXE = ${HERE}/scripts/vera_mstar_bins.py
MSTAR_PLOT_EXE = ${HERE}/src/mcfacts/outputs/plot_mcfacts_handler_quantities.py

#### Setup ####
SEED=3456789012
#FNAME_INI= ${HERE}/recipes/p1_thompson.ini
FNAME_INI= ${HERE}/recipes/model_choice_old.ini
MSTAR_RUNS_WKDIR = ${HERE}/runs_mstar_bins
# NAL files might not exist unless you download them from
# https://gitlab.com/xevra/nal-data
# scripts that use NAL files might not work unless you install
# gwalk (pip3 install gwalk)
FNAME_GWTC2_NAL = ${HOME}/Repos/nal-data/GWTC-2.nal.hdf5
#Set this to change your working directory
wd=${HERE}

######## Instructions ########
#### Install ####

version: clean
	echo "__version__ = '${VERSION}'" > __version__.py
	echo "__version__ = '${VERSION}'" > src/mcfacts/__version__.py

install: clean version
	python -m pip install --editable .

setup: clean version
	source ~/.bash_profile && \
	conda activate base && \
	conda remove -n mcfacts-dev --all -y && \
	conda create --name mcfacts-dev "python>=3.10.4" pip "pytest" -c conda-forge -c defaults -y && \
	conda activate mcfacts-dev && \
	python -m pip install --editable .

unit_test: clean version
	source ~/.bash_profile && \
	conda activate mcfacts-dev && \
	pytest

#### Test one thing at a time ####

# do not put linebreaks between any of these lines. Your run will call a different .ini file
mcfacts_sim: clean
	mkdir -p runs
	cd runs; \
		python ../${MCFACTS_SIM_EXE} \
		--galaxy_num 10 \
		--fname-ini ../${FNAME_INI} \
		--fname-log out.log \
		--seed ${SEED}


plots: mcfacts_sim
	cd runs; \
	python ../${POPULATION_PLOTS_EXE} --fname-mergers ${wd}/output_mergers_population.dat --plots-directory ${wd}

vera_plots: mcfacts_sim
	python ${VERA_PLOTS_EXE} \
		--cdf chi_eff chi_p M gen1 gen2 t_merge \
		--verbose

mstar_runs:
	python ${MSTAR_RUNS_EXE} \
		--fname-ini ${FNAME_INI} \
		--number_of_timesteps 1000 \
		--n_bins_max 10000 \
		--galaxy_num 3 \
		--dynamics \
		--feedback \
		--mstar-min 1e9 \
		--mstar-max 1e13 \
		--nbins 33 \
		--scrub \
		--fname-nal ${FNAME_GWTC2_NAL} \
		--wkdir ${MSTAR_RUNS_WKDIR}
	python3 ${MSTAR_PLOT_EXE} --run-directory ${MSTAR_RUNS_WKDIR}
		

#### CLEAN ####

#TODO: Create an IO class that wraps the standard IO. This wrapper will keep a persistent log of all of the
#instantaneous files created. The wrapper would have a cleanup function, and can also report metrics :^)
#Plus, if we use a standard python IO library, we don't have to worry about rm / del and wildcards!

clean:
	rm -rf ${wd}/run*
	rm -rf ${wd}/runs/*
	rm -rf ${wd}/output_mergers*.dat
	rm -rf ${wd}/m1m2.png
	rm -rf ${wd}/merger_mass_v_radius.png
	rm -rf ${wd}/q_chi_eff.png
	rm -rf ${wd}/time_of_merger.png
	rm -rf ${wd}/merger_remnant_mass.png
	rm -rf ${wd}/gw_strain.png
	rm -rf ${wd}/out.log
	rm -rf ${wd}/mergers_cdf*.png
	rm -rf ${wd}/mergers_nal*.png
	rm -rf ${wd}/r_chi_p.png

clean_win:
	for /d %%i in (.\run*) do rd /s /q "%%i"
	for /d %%i in (.\output_mergers*.dat) do rd /s /q "%%i"
	del /q .\m1m2.png
	del /q .\merger_mass_v_radius.png
	del /q .\q_chi_eff.png
	del /q .\time_of_merger.png
	del /q .\merger_remnant_mass.png
	del /q .\gw_strain.png
	del /q .\out.log
	for /d %%i in (.\mergers_cdf*.png) do rd /s /q "%%i"
	for /d %%i in (.\mergers_nal*.png) do rd /s /q "%%i"
	del /q .\r_chi_p.png
