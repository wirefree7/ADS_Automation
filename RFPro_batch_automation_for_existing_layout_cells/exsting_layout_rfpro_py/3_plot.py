import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HOME = r"C:\Engineering\Script\Read_Cell_name\Existing_layout_EM"  ####Set Home directory for workspaces
wrk_name = "Read_Cell_Name_wrk"  #### Set Workspace name


def read_s2p_file(file_path):
    freqs, s11, s21, s12, s22 = [], [], [], [], []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('!') or line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) >= 9:
                freqs.append(float(parts[0]))
                s11.append(complex(float(parts[1]), float(parts[2])))
                s21.append(complex(float(parts[3]), float(parts[4])))
                s12.append(complex(float(parts[5]), float(parts[6])))
                s22.append(complex(float(parts[7]), float(parts[8])))
    return np.array(freqs), s11, s21, s12, s22

def plot_s_parameters(freqs, s11, s21, s12, s22, title):
    plt.figure(figsize=(10, 6))
    plt.plot(freqs, 20 * np.log10(np.abs(s11)), label='|S11| (dB)')
    plt.plot(freqs, 20 * np.log10(np.abs(s21)), label='|S21| (dB)')
    plt.plot(freqs, 20 * np.log10(np.abs(s12)), label='|S12| (dB)')
    plt.plot(freqs, 20 * np.log10(np.abs(s22)), label='|S22| (dB)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.ylim(bottom=-100)  # y-axis limitation
    plt.tight_layout()

def generate_pdf_report(workspace_path):
    data_folder = os.path.join(workspace_path, 'data')
    os.makedirs(data_folder, exist_ok=True)

    s2p_files = glob.glob(os.path.join(data_folder, 'RFPro_result_*.s2p'))
    if not s2p_files:
        print("No .s2p files found.")
        return

    pdf_path = os.path.join(workspace_path, 'RFPro_S_Parameter_Report.pdf')
    with PdfPages(pdf_path) as pdf:
        for s2p_file in s2p_files:
            title = os.path.basename(s2p_file).replace('.s2p', '')
            freqs, s11, s21, s12, s22 = read_s2p_file(s2p_file)
            plot_s_parameters(freqs, s11, s21, s12, s22, title)
            pdf.savefig()
            plt.close()

    print(f"PDF report generated: {pdf_path}")

# Example usage
workspace_path = os.path.join(HOME, wrk_name)
generate_pdf_report(workspace_path)