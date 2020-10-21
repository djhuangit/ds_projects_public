# Assessing model fairness in mortgage approval using What-If Tool (Data analytics, model bias)
## Disclaimer
### This is a project extended from Qwiklabs [GSP709](https://www.qwiklabs.com/focuses/10903?parent=catalog#)
- In the original exercise, model needs to be deployed to Could AI Platform on GCP before linking up with What-If Tool
- In this version, What-If Tool is linked up with local model using custom prediction function 

### Data source: 
- Original Data source: https://www.ffiec.gov/hmda/hmdaflat.htm
- Use a small subset of the data since the original dataset is big (gs://mortgage_dataset_files/mortgage-small.csv)

## Project Description
-	Train an XGBoost classifier with publicly available mortgage data
-	Pass test data and custom prediction function to link up the model with What-If Tool
-	Assessing the influencing factors in mortgage approval such as purpose of loan, county, population
-	Model predicts “approved” more often when: loan for home purchases, lower population area
-	Demographic parity is achievable by adjusting the threshold for approval

