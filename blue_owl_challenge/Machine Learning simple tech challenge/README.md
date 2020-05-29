# Machine learning challenge
========
* given train data, train classifier to make prediction on test data
* evaluation metric: AUC (>.825)
* given the data features, it looks like a credit assessment problem: given features of a customer, decide whether the loan should be approved or disapproved

========
# Git version control method used here

1. Using Jupytext: https://github.com/mwouts/jupytext
2. largely followed this guide: https://towardsdatascience.com/version-control-with-jupyter-notebooks-f096f4d7035a
3. .ipynb has been associated with .py (instead of .Rmd as shown in the guide above)
* in the tutorial where jupyter_notebook_config.py was modified, use thes lines instead:
'''
c.NotebookApp.contents_manager_class="jupytext.TextFileContentsManager"
c.ContentsManager.default_jupytext_formats = ".ipynb,.py"
'''
4. **for possible collaboration**, only use .py file for version control purpose.