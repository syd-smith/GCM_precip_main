# Divergent Trajectories for Summer Precipitation in the Great Salt Lake Basin (GSLB)

## Project Description
The Great Salt Lake Basin Integrated Plan (GSLBIP) is used to determine water allocation across the Salt Lake Region. To build a plan for the future, a greater understanding of water entering the system through precipitation must be met through analysis of climatological variables. While the majority of the water budget in the Great Salt Lake Basin is from snowpack, understanding changes in summer precipitation due to climate change is necesary in informing resilient water management strategies. This study focuses on exploring possible future summer hydroclimates over the Great Salt Lake Basin using 27 CMIP6 model ensembles. Data were statistically downscaled to 4km resolution using [Multivariate Adaptive Constructed Analogs version 2](https://zenodo.org/records/16747912) (MACAv2). While models across this dataset project substaintial warming across all models and emission scenarios, changes in precipitation remain uncertain. Outcomes can vary as much as projecting future precipitation doubling or being cut in half. Differences in precipitation outcomes largely reflect how individual models represent summer convection, cloud processes, and circulation dynamics. However, a models historical performance in simulating precipitation remains uncorrelated to its projected changes in precipitation. Rather a heteroskedastic relationship emerged showing that models with a dry precipitation bias and less temporal variation in precipitation across the historical period produce a wider range in projected precipitation outcomes. Thus model performance cannot be used to inform substantial model culling. Such findings hightlight the importance that stakeholders consider a wide range in precipitation outcomes in their water management strategies as uncertainty in future precipitation remains. This repository contains the code used to produce numerous figures analyzed in this study. 

## Folder Structure
```
.
├──CMIP6                      #GCM data downloaded with intake_esgf scripts is initally stored here but should be moved to INPUT_DATA
├──GCM_vs_MACA                #Defines GSLB and MACA domains, plots coarse GCM data next to downscaled MACA data
│   └── figure1.py
├──INPUT_DATA                 #Where all inputs must be housed to run code
├──JJA_climate_change         #Figures showing projected changes in summer temperature and precipitation
|   ├── figure2.py
│   └── PCA_vs_climate_change
│       └── figure4.py
├──from_court                 #Scripts from Court
├──from_savanna               #Scripts from Savanna
├──model_performance          #Evaluation of the historical performance of GCMs
|   ├── figure_S5.py
│   └── correlation_matrix
│       └── figure_S6.py
├──tool_belt                  #Scripts of frequently used functions
├──variable_mapping           #Maps used to analyze models difference in precipitation outcomes at a synoptic scale
│   └── final_figures.py      #Contains both figure5 and figure_S4
├──.gitignore                 #Note that all .png and .nc files are ignored
└──README.md
```

## Repository Output Descriptions
Scripts output figures as PNGs to the respective current working directory.
#### Figure 1 - [GCM_precip_main/GCM_vs_MACA/figure1.py](https://github.com/syd-smith/GCM_precip_main/blob/main/GCM_vs_MACA/figure1.py)
Map of summertime (June–August) mean precipitation during 1979–2014 for (a)
CMIP6 coarse resolution (1◦) data and (b) MACAv2-downscaled CMIP6 high resolution product
(4-km). Boundaries for the Great Salt Lake Basin (GSLB) marked as red contour. The map
extent reflects the MACA domain used in the downscaling process (latitude: 36-43N, longitude:
115.1-108W).

#### Figure 2 - [GCM_precip_main/JJA_climate_change/figure2.py](https://github.com/syd-smith/GCM_precip_main/blob/main/JJA_climate_change/figure2.py)
Scatter plot showing the relationship between temperature change (far-future,
2070–2099, minus historical, 1979–2014; K) and the precipitation ratio (far-future, 2070–2099,
divided by historical, 1979–2014) across different Shared Socioeconomic Pathways (SSPs), based
on MACAv2-downscaled CMIP6 projections. Each point represents an individual model simula-
tion averaged over the Great Salt Lake Basin (GSLB), outlined in red in Figure 1. Colors denote
different SSP scenarios.

#### Figure 4 - [GCM_precip_main/JJA_climate_change/PCA_vs_climate_change/figure4.py](https://github.com/syd-smith/GCM_precip_main/blob/main/JJA_climate_change/PCA_vs_climate_change/figure4.py)
Scatter plots showing the relationship between temperature change (far future
minus historical; K) and precipitation ratio (far future divided by historical) across Shared So-
cioeconomic Pathways (SSPs), based on MACAv2-downscaled CMIP6 projections. (a) is shaded
by the first principal component (PC1), and (b) is shaded by the second principal component
(PC2). Each point represents an individual model simulation averaged over the Great Salt Lake
Basin (GSLB), outlined in red in Figure 1.

#### Figure 5 - [GCM_precip_main/variable_mapping/final_figures.py](https://github.com/syd-smith/GCM_precip_main/blob/main/variable_mapping/final_figures.py)
Spatial patterns of projected JJA (June–August) change from the historical pe-
riod (1979–2014) to the far future (2070–2099). (a–c) Percent change in precipitation flux
(kg m−2 s−1), including both solid and liquid phases. (d–f) Change in surface (skin) tempera-
ture (K). (g–i) Change in near-surface (2 m) specific humidity (g kg−1). Wet, Moderate, and Dry
cases are indicated in Figure. 2.

#### Supplemental Figure 4 - [GCM_precip_main/variable_mapping/final_figures.py](https://github.com/syd-smith/GCM_precip_main/blob/main/variable_mapping/final_figures.py)
Spatial patterns of JJA (June–August) mean and projected changes at 500 hPa.
(a–c) Mean geopotential height (m; contours) with mean wind vectors (u, v; m s−1) for the
historical period. (d–f) Projected change in geopotential height (m; contours) with change in
wind vectors (u, v; m s−1) from the historical to the future period.

#### Supplemental Figure 5 - [GCM_precip_main/model_performance/figure_S5.py](https://github.com/syd-smith/GCM_precip_main/blob/main/model_performance/figure_S5.py)
Historical performance of GCMs relative to GridMet, and percent change in
projected precipitation (shading). (a) Precipitation temporal variance ratio versus precipitation
bias ratio. (b) Minimum temperature temporal variance ratio versus minimum temperature bias
(K). (c) Maximum temperature temporal variance ratio versus maximum temperature bias (K).
Each point represents one model. The dotted vertical and horizontal lines mark the ideal values.
The star denotes the reference performance. Points closer to the intersection of the dotted lines
indicate better agreement with observations in both mean and variability.

#### Supplemental Figure 6 - [GCM_precip_main/model_performance/corrrelation_matrix/figure_S6.py](https://github.com/syd-smith/GCM_precip_main/blob/main/model_performance/correlation_matrix/figure_S6.py)
Relationship between projected precipitation and model performance metrics across
models. (a) Projected precipitation versus precipitation bias. (b) Projected precipitation versus
temporal precipitation variance ratio. Each point represents one model. The red line shows the
least-squares linear regression. The spread of the points around the red line indicate statistically
significant heteroskedasticity, meaning that the variance of the precipitation projection decreases
as the bias increases.


## Repository Inputs
All input data must be stored under the directory [INPUT_DATA](https://github.com/syd-smith/GCM_precip_main/tree/main/INPUT_DATA). Note that sub-directories titled "gridMET", "GCM", and "MACA" must be created if not rendered properly when downloading the respository following the structure outlined below.
```
.
├── INPUT_DATA
|   ├── gridMET   
|   ├── GCM
│   └── MACA
```

### Observational Data - gridMet 
gridMET data are high resolution data (~4km) that covers the contiguous US dating from 1979-yesterday. This observational data was used in the MACA downscaling process but also provides reference data for [model_performance](https://github.com/syd-smith/GCM_precip_main/tree/main/model_performance) calculations. To download data, navigate to the "Download" on [this website](https://www.climatologylab.org/gridmet.html) and follow instructions. Regardless of where data initially download, it must be moved to INPUT_DATA/gridMET for figures requiring the data to be run properly. All data should be stored as a single netcdf file containing data from 1979-2014 and titled using the structure as follows: **gsl_region_pr_1979-2014.nc**. Only gridMET variable abbbreviations should be used to title the netcdf files. See table below for required variables and abbreviations. 
| **griMET Variable Name** | **gridMET Variable Abbreviation** | **MACA Variable Equivalent** | **Units** |
| :----------------------: | :-------------------------------: | :--------------------------: | :-------: |
| precipitation_amount | pr | pr | mm |
| air_temperature | tmmn | tasmin | K |
| air_temperature | tmmx | tasmax | K |
| specific_humidity | sph | huss | kg/kg |
| surface_downwelling_shortwave_flux_in_air | srad | rsds | W/m^-2^ |
| uas | uas | uas | m/s^-1^ |
| vas | vas | vas | m/s^-1^ |

### CMIP6 GCM Data
MACA data were downscaled from coarse CMIP6 data. Data were used to inspect climatological, synpotic-scale conditions of the contiguous US and surrounding areas to better understand spatial patterns that might cause greater increases in precipitation by the end of the century (see figure 5 and supplemental figure 4). In addition, data were used to evaluate a models historical performance over the MACA domain. Daily data were used for historical model performance calculations [(model_performance)](https://github.com/syd-smith/GCM_precip_main/tree/main/model_performance) while monthly resolution data were used in to produce maps of the contiguous US [(variable_mapping)](https://github.com/syd-smith/GCM_precip_main/tree/main/variable_mapping). It is recommended that the repective temporal resolutions are used as outlined above to prevent an errors from occuring. However, favoring daily resolution data is recommended to prevent downloading dulicate datasets. See tables below for guidelines on 
**Monthly Data**


### Downscaled Data - MACAv2





