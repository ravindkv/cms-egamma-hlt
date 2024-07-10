* cmsrel CMSSW_13_3_0
* cd CMSSW_13_3_0/src/

* python condDB-diff-HCALRespCorr.py 

## Important command for conddb
### CONDDB USAGE
  * conddb --help
  * conddb list --h

### CONDDB: DB TARGET
  * conddb --db myfile.db
  * conddb --db pro
  * conddb --db dev

### CONDDB: SEARCH
  * conddb search RunInfo
  * conddb search CMSSW_8_0_X

### CONDDB: LISTING db CONTENT
  * conddb --db dev listTags
  * conddb listGTs
  * conddb listGTsForTag runinfo_31X_hlt
  * conddb --db test_output.db list fillinfo_test

### CONDDB: LISTING tAG/gt CONTENT
  * conddb --noLimit list runinfo_31X_hlt
  * conddb list runinfo_31X_hlt --limit 200
  * conddb list 80X_dataRun2_HLT_v0 --long

### CONDDB: DUMP
  * conddb dump d55a178a9e56ce9e33f3b2bbeda9fd836c46b5c5

### CONDDB: DIFF
  * conddb --db runinfo.db diff runinfo_1 runinfo_2 --long
  * conddb diff 76X_dataRun2_HLT_frozen_v11 80X_dataRun2_HLTHI_v0

### CONDDB: COPY/IMPORT
  * conddb [--db target]] copy [object1] [object2] [--destdb DB][--from S][--to E][--type T]
  * conddb_import -c destdb -f sourcedb -i inputTag -t destTag -b begin -e end
  * conddb_import -c sqlite:runinfo.db -f frontier://FrontierProd/CMS_CONDITIONS -i runinfo_31X_hlt -t runinfo_1 -b 268283 -e 268285

