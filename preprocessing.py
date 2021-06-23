"""
Author: Claudia Bigoni
Date: 23.06.2021
Description: Function used for electromyography (EMG) pre-processing.
"""

import numpy as np


def divide_in_epochs(input_signal, fs, t_time=1, t_min=-0.025, t_max=-0.05):
    """Divide the input_signal in epochs according to a trigger. They will be between tmin and tmax. Trigger is at
    t_time
    :param input_signal: MxN array, M samples, N trials
    :param fs: sampling frequency (Hz)
    :param t_time: time of trigger
    :param t_min: starting time of new epoch (related to trigger_t)
    :param t_max: ending time of new epoch (related to trigger_t)
    """
    samp_t_min = int((t_time + t_min)*fs)
    samp_t_max = int((t_time + t_max) * fs)
    epochs = input_signal[samp_t_min:samp_t_max]    # samples x trial

    return epochs


def correlation_bigger_than(input_signal_1, input_signal_2, thr=0.3):
    """Determine if the correlation between two signals is above a given threshold.
    :param input_signal_1: 1xN array, N=number of samples
    :param input_signal_2: 1xN array
    :param thr: threshold for correlation coefficient
    :return return_flag: boolean, True if correlation between signals is above thr
    """
    return_flag = False
    corr_val = np.corrcoef(input_signal_1, input_signal_2)[0, 1]
    if corr_val > thr:
        return_flag = True

    return return_flag


def half_signal_bigger_than(input_signal, thr=0):
    """Determine if more than half of the samples of input_signal have a power above a threshold
    :param input_signal: 1xN array, N=number of samples
    :param thr: threshold
    :return return_flag: boolean, True if at least half of the input signal is above the threshold
    """
    flag_remove = False
    samples_above_limit = input_signal[input_signal > thr]
    if len(samples_above_limit) < len(input_signal)/2:
        flag_remove = True

    return flag_remove


def bigger_than(num, thr=0):
    """Determine if number is above threshold
    :param num: float, or integer
    :param thr: threshold
    :return return_flag: boolean, True if num is bigger than thr"""
    return_flag = False
    if num > thr:
        return_flag = False

    return return_flag


def peak_to_peak_amplitude(input_signal):
    """Compute peak to peak amplitude in signal; i.e. max - min
    :param input_signal MxN array, M samples, N trials
    :return peak_to_peak float"""
    min_v = np.min(input_signal, axis=0)
    max_v = np.max(input_signal, axis=0)
    peak_to_peak = max_v - min_v

    return peak_to_peak
