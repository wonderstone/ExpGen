import numpy as np
from scipy import stats

# Information Coefficient (IC) and Rank Information Coefficient (RIC)
# are two common metrics used to evaluate the performance of a predictive model.
# IC measures the linear correlation between predicted and actual returns,
# while RIC measures the rank correlation between predicted and actual returns.
# However, the implementation of these indicators are different.
# Some may even deverge from the standard definition, check following 
# https://www.investopedia.com/terms/i/information-coefficient.asp


## 1. IC and RIC fundemental functions
def calculate_ic(predicted_returns, actual_returns):
    """Calculate Information Coefficient"""
    return np.corrcoef(predicted_returns, actual_returns)[0, 1]

def calculate_ric(predicted_returns, actual_returns):
    """Calculate Rank Information Coefficient"""
    return stats.spearmanr(predicted_returns, actual_returns)[0]

def calculate_ic_manual(predicted_returns, actual_returns):
    """
    Calculate Information Coefficient (Pearson correlation)
    
    Args:
    predicted_returns (np.array): Array of predicted returns
    actual_returns (np.array): Array of actual returns
    
    Returns:
    float: Information Coefficient
    """
    n = len(predicted_returns)
    
    # Calculate means
    pred_mean = np.mean(predicted_returns)
    actual_mean = np.mean(actual_returns)
    
    # Calculate covariance
    covariance = np.sum((predicted_returns - pred_mean) * (actual_returns - actual_mean)) / n
    
    # Calculate standard deviations
    pred_std = np.sqrt(np.sum((predicted_returns - pred_mean)**2) / n)
    actual_std = np.sqrt(np.sum((actual_returns - actual_mean)**2) / n)
    
    # Calculate correlation (IC)
    ic = covariance / (pred_std * actual_std)
    
    return ic

def calculate_ric_manual(predicted_returns, actual_returns):
    """
    Calculate Rank Information Coefficient (Spearman's rank correlation)
    
    Args:
    predicted_returns (np.array): Array of predicted returns
    actual_returns (np.array): Array of actual returns
    
    Returns:
    float: Rank Information Coefficient
    """
    n = len(predicted_returns)
    
    # Calculate ranks
    pred_ranks = np.argsort(np.argsort(predicted_returns))
    actual_ranks = np.argsort(np.argsort(actual_returns))
    
    # Calculate mean of ranks
    pred_rank_mean = np.mean(pred_ranks)
    actual_rank_mean = np.mean(actual_ranks)
    
    # Calculate covariance of ranks
    rank_cov = np.sum((pred_ranks - pred_rank_mean) * (actual_ranks - actual_rank_mean)) / n
    
    # Calculate standard deviations of ranks
    pred_rank_std = np.sqrt(np.sum((pred_ranks - pred_rank_mean)**2) / n)
    actual_rank_std = np.sqrt(np.sum((actual_ranks - actual_rank_mean)**2) / n)
    
    # Calculate rank correlation (RIC)
    ric = rank_cov / (pred_rank_std * actual_rank_std)
    
    return ric



if __name__ == "__main__":
    # Example usage
    predicted_returns = np.array([0.05, 0.02, 0.03, 0.01, 0.04])
    actual_returns = np.array([0.04, 0.01, 0.03, 0.02, 0.05])

    ic = calculate_ic(predicted_returns, actual_returns)
    ric = calculate_ric(predicted_returns, actual_returns)

    print(f"Information Coefficient: {ic:.4f}")
    print(f"Rank Information Coefficient: {ric:.4f}")


    icm = calculate_ic_manual(predicted_returns, actual_returns)
    ricm = calculate_ric_manual(predicted_returns, actual_returns)

    print(f"Information Coefficient: {icm:.4f}")
    print(f"Rank Information Coefficient: {ricm:.4f}")

    # output:
    # Information Coefficient: 0.8000
    # Rank Information Coefficient: 0.8000
    # Information Coefficient: 0.8000
    # Rank Information Coefficient: 0.8000
