#! /bin/bash

# Which spectrometer are we analyzing.
spec=${0##*_}
spec=${spec%%.sh}
SPEC=$(echo "$spec" | tr '[:lower:]' '[:upper:]')

# What is the last run number for the spectrometer.
# The pre-fix zero must be stripped because ROOT is ... well ROOT
#lastRun=$( \
#    ls raw/"${spec}"_all_*.dat raw/../raw.copiedtotape/"${spec}"_all_*.dat -R 2>/dev/null | perl -ne 'if(/0*(\d+)/) {prin#t "$1\n"}' | sort -n | tail -1 \
#)
lastRun=$( \
    ls raw/rsidis_production_*.dat.0 raw/../raw.copiedtotape/rsidis_production_*.dat.0 cache/rsidis_production_*.dat.0 -R 2>/dev/null | perl -ne 'if(/0*(\d+)/) {print "$1\n"}' | sort -n | tail -1 \
)

# If no arguments are given, prompt the user for all three
if [ $# -ne 3 ]; then
  read -p "Enter run number (default last run): " runNum
  if [ -z "$runNum" ]; then
    runNum=$lastRun
  fi    
  read -p "Enter number of events (default 50000): " numEvents
  if [ -z "$numEvents" ]; then
    numEvents=50000
  fi
  read -p "Enter desired number of good coin events (default 100000): " numCoin
  if [ -z "$numCoin" ]; then
    numCoin=100000
  fi
else
  # 1st argument: run number
  runNum=$1

  # 2nd argument: number of events
  numEvents=$2

  # 3rd argument: max events
  numCoin=$3
fi

# Which scripts to run.
script="SCRIPTS/${SPEC}/PRODUCTION/replay_production_${spec}_hElec_pProt.C"
analysis="get_good_coin_ev.C"
config="CONFIG/${SPEC}/PRODUCTION/${spec}_production_rsidis.cfg"
confighms="CONFIG/${SPEC}/PRODUCTION/${spec}_production_rsidis_hms.cfg"
configshms="CONFIG/${SPEC}/PRODUCTION/${spec}_production_rsidis_shms.cfg"
#expertConfig="CONFIG/${SPEC}/PRODUCTION/${spec}_production_rsidis.cfg" 

#Define some useful directories
rootFileDir="./ROOTfiles"
goldenDir="../ROOTfiles"
goldenFile="${goldenDir}/${spec}_replay_production_golden.root"
monRootDir="./HISTOGRAMS/${SPEC}/ROOT"
monPdfDir="./HISTOGRAMS/${SPEC}/PDF"
reportFileDir="./REPORT_OUTPUT/${SPEC}/PRODUCTION"
reportMonDir="./UTIL_OL/REP_MON" 
reportMonOutDir="./MON_OUTPUT/REPORT" 

# Name of the report monitoring file
reportMonFile="reportMonitor_${spec}_${runNum}_${numEvents}.txt" 

# Which commands to run.
runHcana="hcana -q \"${script}(${runNum}, ${numEvents})\""
runAnalysis="hcana -l -b -q \"${analysis}(${runNum},${numEvents},${numCoin},\\\"${rootFileDir}\\\",\\\"${reportFileDir}\\\",\\\"${monPdfDir}\\\")\""
runOnlineGUI="panguin -f ${config} -r ${runNum} -G ${goldenFile}"
saveOnlineGUI="panguin -f ${config} -r ${runNum} -P -G ${goldenFile}"
runOnlineGUIhms="panguin -f ${confighms} -r ${runNum} -G ${goldenFile}"
saveOnlineGUIhms="panguin -f ${confighms} -r ${runNum} -P -G ${goldenFile}"
runOnlineGUIshms="panguin -f ${configshms} -r ${runNum} -G ${goldenFile}"
saveOnlineGUIshms="panguin -f ${configshms} -r ${runNum} -P -G ${goldenFile}"
#saveExpertOnlineGUI="panguin -f ${expertConfig} -r ${runNum} -P"
runReportMon="./${reportMonDir}/reportSummary.py ${runNum} ${numEvents} ${spec}"
openReportMon="emacs ${reportMonOutDir}/${reportMonFile}"  

# Name of the replay ROOT file
replayFile="${spec}_replay_production_${runNum}"
rootFile="${replayFile}_${numEvents}.root"
latestRootFile="${rootFileDir}/${replayFile}_latest.root"

# Names of the monitoring file
monRootFile="${spec}_coin_production_${runNum}.root"
monPdfFile="${spec}_coin_production_${runNum}.pdf"
monExpertPdfFile="${spec}_coin_production_expert_${runNum}.pdf"
latestMonRootFile="${monRootDir}/${spec}_coin_production_latest.root"
latestMonPdfFile="${monPdfDir}/${spec}_production_latest.pdf"
latestMonPdfFilehms="${monPdfDir}/${spec}_production_hms_latest.pdf"
latestMonPdfFileshms="${monPdfDir}/${spec}_production_shms_latest.pdf"

# Where to put log.
reportFile="${reportFileDir}/replay_${spec}_production_${runNum}_${numEvents}.report"
summaryFile="${reportFileDir}/summary_production_${runNum}_${numEvents}.report"

# What is base name of onlineGUI output.
outFile="${spec}_production_${runNum}"
outExpertFile="summaryPlots_${runNum}_${spec}_production_rsidis"
outExpertFilehms="summaryPlots_${runNum}_${spec}_production_rsidis_hms"
outExpertFileshms="summaryPlots_${runNum}_${spec}_production_rsidis_shms"
outFileMonitor="output.txt"

# Replay out files
replayReport="${reportFileDir}/replayReport_${spec}_production_${runNum}_${numEvents}.txt"

# Start analysis and monitoring plots.
{
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  echo "" 
  date
  echo ""
  echo "Running ${SPEC} COIN analysis on the run ${runNum}:"
  echo " -> SCRIPT:  ${script}"
  echo " -> RUN:     ${runNum}"
  echo " -> NEVENTS: ${numEvents}"
  echo " -> COMMAND: ${runHcana}"
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="

  sleep 2
  eval ${runHcana}

  echo "" 
  echo ""
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  echo ""
  echo "Calculating number of randoms subtracted good coincidence events"
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="

  sleep 2
  eval ${runAnalysis}

  # Link the ROOT file to latest for online monitoring
  ln -fs ${rootFile} ${latestRootFile}  
  
  echo "" 
  echo ""
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  echo ""
  echo "Running onlineGUI for analyzed HMS COIN run ${runNum}:"
  echo " -> CONFIG:  ${confighms}"
  echo " -> RUN:     ${runNum}"
  echo " -> COMMAND: ${runOnlineGUI}"
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="

  sleep 2
  cd onlineGUI

  eval ${runOnlineGUIhms}
  eval ${saveOnlineGUIhms}
  mv "${outExpertFilehms}.pdf" "../HISTOGRAMS/${SPEC}/PDF/${outExpertFilehms}.pdf"

  echo "" 
  echo ""
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  echo ""
  echo "Running onlineGUI for analyzed SHMS COIN run ${runNum}:"
  echo " -> CONFIG:  ${configshms}"
  echo " -> RUN:     ${runNum}"
  echo " -> COMMAND: ${runOnlineGUIshms}"
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  
  eval ${runOnlineGUIshms}
  eval ${saveOnlineGUIshms}
  mv "${outExpertFileshms}.pdf" "../HISTOGRAMS/${SPEC}/PDF/${outExpertFileshms}.pdf"

  echo "" 
  echo ""
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  echo ""
  echo "Running onlineGUI for analyzed COIN run ${runNum}:"
  echo " -> CONFIG:  ${config}"
  echo " -> RUN:     ${runNum}"
  echo " -> COMMAND: ${runOnlineGUI}"
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="  
  eval ${runOnlineGUI}
  eval ${saveExpertOnlineGUI}
  mv "${outExpertFile}.pdf" "../HISTOGRAMS/${SPEC}/PDF/${outExpertFile}.pdf"
  cd ..
  ln -fs ${outExpertFilehms}.pdf ${latestMonPdfFilehms}
  ln -fs ${outExpertFileshms}.pdf ${latestMonPdfFileshms}  
  ln -fs ${outExpertFile}.pdf ${latestMonPdfFile}

  echo "" 
  echo ""
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  echo ""
  echo "Done analyzing ${SPEC} run ${runNum}."
  echo ""
  echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="

  # sleep 2

  # echo ""
  # echo ""
  # echo ""
  # echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:="
  # echo ""
  # echo "Generating report file monitoring data file ${SPEC} run ${runNum}."   
  # echo "" 
  # echo ":=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=:=" 


  # eval ${runReportMon}  
  # mv "${outFileMonitor}" "${reportMonOutDir}/${reportMonFile}" 
  # eval ${openReportMon}   

  # sleep 2
                                                                                        
  echo ""                                                                                                                                                                           
  echo ""                                                                                                                                                                                   
  echo ""                                                                                                                                            
  echo "-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|"                           
  echo ""                                                   
  echo "So long and thanks for all the fish!"                                             
  echo ""          
  echo "-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|"                                               
  echo ""                                                                                                                                                
  echo ""                                                                                    
  echo ""                         

} 2>&1 | tee "${replayReport}"
echo ""
echo "Launching FID tracking efficiency plot..."
python3 plot_effic.py "${reportFile}"
