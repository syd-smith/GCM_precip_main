Created: Aug 29th, 2024
By: Savanna Wolvin, s.wolvin@utah.edu

Edited: Oct 5th, 2024
By: Savanna Wolvin, s.wolvin@utah.edu


>>> Variable is used in scripts


"REGION_STR": >>>
	"GSLBIP", used as a part of the namign convention for the MACA 
	downscaled GCM datasets to signify the region downscaled or name of the 
	project.

--------------------------------------------------------------------------------
Define Directories
--------------------------------------------------------------------------------

"BASE_DIR": >>>
	Define the base directory of all MACA folders.

"COARSE_DIR": >>>
	Define directory to save the coarse grid GCM data and to save the 
	coarse grid gridMET observational data. 

"GRIDMET_DIR": >>>
	Define directory to the fine grid gridMET observational data.

"GCM_DIR": >>> 
	Define directory to the coarse grid CMIP6 data.

"RSDS_DIR": >>>
	Define the directory to save the formulated solar radiation minimum and 
	maximum bounds which will also be used to load these values.

"OUTPUT_DIR": >>>
	Define directory where MACA downscaled CMIP6 variables will be stored. 

"CACHE_DIR": >>>
	Define directory to the GCM datasets, which is the same directory the 
	user should have made a symbolic link towards (e.g., {SAVE_PATH}/esgf/).

"INTAKE_ESGF_CATALOG": >>>
	Name to save the catalog of available models and experiments to as 
	.csv and .pkl files.
	

--------------------------------------------------------------------------------
Define Latitude and Longitude Bounds
--------------------------------------------------------------------------------

"COARSE_LAT_MIN": >>>
	Minimum latitude of the coarse 1-degree grid

"COARSE_LAT_MAX": >>>
	Maximum latitude of the coarse 1-degree grid

"COARSE_LON_MIN": >>>
	Minimum longitude of the coarse 1-degree grid

"COARSE_LON_MAX": >>>
	Maximum longitude of the coarse 1-degree grid

"FINE_LAT_TARGET_BOUNDS": >>>
	[Minimum, Maximum] latitude bounds of the downscaled variables, 
	previously chosen by Clay Lewis - email 6/20/2024

"FINE_LON_TARGET_BOUNDS": >>>
	[Minimum, Maximum] longitude bounds of the downscaled variables, 
	previously chosen by Clay Lewis - email 6/20/2024 


--------------------------------------------------------------------------------
Define GCM Simulations and MACA Variables
--------------------------------------------------------------------------------

"EXPERIMENTS": >>>
	GCM experiment names listed between a subset of "historical" names, 
	"SSP" names, and "ALL" the experiment names together.

--------------------------------------------------------------------------------
Define Historical/Observational Bounds and Variables
--------------------------------------------------------------------------------

"HISTORICAL_YEARS": >>>
	[Start, End] years of the GCM historical simulations, outer limits are
	[1979, 2014]

"GRIDMET_VARIABLES": >>>
	Variable names to processes from the gridMET data.

"GRIDMET_VAR_NAMES": >>>
	Long names of the gridMET variable datasets.

"GRIDMET_VAR_UNITS": >>>
	Expected variable units of the gridMET datasets.

--------------------------------------------------------------------------------
Define Future Simulation Bounds and Variables
--------------------------------------------------------------------------------

"FUTURE_YEARS": >>>
	[Start, End] years of the GCM SSP simulations, outer limits are
	[2015, 2099]

"GCM_VARIABLES": >>>
	Variables to process from the GCM simulations.

"GCM_VARIABLE_UNITS": >>>
	Units of the variables from the GCM simulations.

--------------------------------------------------------------------------------
Define MACA Downscaled Variables
--------------------------------------------------------------------------------

"MACA_VARIABLES": >>>
	Variables to be processed by MACA downscaling. Make sure "pr" is 
	variable number 5 and "huss" is variable number 9. Unless you make 
	changes to "VAR_OF_PREC", "MACA_VARIABLE_UNITS", and 
	"MACA_VAR_MULTIPLY_OR_ADDITIVE".

"VAR_OF_PREC": ??? not used but loaded in
	Define index of the "pr" variable in "MACA_VARIABLES".

"MACA_VARIABLE_UNITS": ??? not used in downscaling
	Define units of the "MACA_VARIABLES".

"MACA_VAR_MULTIPLY_OR_ADDITIVE": >>>
	Define if the variables are multiplicative (1) or additive (0). For 
	example, "pr" and "huss" are multiplicative and others are not.

"CUTOFF": >>>

"DRY_DAY_THRES_COARSE": >>>

"DRY_DAY_THRES_FINE": >>>

--------------------------------------------------------------------------------
Epoch Adjustment Parameters
--------------------------------------------------------------------------------

"EA_DAY_WINDOW": >>>
	Epoch Adjustment (EA) used for initial bias correction procedures
	"EA_DAY_WINDOW" is a moving mean over days. This is used for analog 
	construction to avoid disappearing analogs when conditions become novel. 
	MUST be an odd number.

"EA_YR_WINDOW": >>>
	Epoch Adjustment (EA) used for initial bias correction procedures
	"EA_YR_WINDOW" is a moving mean over years. This is used for analog 
	construction to avoid disappearing analogs when conditions become novel.
	MUST be an odd number.

"EA_VARIABLES": >>>
	Indicate if Epoch Adjustment is applied to individual variables or not. 
	This adjustment removes the yearly and seasonal trends based on a moving 
	average of a "EA_DAY_WINDOW" and "EA_YR_WINDOW". To apply Epoch 
	Adjustment (EA), "EA_VARIABLES"=1, to NOT apply EA, "EA_VARIABLES"=0.

	We do not apply Epoch Adjustment for Relative Humidity (RH), since the 
	data should stay between 0% to 100%. Probably only important to use for 
	temperature ("tasmax", "tasmin"), specific humidity ("huss"), and 
	precipitation ("pr"). 


--------------------------------------------------------------------------------
Bias Correction Parameters
--------------------------------------------------------------------------------

"BC_SEMI_DAY_WINDOW_MULT": >>>
	Full window in Bias Correction (BC) is being saved.  	
	i.e., BC_DAY_WINDOW = 1 + 2 * BC_SEMI_WINDOW

"BC_SEMI_DAY_WINDOW_ADD": >>>
	Was 5, then changed to 15 (2024). Only this window is saved in Bias 
	Correction (BC). But window 3 times as large is used for CDF. 
	BC_DAY_WINDOW = 1 + 2 * BC_SEMI_WINDOW

"BC_MAX_PR_RATIO: >>>
	Limit Precipitation scaling to a factor of 5. 


--------------------------------------------------------------------------------
Analog Selection Parameters
--------------------------------------------------------------------------------

"MACA_SEMI_DAY_WINDOW": >>>
	The MACA window is the 1/2 size of the calender window over which the 
	analogs are selected. 45-days means that the analogs for 1-March can be 
	taken from 15-January to 15-April. 
	i.e., MACA_DAY_WINDOW = 1 + 2 * MACA_SEMI_DAY_WINDOW

"MACA_NUM_BEST_MODELS": >>>
	The number of analogs to use; note that we now apply a residual 
	correction factor through bilinear interpolation that effectively 
	"solves" the analog residual problem.

"ERRORYES": >>>


"GRID_CHUNK_PTS": >>>
	The pixel size of each grid chunk to run in parallel.





