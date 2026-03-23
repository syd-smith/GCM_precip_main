#Divergent Trajectories for Summer Precipitation in the Great Salt Lake Basin

##Project Description
The Great Salt Lake Basin Integrated Plan (GSLBIP) is used to determine water allocation across the Salt Lake Region. To build a plan for the future, a greater understanding of water entering the system through precipitation must be met through analysis of climatological variables. While the majority of the water budget in the Great Salt Lake Basin (GSLB) is from snowpack, understanding changes in summer precipitation due to climate change is necesary in informing resilient water management strategies. This study focuses on exploring possible future summer hydroclimates over the Great Salt Lake Basin using 27 CMIP6 model ensembles. Data were statistically downscaled to 4km resolution using [Multivariate Adaptive Constructed Analogs version 2](https://zenodo.org/records/16747912) (MACAv2). While models across this dataset project substaintial warming across all models and emission scenarios, changes in precipitation remain uncertain. Outcomes can vary as much as projecting future precipitation doubling or being cut in half. Differences in precipitation outcomes largely reflect how individual models represent summer convection, cloud processes, and circulation dynamics. However, a models historical performance in simulating precipitation remains uncorrelated to its projected changes in precipitation. Rather a heteroskedastic relationship emerged showing that models with a dry precipitation bias and less temporal variation in precipitation across the historical period produce a wider range in projected precipitation outcomes. Thus model performance cannot be used to inform substantial model culling. Such findings hightlight the importance that stakeholders consider a wide range in precipitation outcomes in their water management strategies as uncertainty in future precipitation remains. This repository contains the code used to produce numerous figures analyzed in this study. 

##Folder Structure
```
.
├──CMIP6                # GCM data downloaded with intake_esgf scripts is initally stored here but should be moved to INPUT_DATA
├──GCM_vs_MACA          # Defines GSLB and MACA domains, plots coarse GCM data next to downscaled MACA data
├──INPUT_DATA           # Where all inputs must be housed to run code
├──JJA_climate_change   # Figures showing projected changes in summer temperature and precipitation
├──from_court           # Scripts from Court
├──from_savanna         # Scripts from Savanna
├──model_performance    # Evaluation of the historical performance of GCMs
├──tool_belt            # Scripts of frequently used functions
├──variable_mapping     # Maps used to analyze models difference in precipitation outcomes at a synoptic scale
├──.gitignore           # Note that all .png and .nc files are ignored
└──README.md
```

##Repository Outputs


##Repository Inputs
###Observational Data - gridMet 


###CMIP6 GCM Data


###Downscaled Data - MACAv2
