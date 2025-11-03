# app.py
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="N–T–M Diyagram Modülü", layout="wide")
st.title("N–T–M (Kesme–Moment) Diyagram Eğitim Modülü – Basit Kiriş")

# ---------------- UI ----------------
st.sidebar.header("Kiriş & Yükler")
L = st.sidebar.slider("Kiriş boyu L (m)", 1.0, 10.0, 6.0, 0.1)

load_type = st.sidebar.selectbox("Yük türü", ["Tekil Yük (P)", "Yayılı Yük (w)"])
if load_type == "Tekil Yük (P)":
    P = st.sidebar.slider("P (kN) ↓", 1.0, 50.0, 10.0, 0.5)
    a = st.sidebar.slider("Yük konumu a (m)", 0.0, float(L), float(L/2), 0.1)
    w = 0.0
else:
    w = st.sidebar.slider("w (kN/m) ↓", 0.5, 10.0, 2.0, 0.1)
    P, a = 0.0, 0.0

st.sidebar.caption("Mesnetler: Basit destekli (A ve B) varsayımı.")

# ---------------- Statics: reactions ----------------
# Basit kiriş: A ve B mafsal/rolik (düşey tepki RA, RB)
# Tekil yük P @ x=a  =>  RA = P*(L-a)/L , RB = P*a/L
# Yayılı yük w (uniform) => eşdeğer yük wL ortada: RA = RB = wL/2
if load_type == "Tekil Yük (P)":
    RA = P * (L - a) / L
    RB = P * a / L
else:
    RA = w * L / 2.0
    RB = w * L / 2.0

# ---------------- Shear/ moment along the beam ----------------
x = np.linspace(0, L, 801)  # yeterince sık
V = np.zeros_like(x)        # T(x)
M = np.zeros_like(x)        # M(x)

for i, xi in enumerate(x):
    # Kesme kuvveti: sol kesitte düşey kuvvetlerin toplamı
    v = RA
    if load_type == "Tekil Yük (P)" and xi >= a:
        v -= P
    if load_type == "Yayılı Yük (w)":
        v -= w * xi
    # Sağ mesnet tepki RB kesme diyagramında xi<L boyunca henüz "görünmez";
    # tüm uzunlukta sol kesit bakışı yapıyoruz. (RB etkisi xi=L'de sıçrama gibi görülür.)
    V[i] = v

    # Moment: sol kesitte momentlerin toplamı
    m = RA * xi
    if load_type == "Tekil Yük (P)" and xi >= a:
        m -= P * (xi - a)
    if load_type == "Yayılı Yük (w)":
        m -= w * xi * (xi / 2.0)
    M[i] = m

# ---------------- Display reactions ----------------
colA, colB, colC = st.columns(3)
with colA:
    st.metric("RA (kN)", f"{RA:.3f}")
with colB:
    st.metric("RB (kN)", f"{RB:.3f}")
with colC:
    st.metric("Kontrol (Düşey denge)", f"{RA+RB - (P if load_type=='Tekil Yük (P)' else w*L):+.3e} ≈ 0")

# ---------------- Plots ----------------
def plot_curve(x, y, title, ylabel):
    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=2)
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("x (m)")
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig, use_container_width=True)

st.subheader("Diyagramlar")
c1, c2 = st.columns(2)
with c1:
    plot_curve(x, V, "Kesme Kuvveti Diyagramı T(x)", "T (kN)")
with c2:
    plot_curve(x, M, "Eğilme Momenti Diyagramı M(x)", "M (kN·m)")

# ---------------- Probe: value at cursor-like slider ----------------
st.subheader("Kesitte değer oku")
xq = st.slider("x konumu (m)", 0.0, float(L), float(L/2), 0.01)
# En yakın indeksi al
idx = int(np.argmin(np.abs(x - xq)))
st.write(f"x = **{x[idx]:.2f} m** →  **T = {V[idx]:.3f} kN**,  **M = {M[idx]:.3f} kN·m**,  **N = 0**")

st.caption("Not: Bu basit prototipte N=0 varsayıldı ve destek modeli 'basit destekli'. Birden fazla yük, ankastre mesnet, eksene paralel yükler ve N(x) hesapları bir sonraki adımda eklenebilir.")
