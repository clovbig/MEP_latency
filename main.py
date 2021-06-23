"""
Author: Claudia Bigoni
Date: 23.06.2021
Description: Run comparison of automatic latency detectiton, with possible addition of comparison to ground truth (i.e.,
latencies manually detected using the software).
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

import preprocessing as pp
from epoch_c import Epoch

if __name__ == '__main__':
    data_dir = 'data'   # Insert here the path to your data folder
    fs = 5000   # EMG data sampling frequency in Hz

    df_gt = pd.read_csv('')[['sub_id', 'trial', 'lat']]     # path to the ground truth file
    # dataframe to save results
    df = pd.DataFrame(columns=['sub_id', 'trial', 'lat_bigoni', 'lat_hamada1', 'lat_hamada2', 'lat_huang', 'gt'])
    df_row = 0
    subjects = sorted([i for i in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, i))])
    for sub_id in subjects:
        print(f'subject: {sub_id}')
        try:
            epochs_emg = np.load(os.path.join(data_dir, sub_id, 'EMG_data_SP.npy'))
        except OSError:
            continue
        # Pre-process EMG (following methods of Hussain et al., 2019) - NB: this is the same preprocessing used to
        # create the dataframe for the ground truth application. This makes it easy to compare the ground truth
        # latencies with the ones automatically computed by the algorithm for the same trials
        epochs_mep = pp.divide_in_epochs(epochs_emg, fs, 1, 0.01, 0.05)     # Look for MEP in 10-50ms after tms pulse
        ptp = pp.peak_to_peak_amplitude(epochs_mep)     # Compute peak-to-peak amplitude
        # Trials automatic rejection based on (a) each MEP correlation with the average MEP signal for that subject and
        # (b) magnitude of MEP
        remove_corr, remove_small_mep = [], []
        average_mep = np.mean(epochs_mep, axis=1)
        thr_ptp_value = np.percentile(ptp, 25)
        for idx_e, epoch in enumerate(epochs_mep.T):
            remove_corr.append(pp.correlation_bigger_than(epoch, average_mep))
            remove_small_mep.append(pp.bigger_than(ptp[idx_e], thr_ptp_value))
        idx_remove_corr = np.argwhere(np.asarray(remove_corr) == 0).flatten()
        idx_remove_small_mep = np.argwhere(np.asarray(remove_small_mep) == 0).flatten()

        # b. Trials are removed based on baseline (i.e., 25 ms before the pulse) and remove trials where at least half of
        # the baseline power is above a threshold (Hussain et al., 2019)
        epochs_baseline = pp.divide_in_epochs(epochs_emg, fs, 1, -0.025, -0.005)    # Divide in epochs
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

        # Keep only good trials
        epochs_baseline = epochs_baseline[:, idx_keep]
        epochs_mep = epochs_mep[:, idx_keep]
        epochs_emg = epochs_emg[:, idx_keep]
        ptp = ptp[idx_keep]

        # go through trials and compute latency
        baseline_hamada = pp.divide_in_epochs(epochs_emg, fs, 1, -0.2, -0.02)
        for idx_e, mep in enumerate(epochs_mep.T):
            epoch = Epoch(mep, epochs_emg[:, idx_e], fs, 1)
            latency_bigoni = epoch.latency_bigoni_method()
            latency_hamada1 = epoch.latency_method_hamada_1(baseline_hamada)
            latency_hamada2 = epoch.latency_method_hamada_2()
            latency_huang = epoch.latency_method_huang()

            # Ground truth data
            latency_gt = (df_gt[((df_gt['sub_id'] == sub_id) & (df_gt['trial'] == idx_e))]['lat']).values[0]

            # Save results to dataframe
            df.loc[df_row] = pd.Series({'sub_id': sub_id, 'trial': idx_e, 'lat_bigoni': latency_bigoni,
                                        'lat_hamada1': latency_hamada1, 'lat_hamada2': latency_hamada2,
                                        'lat_huang': latency_huang, 'gt': latency_gt})
            df_row += 1

    # Check out some qualitative comparisons
    print(f'Difference (samples) between gt and Bigoni method: '
          f'\n\tmean: {np.mean(abs(df["gt"].values - df["lat_bigoni"].values))}'
          f'\n\tmean std: {np.std(abs(df["gt"].values - df["lat_bigoni"].values))}')
    print(f'Difference (samples) between gt and Huang method: '
          f'\n\tmean: {np.mean(abs(df["gt"].values - df["lat_huang"].values))}'
          f'\n\tmean std: {np.std(abs(df["gt"].values - df["lat_huang"].values))}')
    print(f'Difference (samples) between gt and Hamada1 method: '
          f'\n\tmean: {np.mean(abs(df["gt"].values - df["lat_hamada1"].values))}'
          f'\n\tmean std: {np.std(abs(df["gt"].values - df["lat_hamada1"]))}')
    print(f'Difference (samples) between gt and Hamada2 method: '
          f'\n\tmean: {np.mean(abs(df["gt"].values - df["lat_hamada2"].values))}'
          f'\n\tmean std: {np.std(abs(df["gt"].values - df["lat_hamada2"].values))}')
