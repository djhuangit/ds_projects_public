# Assessing model fairness in mortgage approval using What-If Tool (Data analytics, model bias)
## Disclaimer
### This is a project extended from Qwiklabs [GSP709](https://www.qwiklabs.com/focuses/10903?parent=catalog#)
- In the original exercise, model needs to be deployed to Could AI Platform on GCP before linking up with What-If Tool
- In this version, What-If Tool is linked up with a local model using custom prediction function 

### Data source: 
- Original Data source: https://www.ffiec.gov/hmda/hmdaflat.htm
- Use a small subset of the data since the original dataset is big (gs://mortgage_dataset_files/mortgage-small.csv)

## Project Description
-	Train an XGBoost classifier with publicly available mortgage data
-	Pass test data and custom prediction function to link up the model with What-If Tool
-	Assessing the influencing factors in mortgage approval such as purpose of loan, county, population
-	Model predicts “approved” more often when: loan for home purchases, higher population area
-	Demographic parity is achievable by adjusting the threshold for approval

## Details
1. Using Performance & Fairness tab, the model is more likely to approve mortgage for home purchase loans 
    * approval rate of 78.4% (home purchase) vs 56.9% (other purposes)
![image1](https://github.com/djhuangit/ds_projects_public/raw/master/Model%20fairness%20using%20What-If%20Tool/images/1_home_purchase_loan.png)


2. Using Datapoint editor tab, binning (either X or Y-Axis) by county_code using 2 bins (named count in this tab), it was shown that most of the loan applications were from certain counties
![image2](https://github.com/djhuangit/ds_projects_public/raw/master/Model%20fairness%20using%20What-If%20Tool/images/2_county_code_datapoint.png)

    * Using Performance & Fairness tab and slicing the data by county_code with 2 buckets, the model’s approval rate is higher for the second bin (75% > 68.8%) when using Single threshold (which is a single threshold optimized for all datapoints based on the specified cost ratio). It is probably due to less data in the second bin in the train set that causes model underfitting.
![image3](https://github.com/djhuangit/ds_projects_public/raw/master/Model%20fairness%20using%20What-If%20Tool/images/2_county_code_performance%20and%20fairness.png)


3. Using Performance & Fairness tab and slicing by population, applicants from areas with higher population are more likely to get approved (81.8% > 68.7%). The reason could be similar to what happened to county_code: less data are present for area with lower population, thus model may overfit. In this case, the model is more conservative in mortgage approval for applicants from areas of lower population as compared to those from areas of higher population.
![image4](https://github.com/djhuangit/ds_projects_public/raw/master/Model%20fairness%20using%20What-If%20Tool/images/3_population.png)
