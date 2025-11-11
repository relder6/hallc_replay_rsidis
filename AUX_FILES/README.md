## Description of the files
1. `rsidis_runlist.dat` - List of R-SIDIS (part 1) runs with key parameters.
2. `rsidis_bigtable.csv` - Table of important analysis parameters for R-SIDIS (part 1) runs. The description of the coumns is as follows:

| Column Name               | Description                                                                    |
|---------------------------|--------------------------------------------------------------------------------|
| run                       | Run number                                                                     |
| ebeam                     | Beam energy from energy measurement (synchrotron corrected)                   |
| target                    | Target name                                                                    |
| hms_p                     | HMS central momentum                                                           |
| hms_th                    | HMS central angle (from camera)                                               |
| shms_p                    | SHMS central momentum                                                          |
| shms_th                   | SHMS central angle (from camera)                                              |
| run_type                  | Run type                                                                       |
| x                         | Central x_bjk                                                                  |
| Q2                        | Central Q2                                                                     |
| z                         | Central z                                                                      |
| thpq                      | Central theta_pq                                                               |
| BCM1_Q                   | BCM1 cut charge from the report file                                           |
| BCM1_I                   | BCM1 cut current from the report file                                          |
| BCM2_Q                   | BCM2 cut charge from the report file                                           |
| BCM2_I                   | BCM2 cut current from the report file                                          |
| BCM4A_Q                  | BCM4A cut charge from the report file                                          |
| BCM4A_I                  | BCM4A cut current from the report file                                         |
| BCM4B_Q                  | BCM4B cut charge from the report file                                          |
| BCM4B_I                  | BCM4B cut current from the report file                                         |
| BCM4C_Q                  | BCM4C cut charge from the report file                                          |
| BCM4C_I                  | BCM4C cut current from the report file                                         |
| h_esing_Eff              | HMS E SING FID TRACK EFFIC from the report file                               |
| h_hadron_Eff             | HMS HADRON SING FID TRACK EFFIC from the report file                          |
| p_esing_Eff              | SHMS E SING FID TRACK EFFIC from the report file                              |
| p_hadron_Eff             | SHMS HADRON SING FID TRACK EFFIC from the report file                         |
| ps1                       | Ps1_factor from the report file                                               |
| ps2                       | Ps2_factor from the report file                                               |
| ps3                       | Ps3_factor from the report file                                               |
| ps4                       | Ps4_factor from the report file                                               |
| ps5                       | Ps5_factor from the report file                                               |
| ps6                       | Ps6_factor from the report file                                               |
| comp_livetime             | Computer livetime calculated as (PS#*accepted_phys_triggers)/pTRIG# (for coin it just assumes =1) |
| electr_deadtime          | ROC2 Pre-scaled total live time (EDTM) (no BCM cut)                         |
| coin                      | e-Pi good coincidences from online monitoring script (ROC2)                   |
| randoms                   | e-Pi random coincidences from online monitoring script (ROC2)                 |
| ransubcoin               | e-Pi real coincidences from online monitoring script (ROC2)                   |
| normyield                | Normalized yield from "ransubcoin"                                            |
| normyield_err            | Statistical error on the "normyield"                                          |
| ctmean                   | e-Pi coin time mean from online monitoring script (ROC2)                      |
| ctsigma                  | e-Pi coin time std dev from online monitoring script (ROC2)                   |
| fan_mean                 | Average fan frequency from https://epicsweb.jlab.org/myquery/                 |
| fan_stdev                | Standard deviation from the average during the run from https://epicsweb.jlab.org/myquery/ |
| boil_corr		   | LD2: boiling correction, LH2: yield correction based on fan speed and beam currents       |
| IHWP                     | State of the insertable half-wave plate                                      |

## Contents of the directories:
1. `util/make_skimfiles` - Machinery to create skim files out of R-SIDIS hcana ROOT files.
2. `util/runlist_validation` - Machinery to verify the magnet currents and target types for each run in the R-SIDIS runlist against EPICS.
3. `util/parse_runlist` - Machinery to create a parsed CSV file out of rsidis_runlist.dat.
4. `util/make_bigtable` - Machinery to create rsidis_bigtable.csv.
