# 🎭 Energy-Responsive Performance Mixer Guide

Sistema de performance automática que responde a la energía del público en tiempo real.

## 🎵 Concepto

El mixer crea una **base estable** (bass, drums, other) y **cambia los vocales dinámicamente** basándose en el feedback de energía del público:

- **Energía BAJA** (< 0.3) → Cambia a nuevo vocal para revitalizar
- **Energía ALTA** (> 0.7) → Mantiene el vocal exitoso, lo repite
- **Energía MEDIA** → Observa y espera antes de cambiar

## 🚀 Inicio Rápido

```bash
./run_performance.sh
```

O manualmente:
```bash
source /Users/hordia/miniconda3/etc/profile.d/conda.sh
conda activate UBA-crowdstream
python performance_energy_mixer.py
```

## 🎛️ Parámetros de Inicio

La performance comienza automáticamente con:
- **BPM Base**: 120 (ajustable)
- **Stems Base**: Bass, drums, other de canciones compatibles
- **Vocal Inicial**: Selección aleatoria de vocal compatible
- **Energía Inicial**: 0.5 (neutral)

## 📡 Control OSC

### Energía del Público
```python
/energy [0.0-1.0]      # Nivel de energía/movimiento del público
/movement [0.0-1.0]    # Alias para energía
```

**Ejemplos con python-osc:**
```python
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("localhost", 5005)

# Simular baja energía (público quieto)
client.send_message("/energy", 0.2)

# Simular alta energía (público bailando)
client.send_message("/energy", 0.9)

# Energía media
client.send_message("/energy", 0.5)
```

### Otros Controles
```python
/bpm [60-200]          # Cambiar BPM base
/master_volume [0-1]   # Volumen master
/status                # Mostrar estado actual
/next_vocal            # Forzar cambio de vocal inmediato
```

## 💻 Comandos CLI

Durante la ejecución puedes usar:

```bash
🎭 > energy 0.2        # Simular baja energía
🎭 > energy 0.8        # Simular alta energía
🎭 > bpm 130           # Cambiar a 130 BPM
🎭 > status            # Ver estado actual
🎭 > next              # Forzar siguiente vocal
🎭 > quit              # Salir
```

## 🎮 Ejemplo de Uso

### Simulación Manual
```bash
# 1. Iniciar performance
./run_performance.sh

# 2. Dejar que corra con energía neutra (0.5)
# El sistema mantiene el vocal inicial

# 3. Simular que el público no baila
🎭 > energy 0.2

# Espera 10-15 segundos...
# Sistema detecta baja energía → Cambia a nuevo vocal

# 4. Simular que el nuevo vocal funciona
🎭 > energy 0.8

# Sistema mantiene el vocal exitoso, lo repite

# 5. Ver estado
🎭 > status
```

### Integración con Sensor de Movimiento

```python
# sensor_to_osc.py
from pythonosc import udp_client
import movement_sensor  # Tu sensor de movimiento

client = udp_client.SimpleUDPClient("localhost", 5005)

while True:
    # Leer nivel de movimiento del público (0.0 - 1.0)
    movement = movement_sensor.read_normalized()

    # Enviar al mixer
    client.send_message("/energy", movement)

    time.sleep(1.0)  # Actualizar cada segundo
```

## ⚙️ Configuración

### Parámetros de Energía

Editar en `performance_energy_mixer.py`:

```python
self.energy_threshold_low = 0.3   # Umbral bajo (cambiar vocal)
self.energy_threshold_high = 0.7  # Umbral alto (mantener vocal)
self.min_vocal_duration = 15.0    # Mínimo 15s antes de cambiar
self.energy_stability_time = 10.0 # Esperar 10s estable antes de actuar
self.max_vocal_repeats = 2        # Repetir 2 veces vocales exitosos
```

### BPM Inicial

```python
performance = EnergyResponsivePerformance(
    base_bpm=120.0,      # Cambiar BPM base aquí
    auto_start=True
)
```

### Directorio de Stems

```python
performance = EnergyResponsivePerformance(
    stems_dir="../../stems",           # Ruta a stems
    structures_dir="song-structures",  # Ruta a estructuras
    base_bpm=120.0
)
```

## 📊 Lógica de Decisión

```
┌─────────────────────────────────────────────┐
│         MONITOREO DE ENERGÍA                │
│         (cada 2 segundos)                   │
└─────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Energía < 0.3 ?     │
        └───────────────────────┘
                │           │
             SÍ │           │ NO
                ▼           │
    ┌──────────────────┐   │
    │ Cambiar vocal    │   │
    │ (público quieto) │   │
    └──────────────────┘   │
                           ▼
              ┌───────────────────────┐
              │   Energía > 0.7 ?     │
              └───────────────────────┘
                      │           │
                   SÍ │           │ NO
                      ▼           │
          ┌──────────────────┐   │
          │ Mantener vocal   │   │
          │ Repetir 2 veces  │   │
          └──────────────────┘   │
                                 ▼
                    ┌──────────────────┐
                    │ Observar         │
                    │ (energía media)  │
                    └──────────────────┘
```

## 🎵 Selección de Stems

### Base Estable
- Selecciona bass, drums, other de canciones con BPM cercano al target
- Se mantienen constantes durante la performance
- Ajuste automático de tempo via time-stretching

### Vocales Dinámicos
- Selecciona de canciones con BPM ±15% del base
- Cambia según respuesta del público
- Se repiten si funcionan bien (alta energía)

## 🔧 Audio Config

En `mixer_config.json`:

```json
{
  "audio": {
    "sample_rate": 48000,
    "chunk_size": 512,
    "enable_time_stretching": false,
    "master_volume": 0.8
  },
  "mixing": {
    "stem_volumes": {
      "bass": 0.8,
      "drums": 0.9,
      "vocals": 0.8,
      "piano": 0.7,
      "other": 0.6
    }
  }
}
```

## 📈 Monitoreo

### Ver Estado en Tiempo Real
```bash
🎭 > status

🎭 PERFORMANCE STATUS
==================================================
⚡ Current Energy: 0.75
🎵 Base BPM: 120.0
🔊 Master Volume: 0.80

🎸 Base Stems (Stable):
  ▶️ bass: Zjerm (Eurovision 2025 - Albania)_bass
  ▶️ drums: SURVIVOR (Eurovision 2025 - Armenia)_drums
  ▶️ other: Hallucination (Eurovision 2025 - Denmark)_other

🎤 Current Vocal:
  ▶️ Kiss Kiss Goodbye
  📊 Repeat count: 1/2

⏱️ Time since vocal change: 23.4s
📊 Energy thresholds: Low < 0.30, High > 0.70
```

## 🐛 Troubleshooting

### No se carga ninguna canción
```bash
# Verificar que existe el directorio stems
ls -la ../../stems/

# Verificar estructuras
ls -la song-structures/
```

### Audio no se escucha
- Verificar que pyaudio está instalado: `pip list | grep pyaudio`
- Verificar dispositivo de salida de audio del sistema
- Verificar volumen master en config

### Cambios de vocal muy frecuentes
- Aumentar `min_vocal_duration` (default 15s)
- Aumentar `energy_stability_time` (default 10s)

### Cambios de vocal muy lentos
- Reducir `min_vocal_duration`
- Reducir `energy_stability_time`
- Ajustar thresholds de energía

## 🎯 Casos de Uso

### 1. Club/Evento con Sensor de Movimiento
```python
# Integrar sensor Kinect/webcam
movement_energy = detect_crowd_movement()  # 0.0 - 1.0
client.send_message("/energy", movement_energy)
```

### 2. Performance Controlada Manualmente
```bash
# DJ controla energía manualmente según respuesta visual
🎭 > energy 0.2   # Público quieto
🎭 > energy 0.9   # Público eufórico
```

### 3. Simulación/Testing
```python
# Simular cambios de energía automáticos
import time
energies = [0.5, 0.3, 0.2, 0.8, 0.9, 0.7, 0.4, 0.3]
for e in energies:
    client.send_message("/energy", e)
    time.sleep(20)  # 20 segundos cada nivel
```

## 📚 Recursos

- **Stems**: Usar demucs o spleeter para separación de stems
- **Estructuras**: Usar [all-in-one](https://github.com/hordiales/all-in-one) para análisis
- **OSC**: [python-osc](https://pypi.org/project/python-osc/) para control
- **CrowdStream**: [Proyecto completo](https://timmd-9216.github.io/crowdstream/)
