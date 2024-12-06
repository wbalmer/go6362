README

______


GO 6362 `pRT` retrieval cookbook

Relies on `petitRADTRANS` version 3, https://petitradtrans.readthedocs.io/en/latest/content/installation.html

and changes on wbalmer's fork, and the "hpf_nirspec_data" branch, https://github.com/wbalmer/petitRADTRANS/tree/hpf_nirspec_data


## installation on sci.stsci.edu

1) create a new virtual env with conda: `conda create -n prt3 python=3.11`
2) install chromium, selenium via conda: `conda install esss::chromium conda-forge::selenium`
3) pip is installed when python=3.11 was specified in the conda create, so we can install prt3 prerequisities with pip: `pip install numpy==1.24 cython meson-python ninja`
4) install multinest and pymultinest through conda (this is much easier than the alternative): `conda install conda-forge::pymultinest`
5) then, install mpi4y via conda: `conda install gxx_linux-64` and `pip install mpi4py`, this will likely downgrade the mpich that was installed above.
6) clone fork from git to the code directory. first, `cd /astro/epsig/GO6362/code/`, then `git clone https://github.com/wbalmer/petitRADTRANS.git`, `cd petitRADTRANS` and `git checkout hpf_nirspec_data`
7) install prt3 with the retrieval module: `pip install -e .[retrieval] --no-build-isolation`
8) install species and therefore spectres via pip : `pip install species`
9) open python and set the input data directory to the scratch subdir:
   ```
   from petitRADTRANS.config import petitradtrans_config_parser
   petitradtrans_config_parser.set_input_data_path(r"/astro/epsig/GO6362/code/prt3/input_data")
   ```
10) still in the python terminal, test the package:
   ```
   from petitRADTRANS.radtrans import Radtrans
   radtrans = Radtrans(line_species=['CH4'])
   ```
11) then, you can run e.g. `mpiexec -n 16 python prt_retrieval_test_interp_manyiso.py`

## installation on rockfish.jhu.edu

1) create a new virtual env with conda: `conda create -n prt3 python=3.11`
2) install chromium via conda: `conda install esss::chromium`
3) pip is installed when python=3.11 was specified in the conda create, so we can install prt3 prerequisities with pip: `pip install numpy meson-python ninja`
4) because mpi is already on rockfish, we need to avoid trying to install it via conda and instead install mpi4py in our home dir, so that the paths all work out. so `cd ~/mpi4py-3.1.5` and `pip install .` and then `cd ~`
5) clone fork from git `git clone https://github.com/wbalmer/petitRADTRANS.git` and `git checkout hpf_nirspec_data`
6) install prt3 using pip `pip install -e .[retrieval] --no-build-isolation`
7) install species and therefore spectres via pip : `pip install species`
8) open python and set the input data directory to the scratch subdir:
   ```
   from petitRADTRANS.config import petitradtrans_config_parser
   petitradtrans_config_parser.set_input_data_path(r"/scratch4/rleheny1/wbalmer1/prt3/input_data")
   ```
9) still in the python terminal, test the package:
   ```
   from petitRADTRANS.radtrans import Radtrans
   radtrans = Radtrans(line_species=['CH4'])
   ```
10) now set up Multinest:
   ```
   cd ~
   ml cmake
   git clone https://github.com/JohannesBuchner/MultiNest
   cd MultiNest/build
   cmake ..
   make
   ```
10) then, you can run e.g. `mpiexec -n 16 python prt_retrieval_test_interp_manyiso.py`