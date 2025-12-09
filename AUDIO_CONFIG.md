# 🎵 Configuración de Audio - Performance Energy Mixer

## 📋 Configuración Actual

El sistema ahora **respeta completamente** la configuración en [mixer_config.json](mixer_config.json).

## ⚙️ Opciones de Ajuste de BPM

### 1. Time-Stretching (Recomendado) ✅

**Configuración:**
```json
{
  "audio": {
    "enable_time_stretching": true,
    "enable_pitch_shifting": false,
    "time_stretch_threshold": 0.05
  }
}
```

**Comportamiento:**
- ✅ **Tempo cambia** (BPM se ajusta al target)
- ✅ **Pitch NO cambia** (mantiene tonalidad original)
- 🎵 Suena natural, sin efecto "chipmunk"

**Ejemplo:**
- Canción original: 95 BPM en tono C
- Target: 120 BPM
- Resultado: 120 BPM en tono C (acelera sin cambiar tono)

**Calidad:**
```json
{
  "performance": {
    "high_quality_time_stretch": true,  // Mejor calidad, más CPU
    "hop_length": 256                    // Menor = mejor calidad, más CPU
  }
}
```

---

### 2. Playback Rate Simple (Sin Time-Stretch)

**Configuración:**
```json
{
  "audio": {
    "enable_time_stretching": false,
    "enable_pitch_shifting": false
  }
}
```

**Comportamiento:**
- ⚡ **Tempo cambia** (BPM se ajusta)
- ⚡ **Pitch TAMBIÉN cambia** (como vinyl/cassette acelerado)
- 🎼 Acelerar = pitch más alto, ralentizar = pitch más bajo

**Ejemplo:**
- Canción original: 95 BPM en tono C
- Target: 120 BPM
- Resultado: 120 BPM en tono ~D# (acelera y sube tono)

**Ventajas:**
- ⚡ Mínima carga de CPU
- 🔊 Sin artefactos de procesamiento

**Desventajas:**
- 🎵 Cambio de tonalidad puede sonar extraño
- 🎤 Vocales suenan como "chipmunks" si se acelera mucho

---

### 3. Time-Stretch + Pitch Shift

**Configuración:**
```json
{
  "audio": {
    "enable_time_stretching": true,
    "enable_pitch_shifting": true,
    "max_pitch_shift_semitones": 6
  }
}
```

**Comportamiento:**
- 🎵 **Tempo cambia** (vía time-stretch)
- 🎹 **Pitch se ajusta** (corrección adicional de tonalidad)
- 🎼 Permite transponer para mejor mezcla armónica

**Ejemplo:**
- Canción original: 95 BPM en tono C
- Target: 120 BPM
- Resultado: 120 BPM en tono ajustado (ej. G para armonía)

**Uso:**
- Mezcla de canciones en diferentes tonalidades
- Compatibilidad armónica (Camelot Wheel)

**Advertencia:**
- ⚠️ Más carga de CPU
- ⚠️ Puede introducir artefactos audibles

---

## 🎛️ Threshold de Time-Stretch

```json
{
  "audio": {
    "time_stretch_threshold": 0.05  // 5%
  }
}
```

**Significado:**
- Solo aplica time-stretch si el cambio de BPM es > 5%
- Cambios pequeños usan playback rate directo (más eficiente)

**Ejemplos:**
- 120 → 125 BPM (4.2%) → **No** time-stretch
- 120 → 140 BPM (16.7%) → **Sí** time-stretch

---

## 📊 Comparación de Métodos

| Método | Tempo | Pitch | CPU | Calidad | Uso |
|--------|-------|-------|-----|---------|-----|
| **Time-Stretch** | ✅ Ajusta | ✅ Mantiene | 🔴 Alta | ⭐⭐⭐⭐ | Performance general |
| **Simple Rate** | ✅ Ajusta | ❌ Cambia | 🟢 Baja | ⭐⭐ | Compatible BPM cercanos |
| **Time + Pitch** | ✅ Ajusta | ⚡ Controla | 🔴🔴 Muy Alta | ⭐⭐⭐ | Mezcla armónica |

---

## 🎵 Configuración Recomendada por Escenario

### 🎭 Performance Automática (Default)
```json
{
  "audio": {
    "enable_time_stretching": true,
    "enable_pitch_shifting": false,
    "time_stretch_threshold": 0.05
  },
  "performance": {
    "high_quality_time_stretch": true,
    "hop_length": 256
  }
}
```
✅ Mejor balance calidad/rendimiento

---

### ⚡ Baja Latencia / Bajo CPU
```json
{
  "audio": {
    "enable_time_stretching": false,
    "enable_pitch_shifting": false
  },
  "performance": {
    "low_latency_mode": true
  }
}
```
⚠️ Solo si BPMs son muy similares (±5%)

---

### 🎼 Mezcla Harmónica Profesional
```json
{
  "audio": {
    "enable_time_stretching": true,
    "enable_pitch_shifting": true,
    "max_pitch_shift_semitones": 3,
    "time_stretch_threshold": 0.02
  },
  "performance": {
    "high_quality_time_stretch": true,
    "hop_length": 128
  }
}
```
⚠️ Requiere CPU potente

---

## 🔧 Ajuste Fino

### Calidad vs Rendimiento

**Alta Calidad:**
```json
{
  "performance": {
    "high_quality_time_stretch": true,
    "hop_length": 128  // Menor = mejor calidad
  }
}
```

**Alto Rendimiento:**
```json
{
  "performance": {
    "high_quality_time_stretch": false,
    "hop_length": 512  // Mayor = menos CPU
  }
}
```

---

## 🎯 Cómo Funciona Actualmente

Con la configuración actual (`enable_time_stretching: true`):

```python
# Canción A: 95 BPM → Target: 120 BPM
playback_rate = 120 / 95 = 1.26  # 26% más rápido

# Time-stretching aplicado:
samples = librosa.effects.time_stretch(samples, rate=1/1.26)
# Resultado: tempo 120 BPM, pitch original
```

---

## 📈 Monitoreo

Al iniciar, verás:
```bash
✅ Loaded configuration from mixer_config.json
🎵 Pitch shifting DISABLED
⏱️  Time stretching ENABLED
```

---

## 🐛 Solución de Problemas

### Audio suena distorsionado
- Reducir `hop_length` para mejor calidad
- Aumentar `time_stretch_threshold`

### Mucha carga de CPU
- Desactivar `high_quality_time_stretch`
- Aumentar `hop_length` a 512
- Considerar `enable_time_stretching: false`

### Pitch suena extraño
- Asegurarse que `enable_pitch_shifting: false`
- Verificar que `enable_time_stretching: true`

### Vocales suenan como "chipmunks"
- Activar `enable_time_stretching: true`
- Si ya está activado, reducir diferencias de BPM

---

## 📚 Referencias

- **librosa.effects.time_stretch**: [Documentación](https://librosa.org/doc/main/generated/librosa.effects.time_stretch.html)
- **librosa.effects.pitch_shift**: [Documentación](https://librosa.org/doc/main/generated/librosa.effects.pitch_shift.html)
