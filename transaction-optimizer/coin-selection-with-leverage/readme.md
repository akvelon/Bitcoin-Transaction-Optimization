
## Coin Selection with Leverage Readme



This document walks through the contents of the folder "/coin-selection-with-leverage", explains the algorithms and shows how to run the simulations.

### Folder Contents

\coin-selection-with-leverage

    1. \data
      a. utxo_sample.csv: Sample of UTXO set taken on October 1st, 2019
      b. cc_data.csv: Transaction amounts from credit card data taken from the IEEE-CIS Kaggle Competition (URL: https://www.kaggle.com/c/ieee-fraud-detection)
      
    2. \scripts
        a. BTC_Utils.py: python script including some helper functions
        b. BTC_KnapFallBack: Implements Fallback solution
        c. BTC_KnapAlg: Implements standard Knapsack solution
        d. BTC_KnapLevAlg: Implements new Leverage solution
        e. BTC_Simulation: Combines 3 techniques and completes simulations
    3. \notebooks
        a. BTO LevSim.ipynb: Jupyter notebook to run simulations with Leverage full solution. Various parameters are avaialbe to tweak in notebook.
        b. BTO noLevSim.ipynb: Jupyter notebook to run simulations with no Leverage full solution. Various parameters are avaialbe to tweak in notebook.
    
    4. \simulation-results
        a. KnapsackSuccessRate_noLev.csv: csv file from showing success rate of standard knapsack algorithm. Used to compute the "leverage boost factor" used in leverage simulations.
        b. leverageResults_ccData_dynamicLbf.csv: csv file showing simulation results quoted in technical paper.
        c. noLeverageResults_ccData_dynamicLbf.csv: csv file showing simulation results quoted in technical paper.
        
        Future results will be saved here as .csv files.
    5. technical_paper.pdf
        Technical paper outlining full approach of new technique and simulation results.
    6. readme.md

### Overview of Techniques

Given a fixed collection of payment requests:

#### Fallback Solution
Use the fewest number of UTXOs neccessary to process payments. Starting from largest UTXO (in value) and adding next highest and so on. Usually creates a change output.

#### Knapsack Algorithm
Searchs UTXO pool for collection of UTXOs to use to avoid change. If it finds a solution which uses more input UTXOs than that of Fallback, algorithm is considered to have failed and the Fallback solution or Leverage solution is used.

#### Knapsack with Leverage
Used only after Knapsack algorithm fails. Creates two transactions at once, one to process current payments and another to process some to be determined payments from the pool. 

Designed to utilze the change output from first transaction as an input UTXO for the second so that second transaction is change-free.

### To Run Simulations

1. Install PuLP (https://pythonhosted.org/PuLP/)
2. Run either BTO LevSim.ipynb or BTO noLevSim.ipynb with parameters of your choosing and indicate where to save results. (Instructions in notebooks)
3. Alternative data sources for the UTXO and Payment Request pools can be used as well. Files can be pointed to and loaded in these notebooks for easy use in the simulations.

The various parameters found in the above python scripts have more in-depth description in the notebooks and scripts themselves as well as the technical paper.




```python

```
