import math
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

# Fungsi simulasi gerak jatuh bebas tanpa hambatan udara
def simulasi_jatuh_bebas(massa, tinggi, gravitasi, langkah_waktu=0.01):
    waktu = []
    posisi = []
    kecepatan = []

    # Waktu total yang dibutuhkan agar benda mencapai tanah
    waktu_total = math.sqrt(2 * tinggi / gravitasi)

    t = 0
    while t <= waktu_total:
        waktu.append(t)
        kecepatan.append(gravitasi * t)
        posisi.append(tinggi - 0.5 * gravitasi * t**2) 
        t += langkah_waktu

    return waktu, posisi, kecepatan

def simulasi_jatuh_bebas_dengan_hambatan(massa, tinggi_awal, gravitasi, rho, A, Cd, langkah_waktu=0.01):
    # Koefisien hambatan udara
    k = 0.5 * rho * A * Cd

    waktu = []
    posisi = []
    kecepatan = []

    # Waktu total 
    t_max = (massa / gravitasi * k) ** 0.5 * np.acosh(np.exp((tinggi_awal * k) / massa))

    # Konstanta digunakan
    sqrt_gk_m = math.sqrt((gravitasi * k) / massa)
    v_terminal = math.sqrt((massa * gravitasi) / k)

    t = 0
    x_t = tinggi_awal

    while t <= t_max:
        # Kecepatan pada waktu t dengan hambatan udara
        v_t = v_terminal * np.tanh(sqrt_gk_m * t)
        kecepatan.append(v_t)

        # Posisi pada waktu t dengan hambatan udara
        x_t = tinggi_awal - (massa / k) * np.log(np.cosh(sqrt_gk_m * t))

        # Cegah posisi negatif
        if x_t < 0:
            x_t = 0

        posisi.append(x_t)
        waktu.append(t)

        # Hentikan simulasi jika posisi mencapai nol
        if x_t == 0:
            break

        t += langkah_waktu

    return waktu, posisi, kecepatan


# Fungsi menyimpan data ke file
def simpan_data(nama_file, data):
    with open(nama_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Waktu (s)", "Tinggi (m)", "Kecepatan (m/s)"])
        for row in data:
            writer.writerow([f"{row[0]:.2f}", f"{row[1]:.2f}", f"{row[2]:.2f}"])

# Menu utama
def menu_utama():
    layout = [
        [sg.Text("Simulasi Gerak Jatuh Bebas")],
        [sg.Button("Tanpa Hambatan Udara")],
        [sg.Button("Dengan Hambatan Udara")],
        [sg.Button("Keluar")],
    ]
    return sg.Window("Simulasi Gerak Jatuh Bebas", layout)

# Menu simulasi tanpa hambatan udara
def menu_simulasi():
    layout = [
        [sg.Text("Masukkan Parameter Simulasi")],
        [sg.Text("Massa Benda (kg):"), sg.InputText(key="-MASSA-")],
        [sg.Text("Tinggi Awal (m):"), sg.InputText(key="-TINGGI-")],
        [sg.Text("Gravitasi (m/s^2):"), sg.InputText("9.8", key="-GRAVITASI-")],
        [sg.Button("Jalankan Simulasi"), sg.Button("Kembali")],
    ]
    return sg.Window("Simulasi Parameter", layout)

# Menu simulasi dengan hambatan udara
def menu_simulasi_hambatan():
    layout = [
        [sg.Text("Masukkan Parameter Simulasi dengan Hambatan Udara")],
        [sg.Text("Massa Benda (kg):"), sg.InputText(key="-MASSA-")],
        [sg.Text("Tinggi Awal (m):"), sg.InputText(key="-TINGGI-")],
        [sg.Text("Gravitasi (m/s^2):"), sg.InputText("9.8", key="-GRAVITASI-")],
        [sg.Text("Densitas Udara (kg/m^3):"), sg.InputText("1.225", key="-RHO-")],
        [sg.Text("Luas Penampang (m^2):"), sg.InputText("0.01", key="-A-")],
        [sg.Text("Koefisien Hambatan (Cd):"), sg.InputText("0.47", key="-CD-")],
        [sg.Button("Jalankan Simulasi"), sg.Button("Kembali")],
    ]
    return sg.Window("Simulasi Parameter dengan Hambatan Udara", layout)

# Loop menu utama
window_main = menu_utama()

while True:
    event, values = window_main.read()
    if event in (sg.WINDOW_CLOSED, "Keluar"):
        break

    if event == "Tanpa Hambatan Udara":
        window_main.hide()
        window_simulasi = menu_simulasi()

        while True:
            event_sim, values_sim = window_simulasi.read()
            if event_sim in (sg.WINDOW_CLOSED, "Kembali"):
                window_simulasi.close()
                window_main.un_hide()
                break

            if event_sim == "Jalankan Simulasi":
                try:
                    # input data
                    massa = float(values_sim["-MASSA-"])
                    tinggi_awal = float(values_sim["-TINGGI-"])
                    gravitasi = float(values_sim["-GRAVITASI-"])

                    if massa <= 0 or tinggi_awal <= 0 or gravitasi <= 0:
                        raise ValueError("Nilai massa, tinggi, dan gravitasi harus positif.")

                    # Simulasi menggunakan rumus jatuh bebas tanpa hambatan udara
                    waktu, posisi, kecepatan = simulasi_jatuh_bebas(
                        massa, tinggi_awal, gravitasi
                    )

                    # menampilkan animasi
                    fig, ax = plt.subplots()
                    ax.set_xlim(0, max(waktu))
                    ax.set_ylim(0, tinggi_awal)
                    ax.set_title("Simulasi Gerak Jatuh Bebas")
                    ax.set_xlabel("Waktu (detik)")
                    ax.set_ylabel("Tinggi (meter)")
                    line, = ax.plot([], [], lw=2)

                    def update(frame):
                        # Menghentikan animasi ketika posisi mencapai atau sangat mendekati 0
                        if posisi[frame] <= 0.01 or kecepatan[frame] <= 0.01:
                            return line,  # Animasi berhenti
                        line.set_data(waktu[:frame], posisi[:frame])
                        return line,

                    ani = FuncAnimation(fig, update, frames=len(waktu), interval=50, blit=True)
                    plt.show()

                    # Simpan data
                    data = list(zip(waktu, posisi, kecepatan))
                    simpan_data("simulasi_data.csv", data)
                    sg.popup("Data berhasil disimpan ke 'simulasi_data.csv'!", title="Sukses")

                    # Menutup program 
                    window_simulasi.close()
                    window_main.close()
                    break

                except ValueError as e:
                    sg.popup(f"Error: {e}", title="Input Tidak Valid")

    elif event == "Dengan Hambatan Udara":
        window_main.hide()
        window_simulasi_hambatan = menu_simulasi_hambatan()

        while True:
            event_sim_hambatan, values_sim_hambatan = window_simulasi_hambatan.read()
            if event_sim_hambatan in (sg.WINDOW_CLOSED, "Kembali"):
                window_simulasi_hambatan.close()
                window_main.un_hide()
                break

            if event_sim_hambatan == "Jalankan Simulasi":
                try:
                    # input data
                    massa = float(values_sim_hambatan["-MASSA-"])
                    tinggi_awal = float(values_sim_hambatan["-TINGGI-"])
                    gravitasi = float(values_sim_hambatan["-GRAVITASI-"])
                    rho = float(values_sim_hambatan["-RHO-"])
                    A = float(values_sim_hambatan["-A-"])
                    Cd = float(values_sim_hambatan["-CD-"])

                    if massa <= 0 or tinggi_awal <= 0 or gravitasi <= 0 or rho <= 0 or A <= 0 or Cd <= 0 :
                        raise ValueError("Nilai harus positif.")

                    # Simulasi dengan hambatan udara
                    waktu, posisi, kecepatan = simulasi_jatuh_bebas_dengan_hambatan(
                        massa, tinggi_awal, gravitasi, rho, A, Cd
                    )

                    # Menampilkan animasi
                    fig, ax = plt.subplots()
                    ax.set_xlim(0, max(waktu))
                    ax.set_ylim(0, tinggi_awal)
                    ax.set_title("Simulasi Gerak Jatuh Bebas dengan Hambatan Udara")
                    ax.set_xlabel("Waktu (detik)")
                    ax.set_ylabel("Tinggi (meter)")
                    line, = ax.plot([], [], lw=2)

                    def update(frame):
                        # Menghentikan animasi ketika posisi mencapai atau sangat mendekati 0
                        if posisi[frame] <= 0.01 or kecepatan[frame] <= 0.01:
                            return line,  # Animasi berhenti
                        line.set_data(waktu[:frame], posisi[:frame])
                        return line,

                    ani = FuncAnimation(fig, update, frames=len(waktu), interval=50, blit=True)
                    plt.show()

                    # Simpan data
                    data = list(zip(waktu, posisi, kecepatan))
                    simpan_data("simulasi_data_dengan_hambatan.csv", data)
                    sg.popup("Data berhasil disimpan ke 'simulasi_data_dengan_hambatan.csv'!", title="Sukses")

                    # Menutup program
                    window_simulasi_hambatan.close()
                    window_main.close()
                    break

                except ValueError as e:
                    sg.popup(f"Error: {e}", title="Input Tidak Valid")

window_main.close()
