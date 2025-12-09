# 🍓 Setup para Raspberry Pi

Guía específica para instalar y ejecutar el Performance Energy Mixer en Raspberry Pi (ARM).

## 📋 Hardware Recomendado

### Mínimo (Funcional)
- **Raspberry Pi 4** con 4GB RAM
- Tarjeta SD de 32GB (Clase 10)
- Fuente de alimentación oficial (5V 3A)
- Interfaz de audio USB (opcional pero recomendado)

### Recomendado (Óptimo)
- **Raspberry Pi 5** con 8GB RAM
- SSD USB para mejor rendimiento
- DAC USB o HAT de audio de calidad
- Ventilador o disipador activo

### Compatible pero limitado
- Raspberry Pi 3B+ (2-4 stems máximo)
- Raspberry Pi Zero 2W (solo 2 stems, sin time-stretch)

---

## 🚀 Instalación Rápida

### 1. Preparar Sistema

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar git si no está
sudo apt-get install -y git

# Clonar o copiar el proyecto
cd ~/
# (copiar archivos al Raspberry Pi)
```

### 2. Ejecutar Setup Automático

```bash
cd realtime-stems-mixer

# Dar permisos
chmod +x setup_venv_rpi.sh

# Ejecutar instalación (10-20 minutos)
./setup_venv_rpi.sh
```

El script instalará:
- ✅ Dependencias del sistema (portaudio, libsndfile)
- ✅ PyAudio desde apt (pre-compilado)
- ✅ Bibliotecas Python optimizadas para ARM
- ✅ Virtual environment

---

## ⚙️ Configuración Optimizada

El proyecto incluye [mixer_config_rpi.json](mixer_config_rpi.json) optimizado para Raspberry Pi:

```bash
# Usar configuración para RPI
cp mixer_config_rpi.json mixer_config.json
```

### Diferencias vs configuración estándar:

| Parámetro | Estándar | RPI | Razón |
|-----------|----------|-----|-------|
| **sample_rate** | 48000 | 22050 | Menos carga CPU |
| **chunk_size** | 512 | 1024 | Reduce latencia USB |
| **time_stretching** | true | false | Ahorro CPU crítico |
| **master_volume** | 0.8 | 0.7 | Prevenir distorsión |
| **hop_length** | 256 | 512 | Menos procesamiento |
| **low_latency_mode** | false | true | Optimización ARM |

---

## 🎵 Ejecutar Performance

```bash
# Activar environment
source venv/bin/activate

# Opción 1: Configuración optimizada para RPI
python performance_energy_mixer.py

# Opción 2: Con configuración específica
python performance_energy_mixer.py --config mixer_config_rpi.json
```

---

## 🐛 Solución de Problemas Específicos de RPI

### Error: PyAudio compilation failed

**Causa:** Falta portaudio en el sistema

**Solución:**
```bash
sudo apt-get install -y portaudio19-dev python3-pyaudio
sudo apt-get install -y libportaudio2 libasound2-dev
```

### Error: No module named 'numpy'

**Causa:** Instalación incompleta

**Solución:**
```bash
source venv/bin/activate
pip install numpy --no-cache-dir
```

### Error: "Illegal instruction" al importar numpy

**Causa:** Versión de numpy incompatible con ARM

**Solución:**
```bash
pip uninstall numpy
pip install "numpy<2.0.0"
```

### Audio crackling o dropouts

**Causa:** CPU sobrecargado o buffer insuficiente

**Solución 1 - Aumentar chunk_size:**
```json
{
  "audio": {
    "chunk_size": 2048  // o 4096
  }
}
```

**Solución 2 - Reducir sample_rate:**
```json
{
  "audio": {
    "sample_rate": 16000
  }
}
```

**Solución 3 - Deshabilitar time-stretch:**
```json
{
  "audio": {
    "enable_time_stretching": false
  }
}
```

### CPU al 100%

**Monitorear CPU:**
```bash
# En otra terminal
htop
```

**Soluciones:**
1. Reducir número de stems (solo bass + drums + vocal)
2. Deshabilitar time-stretching
3. Usar sample_rate más bajo (16000)
4. Activar governor performance:
```bash
sudo apt-get install -y cpufrequtils
sudo cpufreq-set -g performance
```

### Memoria insuficiente

**Verificar memoria:**
```bash
free -h
```

**Soluciones:**
1. Aumentar swap:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Cambiar CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

2. Cargar menos stems simultáneamente

---

## ⚡ Optimizaciones Adicionales

### 1. Overclock (Raspberry Pi 4)

```bash
sudo nano /boot/config.txt
```

Agregar:
```
# Overclock moderado
over_voltage=2
arm_freq=1750
gpu_freq=600
```

⚠️ **Requiere refrigeración adecuada**

### 2. Deshabilitar GUI (más memoria/CPU)

```bash
sudo systemctl set-default multi-user.target
sudo reboot
```

Revertir:
```bash
sudo systemctl set-default graphical.target
```

### 3. Governor de CPU

```bash
# Performance (máxima velocidad)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Ondemand (balance)
echo ondemand | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### 4. Usar USB 3.0 para Audio

Si tienes Raspberry Pi 4/5, conecta la interfaz de audio a puerto USB 3.0 (azul) para mejor rendimiento.

---

## 📊 Benchmarks Aproximados

### Raspberry Pi 5 (8GB)
- ✅ 4-5 stems simultáneos
- ✅ Time-stretching limitado (calidad baja)
- ✅ Sample rate: 22050-44100 Hz

### Raspberry Pi 4 (4GB)
- ✅ 3-4 stems simultáneos
- ⚠️ Time-stretching: NO recomendado
- ✅ Sample rate: 22050 Hz

### Raspberry Pi 3B+ (1GB)
- ⚠️ 2-3 stems máximo
- ❌ Time-stretching: NO
- ⚠️ Sample rate: 16000 Hz

---

## 🔧 Configuración de Audio en RPI

### Listar dispositivos de audio

```bash
# PyAudio devices
python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"

# ALSA devices
aplay -l
```

### Configurar dispositivo por defecto

```bash
sudo nano /etc/asound.conf
```

Agregar:
```
pcm.!default {
    type hw
    card 1
}
```

---

## 📡 Control Remoto vía OSC

Configurar para recibir OSC desde cualquier dispositivo en la red:

```json
{
  "osc": {
    "host": "0.0.0.0",  // Escuchar en todas las interfaces
    "port": 5005
  }
}
```

Desde otro dispositivo (laptop/phone):
```python
from pythonosc import udp_client

# Usar IP del Raspberry Pi
client = udp_client.SimpleUDPClient("192.168.1.100", 5005)
client.send_message("/energy", 0.8)
```

---

## 🌡️ Monitoreo de Sistema

### Script de monitoreo

```bash
# monitor_rpi.sh
#!/bin/bash
while true; do
    clear
    echo "=== Raspberry Pi Status ==="
    echo "CPU Temp: $(vcgencmd measure_temp)"
    echo "CPU Freq: $(vcgencmd measure_clock arm | awk -F= '{print $2/1000000 " MHz"}')"
    echo ""
    echo "=== Top Processes ==="
    ps aux --sort=-%cpu | head -5
    echo ""
    echo "=== Memory ==="
    free -h
    sleep 2
done
```

---

## 📝 Ejemplo de Uso Completo

```bash
# 1. Setup inicial (una vez)
./setup_venv_rpi.sh

# 2. Configurar para RPI
cp mixer_config_rpi.json mixer_config.json

# 3. Activar environment
source venv/bin/activate

# 4. Ejecutar
python performance_energy_mixer.py

# 5. En otra terminal, monitorear
htop

# 6. Enviar comandos OSC desde otro dispositivo
# Ver PERFORMANCE_ENERGY_GUIDE.md
```

---

## 🎯 Configuración Recomendada Final

Para Raspberry Pi 4 con 4GB:

```json
{
  "audio": {
    "sample_rate": 22050,
    "chunk_size": 1024,
    "enable_time_stretching": false,
    "master_volume": 0.7
  },
  "performance": {
    "low_latency_mode": true
  }
}
```

Cargar máximo 3-4 stems (bass, drums, vocals).

---

## 🔗 Enlaces Útiles

- [Raspberry Pi Audio Guide](https://www.raspberrypi.com/documentation/computers/configuration.html#audio)
- [Overclocking Guide](https://www.raspberrypi.com/documentation/computers/config_txt.html#overclocking)
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)

---

## ✅ Checklist Post-Setup

- [ ] Sistema actualizado
- [ ] portaudio instalado
- [ ] PyAudio funciona (import pyaudio sin error)
- [ ] librosa/numpy importan correctamente
- [ ] mixer_config_rpi.json copiado a mixer_config.json
- [ ] Audio device configurado
- [ ] Performance mixer inicia sin errores
- [ ] CPU < 80% durante reproducción
- [ ] Temperatura < 70°C
- [ ] Audio sin crackling

---

## 🆘 Ayuda Adicional

Si encuentras problemas específicos de ARM/Raspberry Pi, consulta:
- `/var/log/syslog` para errores del sistema
- `dmesg | tail` para problemas de hardware
- `vcgencmd get_throttled` para verificar throttling
