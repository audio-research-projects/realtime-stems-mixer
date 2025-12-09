# 🎵 Tips para Mejorar Calidad de Audio

Guía para resolver problemas de distorsión y mejorar la calidad del audio.

## 🔍 Problema: Voces Distorsionadas

### Causas Comunes:

1. **Clipping (Sobrecarga de Volumen)**
   - Múltiples stems se suman y exceden 1.0
   - Resultado: Audio distorsionado, "crujiente"

2. **Cambio de Pitch no Deseado**
   - BPMs muy diferentes entre canciones
   - Sin time-stretching, el pitch cambia junto con el tempo
   - Ejemplo: 95 BPM → 120 BPM = voz 26% más aguda

3. **Problemas de Audio en Raspberry Pi**
   - Buffer insuficiente
   - USB audio con latencia
   - CPU sobrecargado

---

## ✅ Soluciones Implementadas

### 1. Volúmenes Reducidos

**Configuración optimizada para RPi:**

```json
{
  "audio": {
    "master_volume": 0.5  // Reducido de 0.7
  },
  "mixing": {
    "stem_volumes": {
      "bass": 0.5,    // Reducido ~30%
      "drums": 0.6,   // Reducido ~25%
      "vocals": 0.55, // Reducido ~27%
      "piano": 0.4,   // Reducido ~33%
      "other": 0.35   // Reducido ~30%
    }
  }
}
```

**Aplicar:**
```bash
cp mixer_config_rpi.json mixer_config.json
```

---

### 2. Soft Limiting Mejorado

El código ahora aplica limitador más agresivo:

```python
# Si amplitud > 0.8 (antes 0.9)
if max_amp > 0.8:
    mixed_audio = np.tanh(mixed_audio / max_amp) * 0.8

# Hard limiting de emergencia
elif max_amp > 0.95:
    mixed_audio = np.clip(mixed_audio, -0.95, 0.95)
```

**Resultado:**
- ✅ Previene clipping
- ✅ Suaviza peaks
- ✅ Audio más limpio

---

### 3. Selección de BPM Compatible

**Nuevo sistema de filtrado:**

El mixer ahora **solo carga canciones con BPM ±10%** del target:

```
Target: 120 BPM
Rango aceptable: 108-132 BPM

✅ 115 BPM - OK (4% diferencia)
✅ 125 BPM - OK (4% diferencia)
⚠️  95 BPM - Rechazado (21% diferencia)
⚠️  140 BPM - Rechazado (17% diferencia)
```

**Ventajas:**
- ✅ Cambios de pitch mínimos (<10%)
- ✅ Audio más natural
- ✅ No requiere time-stretching (ahorro de CPU)

**Ver al iniciar:**
```bash
🎸 Loading base stems...
✅ Found 8 compatible songs (BPM ±10.0%)
  ✅ bass: Espresso Macchiato (BPM: 120, diff: 0.0%)
  ✅ drums: Kiss Kiss Goodbye (BPM: 125, diff: 4.2%)
  ✅ other: Run With U (BPM: 115, diff: 4.2%)
```

---

## 🎛️ Ajustes en Tiempo Real

### Vía CLI:

```bash
🎭 > vocals 0.4      # Bajar vocales si suenan distorsionados
🎭 > bass 0.3        # Bajar bass
🎭 > drums 0.5       # Bajar drums
🎭 > status          # Ver volúmenes actuales
```

### Vía OSC:

```python
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("192.168.x.x", 5005)

# Bajar master volume
client.send_message("/master_volume", 0.4)

# Ajustar stems individuales (no implementado aún)
# client.send_message("/stem/vocals", 0.4)
```

---

## 📊 Monitoreo de Calidad

### Indicadores de BPM:

Al cargar vocales, verás:

```bash
🎤 NEW VOCAL: Kiss Kiss Goodbye (BPM: 125 vs 120, diff: 4.2%, pitch: ✅ minimal)
🎤 NEW VOCAL: Zjerm (BPM: 95 vs 120, diff: 26.3%, pitch: 🔴 noticeable)
```

**Leyenda:**
- ✅ **minimal** (< 5%) - Pitch casi imperceptible
- ⚠️ **moderate** (5-10%) - Pitch audible pero aceptable
- 🔴 **noticeable** (> 10%) - Pitch muy evidente, puede sonar mal

---

## 🎯 Configuración por Escenario

### Para Audio Limpio (Prioridad: Calidad)

```json
{
  "audio": {
    "master_volume": 0.4,
    "enable_time_stretching": false
  },
  "mixing": {
    "stem_volumes": {
      "bass": 0.4,
      "drums": 0.5,
      "vocals": 0.45,
      "piano": 0.3,
      "other": 0.3
    }
  }
}
```

- BPM tolerance: 10%
- Volúmenes bajos
- Sin time-stretch (más CPU eficiente)

---

### Para Máxima Compatibilidad (Prioridad: Variedad)

```json
{
  "audio": {
    "master_volume": 0.5,
    "enable_time_stretching": true,
    "time_stretch_threshold": 0.05
  }
}
```

- BPM tolerance: 20%
- Time-stretching activado (preserva pitch)
- Más carga de CPU

---

### Para Raspberry Pi (Balance)

```bash
# Usar config optimizada
cp mixer_config_rpi.json mixer_config.json
```

```json
{
  "audio": {
    "sample_rate": 22050,        // Menos carga CPU
    "master_volume": 0.5,         // Previene clipping
    "enable_time_stretching": false  // Ahorro CPU crítico
  }
}
```

- BPM tolerance: 10% (estricto)
- Sample rate reducido
- Sin time-stretching

---

## 🔧 Debugging Audio

### Check Clipping:

El mixer imprime cuando aplica limiting:

```bash
# Si ves esto frecuentemente, bajar volúmenes
⚠️  Soft limiting applied (peak: 0.92)
```

### Check BPM Compatibility:

```bash
# Bueno - diferencia pequeña
✅ bass: Song A (BPM: 118, diff: 1.7%)

# Advertencia - diferencia notable
⚠️  vocals: Song B (BPM: 135, diff: 12.5%)

# Problemas esperados
🔴 No compatible vocals at 120 BPM (±10.0%)
```

### Check CPU en RPi:

```bash
# En otra terminal
htop

# Si CPU > 90%, reducir:
# 1. Sample rate (22050 → 16000)
# 2. Número de stems (solo 3 stems)
# 3. Chunk size (1024 → 2048)
```

---

## 📈 Mejoras Progresivas

### Paso 1: Básico (Ya implementado)
- ✅ Volúmenes reducidos
- ✅ Soft limiting
- ✅ BPM filtering ±10%

### Paso 2: Avanzado (Opcional)
- Compressor dinámico
- EQ automático
- Normalización por stem

### Paso 3: Profesional (Futuro)
- Análisis de key/tonalidad
- Auto-gain staging
- Sidechain compression

---

## 🎓 Conceptos Técnicos

### Time-Stretching vs Playback Rate:

**Playback Rate Simple (Actual):**
```python
# Como acelerar un vinyl
speed = 120 / 95 = 1.26x
tempo: +26% ✅
pitch: +26% ⚠️ (más agudo)
cpu: Bajo ✅
```

**Time-Stretching (Opcional):**
```python
# Librosa preserva pitch
librosa.effects.time_stretch(audio, rate=1.26)
tempo: +26% ✅
pitch: 0% ✅ (preservado)
cpu: Alto ⚠️
```

### BPM Tolerance Math:

```
Target: 120 BPM
Tolerance: 10%

Min BPM = 120 * (1 - 0.10) = 108
Max BPM = 120 * (1 + 0.10) = 132

Acceptable range: [108, 132]
```

### Pitch Change Calculation:

```python
# Fórmula
semitones = 12 * log2(new_bpm / old_bpm)

# Ejemplo: 95 → 120 BPM
semitones = 12 * log2(120/95)
semitones = 12 * 0.336 = 4.03 semitones (⅓ de octava)
# Resultado: Voz suena 4 semitonos más aguda (aprox. E → G#)
```

---

## ✅ Checklist de Calidad

Al iniciar performance:

- [ ] Config RPi aplicada (`mixer_config_rpi.json`)
- [ ] Volúmenes reducidos (master ≤ 0.5)
- [ ] BPM filtering activo (mensajes ±10%)
- [ ] Stems cargados con BPM cercano
- [ ] Soft limiting funcionando
- [ ] Audio sin clipping
- [ ] Vocales suenan naturales (pitch minimal)
- [ ] CPU < 80% (si RPi)

---

## 🆘 Troubleshooting

**Problema:** Aún hay distorsión
```bash
# Solución 1: Bajar más los volúmenes
🎭 > vocals 0.3
🎭 > bass 0.3
🎭 > drums 0.4

# Solución 2: Usar menos stems
# Solo cargar bass + drums + vocals (quitar piano/other)
```

**Problema:** Voces suenan "chipmunks"
```bash
# Causa: BPM muy diferente
# Solución: Cambiar base_bpm o activar time-stretch

# Opción 1: Cambiar BPM base
python performance_energy_mixer.py --bpm 110

# Opción 2: Activar time-stretch (más CPU)
# Editar mixer_config.json
"enable_time_stretching": true
```

**Problema:** CPU al 100% en RPi
```bash
# Reducir calidad:
# 1. Sample rate: 22050 → 16000
# 2. Chunk size: 1024 → 2048
# 3. Deshabilitar piano/other
```

---

## 📚 Referencias

- [Audio Clipping (Wikipedia)](https://en.wikipedia.org/wiki/Clipping_(audio))
- [Time Stretching (librosa)](https://librosa.org/doc/main/generated/librosa.effects.time_stretch.html)
- [BPM Matching Guide](https://www.native-instruments.com/en/products/traktor/dj-software/traktor-pro-3/dj-101-beatmatching/)
