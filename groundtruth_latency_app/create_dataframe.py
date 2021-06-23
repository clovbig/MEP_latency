"""
Author: Claudia Bigoni
Date: 29.01.2021
Description: This script created a dataframe containing MEP signals from different subjects. The dataframe is saved in a
.pkl file, readable by latency_gt.py.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

import preprocessing as pp


if __name__ == '__main__':
    data_dir = os.path.join(os.path.join("data"))
    fs = 5000  # sampling frequency, Hz

    df_meps = pd.DataFrame(columns=['sub_id', 'trial', 'mep'])  # initialize dataframe
    df_row_idx = 0

    subjects = sorted([i for i in os.listdir(os.path.join(data_dir)) if os.path.isdir(os.path.join(data_dir, i))])
    for sub_id in subjects:     # loop through subjects
        print(f'subject: {sub_id}')
        try:
            epochs_emg = np.load(os.path.join(data_dir, sub_id, 'EMG_data_SP.npy'))     # load data
        except OSError:
            continue

        # Pre-process EMG
        # mep data
        epochs_mep = pp.divide_in_epochs(epochs_emg, fs, 1, 0.01, 0.05)
        ptp = pp.peak_to_peak_amplitude(epochs_mep)
        remove_corr, remove_small_mep = [], []
        average_mep = np.mean(epochs_mep, axis=1)
        thr_ptp_value = np.percentile(ptp, 25)
        for idx_e, epoch in enumerate(epochs_mep.T):
            remove_corr.append(pp.correlation_bigger_than(epoch, average_mep))
            remove_small_mep.append(pp.bigger_than(ptp[idx_e], thr_ptp_value))
        idx_remove_corr = np.argwhere(np.asarray(remove_corr) == 0).flatten()
        idx_remove_small_mep = np.argwhere(np.asarray(remove_small_mep) == 0).flatten()

        # b. epoch for baseline emg and remove trials where half of the signal is above a threshold (related to power)
        epochs_baseline = pp.divide_in_epochs(epochs_emg, fs, 1, -0.025, -0.005)
        remove_baseline = []
        for epoch in epochs_baseline.T:
            epoch_power = abs(epoch)**2
            thr_power_baseline = np.percentile(epoch_power, 75) + 3 * stats.iqr(epoch_power)
            remove_baseline.append(pp.half_signal_bigger_than(abs(epoch), thr_power_baseline))
        idx_remove_baseline = np.argwhere(remove_baseline == 1).flatten()

        # 2. Remove trials containing artifacts in either mep or baseline emg
        idx_remove = set(list(idx_remove_baseline) + list(idx_remove_corr))
        num_trials = epochs_emg.shape[1]
        idx_keep = np.setdiff1d(range(0, num_trials), list(idx_remove))

        # Save data to dataframe
        epochs_mep = epochs_mep[:, idx_keep]
        for idx_e, epoch in enumerate(epochs_mep.T):
            df_meps.loc[df_row_idx] = pd.Series({'sub_id': sub_id, 'trial': idx_e, 'mep': [epoch]})
            df_row_idx += 1

    # Save dataframe
    df_meps.to_pickle(os.path.join(data_dir, 'df_meps.pkl'))
