import numpy as np
import scipy.signal as signal
from scipy.fftpack import fft, ifft
import json
import pandas as pd
import endaq as en
import matplotlib.pyplot as plt # For plotting
import sys


def passfilter(filter: str,data: np.ndarray, cutoff: list[float], sample_rate: float = 1000, order: int = 5):
    """
    Filter the data using a Butterworth filter.
    filter: 'lowpass', 'highpass', 'bandpass', or 'bandstop'
    data: the data to filter
    cutoff: the cutoff frequency or frequencies
    sample_rate: the sample rate of the data 
    order: the order of the filter
    """

    # if(cutoff[0]==-1):
    #     cutoff=cutoff[1]
    # elif(cutoff[1]==-1):
    #     cutoff=cutoff[0]

    sos = signal.butter(order, cutoff, filter, fs=sample_rate, output='sos')
    filtered_data = signal.sosfiltfilt(sos, data)

    return filtered_data


def plot_data(data: np.ndarray, sample_rate: float, title: str, xlabel: str, ylabel: str):
    """
    Plot the data.
    data: the data to plot
    sample_rate: the sample rate of the data
    title: the title of the plot
    xlabel: the x-axis label
    ylabel: the y-axis label
    """

    time = np.arange(0, len(data) / sample_rate, 1 / sample_rate)
    plt.plot(time, data)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def dump_json(signal_data: dict, file_path: str):
    """
    Dump the data to a json file.
    data: the data to dump
    file_path: the path of the file to dump the data to
    """
    with open(file_path, 'w') as f:
        json.dump(signal_data, f, indent=4)



def custom_FFT(x, fs=1.0, window='hann', nperseg=256, noverlap=None):
    """
    Compute the average magnitude of the FFT of a signal using Welch's method.
    Data vector: x
    Sampling frequency: fs
    Window function: window
    Number of samples per segment: nperseg
    Number of samples to overlap: noverlap (If not given it will be half of nperseg)

    Returns: f, avg_mag (frequency vector and average magnitude)
    """
    # Convert the input to a numpy array
    x = np.asarray(x)
    
    # # Define the overlap
    # if noverlap is None:
    #     noverlap = nperseg // 2
    # # Get the window function
    # # win = signal.get_window(window, nperseg)

    # #implemtnt hanning window
    # # Compute the Hanning window
    # win = np.hanning(nperseg)
    # win.shape = (nperseg, 1)
    # # # Compute the step size
    # # print(type(win))
    # step = nperseg - noverlap
    # # # Number of segments
    # n_segments = (len(x) - noverlap) // step
    # # # Frequency vector
    # f = np.fft.rfftfreq(nperseg, d=1/fs)
    # print(f)
    # # # Initialize array to accumulate magnitudes
    # avg_mag = np.zeros(len(f))
    
    # # # Loop over segments
    # for i in range(n_segments):
    # #     # Extract the segment.
    #     segment = x[i*step : i*step + nperseg]
    #     # segment = np.array(segment)
    # #     # Apply the window
    # #     print(type(segment))
    #     segment = np.asarray(segment) * win
        
    # #     # Compute the FFT of the segment
    #     fft_segment = np.fft.rfft(segment)
        
    # #     # Take the magnitude (not squared)
    #     magnitude = np.abs(fft_segment)
        
    # #     # Accumulate the magnitudes
    #     avg_mag += magnitude
    
    # # # Average the magnitudes
    # avg_mag /= n_segments

    #################################### Claude ####################################
    if noverlap is None:
        noverlap = nperseg // 2
    
    # Create the window
    win = signal.get_window(window, nperseg)
    
    # Normalize the window
    win = win / np.sum(win)
    
    # Calculate the number of segments
    nstep = nperseg - noverlap
    num_segments = (len(x) - noverlap) // nstep
    
    # Truncate x to fit an integer number of segments
    x = x[:num_segments*nstep + noverlap]
    
    # Reshape x to create overlapping segments
    segments = np.lib.stride_tricks.sliding_window_view(x, nperseg)[::nstep]
    
    # Apply window to each segment
    windowed = segments * win
    
    # Compute FFT for each windowed segment
    fft_segments = np.fft.rfft(windowed, axis=1)
    
    # Compute magnitude spectrum
    mag_spectrum = np.abs(fft_segments)
    
    # Average magnitude spectrum across segments
    avg_mag_spectrum = np.mean(mag_spectrum, axis=0)
    
    # Compute frequency array
    f = np.fft.rfftfreq(nperseg, d=1/fs)
    
    return f, avg_mag_spectrum


    #################################### ENDAQ ####################################



    # Compute the FFT using ENDAQ
    # df = en.DataFile(data=x, sample_rate=fs)
    # df = pd.DataFrame(x)

    # avg_mag= en.calc.fft.fft(df)
    # f = en.calc.fft.freq(df, nfft=None, sample_rate=fs)
    # avg_mag = avg_mag.to_numpy()


    # avg_mag = endaq.calc.fft.fft(df)

    # Calculate frequencies corresponding to FFT result
    # n = len(df)  # or the value of nfft if it's used
    # frequencies = np.fft.fftfreq(nperseg, d=1/fs)

    # Define the frequency range
    # f_min, f_max = 0,nperseg

    # Get the indices of frequencies in the desired range
    # valid_idx = np.where((frequencies >= f_min) & (frequencies <= f_max))
    # avg_mag=avg_mag.to_numpy()
    # Filter the FFT results and frequencies
    # filtered_frequencies = frequencies[valid_idx]
    # filtered_avg_mag = avg_mag[valid_idx]
    # f = f.to_numpy()
    # ans = en.calc.fft()
    
    # return f , avg_mag
    


def PSD(x, fs=1.0, window='hann', nperseg=None, noverlap=None, nfft=None, detrend='constant', return_onesided=True, scaling='density', axis=-1, average='mean'):
    """
    Compute the Power Spectral Density of a signal.
    Data vector: x
    Sampling frequency: fs
    Window function: window
    Number of samples per segment: nperseg
    Number of samples to overlap: noverlap
    Number of points for the FFT: nfft
    Detrend: detrend
    Return one-sided spectrum: return_onesided
    Scaling: scaling
    Axis: axis
    Average method: average

    Returns: f, Pxx (frequency vector and PSD)
    """

    return signal.welch(x, fs, window, nperseg, noverlap, nfft, detrend, return_onesided, scaling, axis, average)
    

def compute_acceleration_envelope(data, lowcut, highcut, fs, order=4):
    """
    Compute the acceleration envelope of a signal.
    data: the data to process
    lowcut: the low cutoff frequency
    highcut: the high cutoff frequency
    fs: the sample rate of the data
    order: the order of the filter

    Returns: envelope (the acceleration envelope)
    """

    # Step 1: Band-pass filter the data
    filtered_data = passfilter("bandpass",data, [lowcut, highcut], fs, order)
    
    # Step 2: Compute the Hilbert transform to get the analytic signal
    analytic_signal = signal.hilbert(filtered_data)
    
    # Step 3: Compute the envelope (magnitude of the analytic signal)
    envelope = np.abs(analytic_signal)
    
    return envelope


def compute_cepstrum(signal):
    # Step 1: Compute the Fourier Transform of the signal
    spectrum = custom_FFT(signal)
    
    # Step 2: Compute the log magnitude of the spectrum
    log_magnitude = np.log(np.abs(spectrum) + 1e-8)  # Adding small constant to avoid log(0)
    
    # Step 3: Compute the Inverse Fourier Transform of the log magnitude
    cepstrum = ifft(log_magnitude)
    
    # Compute the real part of cepstrum
    cepstrum = np.real(cepstrum)
    
    return cepstrum


# Example usage
if __name__ == "__main__":

    mode = sys.argv[1]
    if mode == "filter":
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        filter_type = sys.argv[4]
        order = int(sys.argv[5])
        cut_in = float(sys.argv[6])
        cut_out = float(sys.argv[7])
        sample_rate = float(sys.argv[8])

        df = pd.read_csv(input_file, delimiter='\t', header=None)
        # data = df
        print(df.shape)
        x = df[0].to_numpy()
        # Compute FFT
        # fs = 10000  # Sampling frequency: 1000 Hz
        # Create a figure for plotting all signals
        # List to store FFT results for each signal
        signal_data = {}
        # data = df[0].to_numpy()
        # f, _ = custom_FFT(data, fs=100, window='hann', nperseg=256, noverlap=128)
        # signal_data["frequencies"] = f.tolist()  # Save frequencies only once

        plt.figure(figsize=(10, 6))
        for i in range(df.shape[1]):
            data = df[i].to_numpy()

            # Apply the selected transformation based on user input
            if filter_type == 'lowpass':
                result = passfilter(filter=filter_type,data=data,cutoff=cut_in,order=order,sample_rate=sample_rate)
            elif filter_type == 'highpass':
                result = passfilter(filter=filter_type,data=data,cutoff=cut_out,order=order,sample_rate=sample_rate)
            elif filter_type == 'bandpass':
                result = passfilter(filter=filter_type,data=data,cutoff=cut_out,order=order,sample_rate=sample_rate)

            # Plot the magnitude spectrum
            # plt.plot(f, result, label=f'Signal {i+1}')
            # Add magnitude spectrum of each signal to the dictionary
            if i==0:
                signal_data[f"x_data"] = result.tolist()
            elif (i==1):
                signal_data[f"y_data"] = result.tolist()
            elif (i==2):
                signal_data[f"z_data"] = result.tolist()
                
        
        
        plt.title('Average Magnitude Spectrum of All Signals')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Magnitude')
        plt.grid(True)
        # Add a legend to differentiate between signals
        plt.legend()
        # Save the figure to a PNG file
        # plt.savefig('magnitude_spectrum.png', dpi=300)
        # plt.show()
        # Save the FFT results to a JSON file
        dump_json(signal_data, output_file)
        print(f"FFT results have been dumped to {output_file}")

    elif mode == "transform":
        input_file = sys.argv[2]  # First argument: input file path
        output_file = sys.argv[3]  # Second argument: output file path
        transform_type = sys.argv[4]  # Third argument: transform type (fft, psd, cepstrum, envelope)
        filter_size = int(sys.argv[5])  # Fourth argument: filter size (nperseg)
        window_type = sys.argv[6]  # Fifth argument: window type
        overlap = int(sys.argv[7]) if sys.argv[6].isdigit() else None  # Sixth argument: overlap

        # Generate a sample signal
        # t = np.linspace(0, 1, 1000, endpoint=False)
        # x = np.sin(2*np.pi*10*t) + 0.5*np.sin(2*np.pi*20*t)
        df = pd.read_csv(input_file, delimiter='\t', header=None)
        # data = df
        print(df.shape)
        x = df[0].to_numpy()
        # Compute FFT
        # fs = 10000  # Sampling frequency: 1000 Hz
        # Create a figure for plotting all signals
        # List to store FFT results for each signal
        signal_data = {}
        data = df[0].to_numpy()
        f, _ = custom_FFT(data, fs=100, window='hann', nperseg=256, noverlap=128)
        signal_data["frequencies"] = f.tolist()  # Save frequencies only once

        plt.figure(figsize=(10, 6))
        for i in range(df.shape[1]):
            data = df[i].to_numpy()

            # Apply the selected transformation based on user input
            if transform_type == 'fft':
                f, result = custom_FFT(data, fs=100, window=window_type, nperseg=filter_size, noverlap=overlap)
            elif transform_type == 'psd':
                f, result = PSD(data, fs=100, window=window_type, nperseg=filter_size, noverlap=overlap)
            elif transform_type == 'cepstrum':
                result = compute_cepstrum(data)
            elif transform_type == 'envelope':
                lowcut = 0.1  # Set defaults or pass additional params for bandpass envelope
                highcut = 50.0
                result = compute_acceleration_envelope(data, lowcut, highcut, fs=100)

            # Plot the magnitude spectrum
            # plt.plot(f, result, label=f'Signal {i+1}')
            # Add magnitude spectrum of each signal to the dictionary
            if i==0:
                signal_data[f"x_data"] = result.tolist()
            elif (i==1):
                signal_data[f"y_data"] = result.tolist()
            elif (i==2):
                signal_data[f"z_data"] = result.tolist()
                
        
        
        plt.title('Average Magnitude Spectrum of All Signals')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Magnitude')
        plt.grid(True)
        # Add a legend to differentiate between signals
        plt.legend()
        # Save the figure to a PNG file
        # plt.savefig('magnitude_spectrum.png', dpi=300)
        # plt.show()
        # Save the FFT results to a JSON file
        dump_json(signal_data, output_file)
        print(f"FFT results have been dumped to {output_file}")