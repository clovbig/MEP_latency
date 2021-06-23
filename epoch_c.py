"""
Author: Claudia Bigoni
Date: 23.06.2021
Description: class Epoch to study MEP features (i.e., peak-to-peak amplitudes and latency)
"""
import numpy as np
import preprocessing as pp


class Epoch:
    def __init__(self, input_signal, input_signal_baseline, fs, trigger_sample):
        self.v = input_signal
        self.baseline = input_signal_baseline
        self.fs = fs
        self.trigger = trigger_sample

        self.ptp = self.peak_to_peak_amplitude()

    def peak_to_peak_amplitude(self):
        peak_to_peak = abs(np.max(self.v) - np.min(self.v))

        return peak_to_peak

    def latency_bigoni_method(self, min_len=4):
        # Latency is time point when signal starts to deflect (either up or down)
        # find positive an negative peaks (i.e., maximum and minimum of the signal)
        p_peak = np.argmax(self.v)
        n_peak = np.argmin(self.v)
        # If negative deflection is before positive one, flip the signal
        if p_peak > n_peak:
            self.v = -self.v
            p_peak = np.argmax(self.v)
            n_peak = np.argmin(self.v)
        # Compute first derivative over samples - look until the positive peak only 
        # The derivative is approximated as the difference between consecutive samples
        first_derv = np.diff(self.v[:p_peak])
        # Only interested in positive derivative
        idx_positive = np.argwhere(first_derv > 0).flatten()
        # Consider only consecutive samples where derivative is positive
        idx_positive_diff = np.where(np.diff(idx_positive) == 1)[0]
        idx_positive_diff_diff = np.where(np.diff(idx_positive_diff) == 1)[0]
        # Take all chunks of at least 2 consecutive samples having positive derivatives
        chunks = np.split(idx_positive_diff_diff,
                          (np.add(np.where(np.diff(idx_positive_diff_diff) > 1), 1)).tolist()[0])
        # Find the longest chunk in splits
        max_len = min_len
        for c in chunks:
            if len(c) > max_len:
                max_len = len(c)
                c_longest = c

        # latency is the beginning of the longest array of samples with positive derivatives
        try:
            latency = idx_positive[idx_positive_diff[c_longest[0]]]
        except NameError:
            latency = 'nan'
            print('Bigoni method - There is no long enough chunk of positive derivatives')
        except IndexError:
            latency = 'nan'
            print('Bigoni method - did not find the beginning of MEP')

        return latency

    def latency_method_hamada_1(self, baseline_signals):
        # Latency is time point at which rectified EMG signal exceeds an amplitude threshold defined as the average
        # 100 ms pre-stimulus EMG activity across all trials plus two SDs"""
        thr = np.mean(baseline_signals) + 2 * np.std(baseline_signals)
        try:
            latency = np.where(abs(self.v) > thr)[0][0]
        except IndexError:
            latency = 'nan'
            print('Hameda method 1 - did not find the beginning of MEP')

        return latency

    def latency_method_hamada_2(self):
        # Latency is time point at which rectified EMG signal exceeds an amplitude threshold defined as the average
        # 100 ms pre-stimulus EMG activity plus two SDs"""
        baseline_100 = pp.divide_in_epochs(self.baseline, self.fs, self.trigger, -0.1, -0.002)
        thr = np.mean(baseline_100) + 2 * np.std(baseline_100)
        try:
            latency = np.where(abs(self.v) > thr)[0][0]
        except IndexError:
            latency = 'nan'
            print('Hameda method 2 - did not find the beginning of MEP')

        return latency

    def latency_method_huang(self):
        # Latency is time point at which the EMG signal exceeds by more than 5 times the standard deviation the EMG
        # signal measured during the pre-stimulus interval (-200 to 0 ms before the onset of the TMS pulse)"""
        baseline_200 = pp.divide_in_epochs(self.baseline, self.fs, self.trigger, -0.2, -0.002)
        thr = 5 * np.std(baseline_200)
        try:
            latency = np.where(self.v > thr)[0][0]
        except IndexError:
            latency = 'nan'
            print('Huang method - did not find the beginning of MEP')

        return latency

    def garvey_revised(self):
        # Garvey et al., 2001 proposes a method for MEP onset during active contraction. This is considered based on the
        # mean consecutive difference (MCD), which describes the variation of the pre-stimulus EMG (i.e. 100ms before
        # pulse). Boundaries are EMG +- MCDx2.66. MEP onset is defined as "the first consecutive data points to fall
        # below the lower variation limit". Here we should also do above
        baseline_100 = np.abs(pp.divide_in_epochs(self.baseline, self.fs, self.trigger, -0.1, -0.002))
        mean_baseline = np.mean(baseline_100)
        mcd = np.mean(np.abs(np.diff(baseline_100)))
        thr_low = np.mean(baseline_100) - 2.66*mcd
        # thr_high = np.mean(baseline_100) + 2.66*mcd

        idx_low = np.where(self.v <= thr_low)[0]
        # idx_high = np.where(self.v >= thr_high)[0]

        chunks_low = np.split(idx_low, (np.add(np.where(np.diff(idx_low) > 4))))
        # chunks_high = np.split(idx_high, (np.add(np.where(np.diff(idx_high) > 4))))
        try:
            latency = chunks_low[0][0]
        except IndexError:
            latency = 'nan'
            print('Garvey method - did not find the beginning of MEP')

    def daskalakis(self):
        # The MEP onset was defined as the last crossing of the mean pre-stimulus EMG level before the point of maximum
        # deflection. Pre-stimulus window: 40ms
        baseline_40 = pp.divide_in_epochs(self.baseline, self.fs, self.trigger, -0.04, -0.002)
        thr = np.mean(baseline_40)
        p_peak = np.argmax(self.v)
        n_peak = np.argmin(self.v)
        # If negative deflection is before positive one, flip the signal
        if p_peak > n_peak:
            self.v = -self.v
            p_peak = np.argmax(self.v)
            n_peak = np.argmin(self.v)
        try:
            latency = np.where(self.v[:p_peak] > thr)[0][-1]
        except IndexError:
            latency = 'nan'
            print('Daskalakis method - did not find the beginning of MEP')

        return latency




