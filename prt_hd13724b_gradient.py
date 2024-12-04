#!/usr/bin/env python
# coding: utf-8

# Let's start by importing everything we need.
import os
# To not have numpy start parallelizing on its own
os.environ["OMP_NUM_THREADS"] = "1"

# for rockfish 
import sys
sys.setdlopenflags(os.RTLD_NOW | os.RTLD_GLOBAL)

import numpy as np
import matplotlib.pyplot as plt

import petitRADTRANS as prt
from petitRADTRANS import physical_constants as cst

# Import the class used to set up the retrieval.
from petitRADTRANS.retrieval import Retrieval,RetrievalConfig
# Import Prior functions, if necessary.
from petitRADTRANS.retrieval.utils import gaussian_prior
# Import atmospheric model function
from petitRADTRANS.retrieval.models import emission_model_diseq, gradient_profile_emission


# Define the pRT run setup
retrieval_config = RetrievalConfig(
    retrieval_name="HD13724B_test", # give a useful name for your retrieval
    run_mode="retrieve",  # 'retrieve' to run, or 'evaluate' to make plots
    amr=True,  # adaptive mesh refinement, slower if True
    scattering_in_emission=True  #  add scattering for emission spectra clouds
)

import petitRADTRANS # need to get the name for the example data
path_to_data = "./"

retrieval_config.add_data(
    'NIRSPEC_G395H_HPF',
    path_to_data+"hd13724b_nirspec_nonans.txt",
    data_resolution=5000,
    model_resolution=10000,
    model_generating_function = gradient_profile_emission,
    resample=True,
    filters=True,
    radvel=True,
    line_opacity_mode='lbl'
)

retrieval_config.add_data(
    'SPHERE_IFU',
    path_to_data+"hd13724B_sphere.txt",
    data_resolution=50,
    model_resolution=100,
    model_generating_function = gradient_profile_emission,
    line_opacity_mode='c-k'
)

retrieval_config.add_photometry(
    path_to_data + 'hd13724B_sphere_phot.txt',
    gradient_profile_emission,
    model_resolution=40
)

# todo: add other spectra

# Add parameters, and priors for free parameters

# This run uses the model of Molliere (2020) for HR8799e
# The lambda function provide uniform priors

# Distance to the planet in cm
retrieval_config.add_parameter(
    name='D_pl',
    free=False,
    value=43.4486 * cst.pc
)

# Log of the surface gravity in cgs units.
retrieval_config.add_parameter(
    'log_g',
    True,
    transform_prior_cube_coordinate = lambda x : 2 + 3.5 * x
)

# Planet mass in mj
retrieval_config.add_parameter(
    'mass',
    True,
    transform_prior_cube_coordinate=lambda x : gaussian_prior(x, 61, 4) * cst.m_jup
)

# hpf nirspec hyperparameters
retrieval_config.add_parameter(
    'NIRSPEC_G395H_HPF_nodes',
    False,
    value=60
)

retrieval_config.add_parameter(
    'NIRSPEC_G395H_HPF_radvel',
    True,
    transform_prior_cube_coordinate=lambda x : ( -15 + 30 * x)
)

retrieval_config.add_parameter(
    'NIRSPEC_G395H_HPF_R_slope',
    True,
    transform_prior_cube_coordinate=lambda x : ( 100 + 1900 * x)
)

retrieval_config.add_parameter(
    'NIRSPEC_G395H_HPF_R_int',
    True,
    transform_prior_cube_coordinate=lambda x : ( 200 + 2800 * x)
)

n_layers = 6
retrieval_config.add_parameter('N_layers', False, value = n_layers)
retrieval_config.add_parameter('T_bottom', True,
                            transform_prior_cube_coordinate = \
                            lambda x : 2000.0 + 20000.0*x)

#dts = [0.07,0.10,0.18,0.27,0.24,0.25]
retrieval_config.add_parameter(f'PTslope_1',
                            True,
                            transform_prior_cube_coordinate = \
                                lambda x : gaussian_prior(x,0.25,0.025))
retrieval_config.add_parameter(f'PTslope_2',
                            True,
                            transform_prior_cube_coordinate = \
                                lambda x : gaussian_prior(x,0.25,0.045))
retrieval_config.add_parameter(f'PTslope_3',
                            True,
                            transform_prior_cube_coordinate = \
                                lambda x : gaussian_prior(x,0.26,0.05))
retrieval_config.add_parameter(f'PTslope_4',
                            True,
                            transform_prior_cube_coordinate = \
                                lambda x : gaussian_prior(x,0.2,0.05))
retrieval_config.add_parameter(f'PTslope_5',
                            True,
                            transform_prior_cube_coordinate = \
                                lambda x : gaussian_prior(x,0.12,0.045))
retrieval_config.add_parameter(f'PTslope_6',
                            True,
                            transform_prior_cube_coordinate = \
                                lambda x : gaussian_prior(x,0.07,0.07))

# Chemistry
# A 'free retrieval' would have each line species as a parameter
# Using a (dis)equilibrium model, we only supply bulk parameters.
# Carbon quench pressure
retrieval_config.add_parameter(
    'log_pquench',
    True,
    transform_prior_cube_coordinate=lambda x : -6.0 + 9.0 * x
    )
# Metallicity [Fe/H]
retrieval_config.add_parameter(
    'Fe/H',
    True,
    transform_prior_cube_coordinate=lambda x : -1.5 + 3.0 * x
)
# C/O ratio
retrieval_config.add_parameter(
    'C/O',
    True,
    transform_prior_cube_coordinate=lambda x : 0.1+1.5*x
)
# Clouds
# Based on an Ackermann-Marley (2001) cloud model
# Width of particle size distribution
retrieval_config.add_parameter(
    'sigma_lnorm',
    True,
    transform_prior_cube_coordinate=lambda x : 1.05 + 1.95 * x
)
# Vertical mixing parameters
retrieval_config.add_parameter(
    'log_kzz',
    True,
    transform_prior_cube_coordinate=lambda x : 5.0 + 8.0 * x
)
# Sedimentation parameter
retrieval_config.add_parameter(
    'fsed',
    True,
    transform_prior_cube_coordinate=lambda x : 1.0 + 10.0 * x
)

# Define opacity species to be included

retrieval_config.set_rayleigh_species(['H2', 'He'])
retrieval_config.set_continuum_opacities(['H2-H2', 'H2-He'])
retrieval_config.set_line_species(
    [
        # '1H2-16O__POKAZATEL.R1e6_0.3-28mu',
        # '12C-16O__HITEMP',
        # '13C-16O__HITRAN',
        'H2O',
        '12CO',
        '13CO',
        '12C-18O',
        # '12C-17O'
        # 'H2O__POKAZATEL.R1e6',
        # 'CO-NatAbund__HITEMP.R1e6',
        'CH4',
        'CO2',
        'HCN',
        'H2S',
        'FeH',
        'NH3',
        'PH3',
        'Na',
        'K',
        'TiO',
        'VO',
        'SiO'
    ],
    eq = True
)

retrieval_config.add_cloud_species('Fe(s)_crystalline__DHS', eq=True, abund_lim=(-3.5, 1.0))
retrieval_config.add_cloud_species('MgSiO3(s)_crystalline__DHS', eq=True, abund_lim=(-3.5, 1.0))
retrieval_config.add_cloud_species('KCl(s)_crystalline__DHS', eq=True, abund_lim=(-3.5, 1.0))

# add isotopes as freely retrieved so we can do the ratio
retrieval_config.add_parameter(
    '12CO',
    True,
    transform_prior_cube_coordinate=lambda x : -10. + 10 * x
)

retrieval_config.add_parameter(
    '13CO',
    True,
    transform_prior_cube_coordinate=lambda x : -10. + 10 * x
)

retrieval_config.add_parameter(
    '12C-18O',
    True,
    transform_prior_cube_coordinate=lambda x : -10. + 10 * x
)

for specie in retrieval_config.cloud_species:
    
    retrieval_config.add_parameter(
        'eq_scaling_'+specie.split('_')[0],
        True,
        transform_prior_cube_coordinate=lambda x : -3.5 + 4.5 * x
    )

# Before we run the retrieval, let's set up plotting.

# Define what to put into corner plot if run_mode == 'evaluate'
# retrieval_config.parameters['planet_radius'].plot_in_corner = True
# retrieval_config.parameters['planet_radius'].corner_label = r'$R_{\rm P}$ ($\rm R_{Jup}$)'
# retrieval_config.parameters['planet_radius'].corner_transform = lambda x : x / cst.r_jup_mean
retrieval_config.parameters['mass'].plot_in_corner = True
retrieval_config.parameters['mass'].corner_label = r'$M_{\rm P}$ ($\rm M_{Jup}$)'
retrieval_config.parameters['mass'].corner_transform = lambda x : x / cst.m_jup
retrieval_config.parameters['log_g'].plot_in_corner = True
# retrieval_config.parameters['log_g'].corner_ranges = [2., 5.]
retrieval_config.parameters['log_g'].corner_label = "log g"
retrieval_config.parameters['fsed'].plot_in_corner = True
retrieval_config.parameters['log_kzz'].plot_in_corner = True
retrieval_config.parameters['log_kzz'].corner_label = "log Kzz"
retrieval_config.parameters['C/O'].plot_in_corner = True
retrieval_config.parameters['Fe/H'].plot_in_corner = True
retrieval_config.parameters['log_pquench'].plot_in_corner = True
retrieval_config.parameters['log_pquench'].corner_label = "log pquench"

retrieval_config.parameters['12CO'].plot_in_corner = True
retrieval_config.parameters['12CO'].corner_label = r"$^{12}CO$"
retrieval_config.parameters['13CO'].plot_in_corner = True
retrieval_config.parameters['13CO'].corner_label = r"$^{13}CO$"
retrieval_config.parameters['12C-18O'].plot_in_corner = True
retrieval_config.parameters['12C-18O'].corner_label = r"$C^{18}O$"

retrieval_config.parameters['NIRSPEC_G395H_HPF_radvel'].plot_in_corner = True
retrieval_config.parameters['NIRSPEC_G395H_HPF_radvel'].corner_label = "RV_bd"

retrieval_config.parameters['NIRSPEC_G395H_HPF_R_slope'].plot_in_corner = True
retrieval_config.parameters['NIRSPEC_G395H_HPF_R_slope'].corner_label = "$R$ slope"

retrieval_config.parameters['NIRSPEC_G395H_HPF_R_int'].plot_in_corner = True
retrieval_config.parameters['NIRSPEC_G395H_HPF_R_int'].corner_label = "$R$ int"

for spec in retrieval_config.cloud_species:
    cname = spec.split('_')[0]
    retrieval_config.parameters['eq_scaling_' + cname].plot_in_corner = True
    retrieval_config.parameters['eq_scaling_' + cname].corner_label = cname

# Define axis properties of spectral plot if run_mode == 'evaluate'
retrieval_config.plot_kwargs["spec_xlabel"] = 'Wavelength [micron]'

retrieval_config.plot_kwargs["spec_ylabel"] = "Flux [W/m2/micron]"
retrieval_config.plot_kwargs["y_axis_scaling"] = 1.0
retrieval_config.plot_kwargs["xscale"] = 'linear'
retrieval_config.plot_kwargs["yscale"] = 'linear'
retrieval_config.plot_kwargs["resolution"] = None  # maximum resolution, will rebin the data
# retrieval_config.plot_kwargs["nsample"] = 1  # if we want a plot with many sampled spectra

# Define from which observation object to take P-T in evaluation mode (if run_mode == 'evaluate'), add PT-envelope plotting options
retrieval_config.plot_kwargs["take_PTs_from"] = 'NIRSPEC_G395H_HPF'
retrieval_config.plot_kwargs["temp_limits"] = [150, 15000]
retrieval_config.plot_kwargs["press_limits"] = [1e3, 1e-6]


retrieval = Retrieval(
    retrieval_config,
    output_directory="./",
    evaluate_sample_spectra=False,
    test_plotting=False
)


run_retrieval = True

if run_retrieval:
    retrieval.run(
        n_live_points=960,
        sampling_efficiency=0.05,
        const_efficiency_mode=True,
        resume=False,
        seed=-1  # ⚠️ seed should be removed or set to -1 in a real retrieval, it is added here for reproducibility
    )

plot = False

if plot:
    retrieval.plot_all(contribution=True)
