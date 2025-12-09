# 🔧 Setup con Virtual Environment (venv)

Guía para configurar el Performance Energy Mixer usando Python virtual environment en lugar de Conda.

## 📋 Requisitos Previos

### Sistema Operativo

**macOS:**
```bash
# Instalar Homebrew si no está instalado
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar portaudio (requerido para PyAudio)
brew install portaudio

# Python 3.8+ viene preinstalado, o instalar con:
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
# Instalar Python 3 y dependencias de audio
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install portaudio19-dev python3-pyaudio

# Para librosa/soundfile
sudo apt-get install libsndfile1
```

**Windows:**
```bash
# Instalar Python 3.8+ desde python.org
# Descargar e instalar desde: https://www.python.org/downloads/
```

---

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
# 1. Dar permisos de ejecución
chmod +x setup_venv.sh

# 2. Ejecutar setup
./setup_venv.sh

# 3. Ejecutar performance mixer
./run_performance_venv.sh
```

---

### Opción 2: Manual

```bash
# 1. Crear virtual environment
python3 -m venv venv

# 2. Activar environment
source venv/bin/activate

# 3. Actualizar pip
pip install --upgrade pip

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
python performance_energy_mixer.py
```

---

## 📦 Dependencias Instaladas

El script instala automáticamente:

### Core (Obligatorias)
- **numpy** - Procesamiento numérico
- **scipy** - Algoritmos científicos
- **librosa** - Análisis y procesamiento de audio
- **soundfile** - Lectura/escritura de archivos de audio
- **pyaudio** - I/O de audio en tiempo real
- **python-osc** - Comunicación OSC

### Adicionales (Opcionales)
- **pydub** - Manipulación de audio
- **scikit-learn** - Machine learning (futuro)
- **matplotlib** - Visualizaciones
- Ver [requirements.txt](requirements.txt) para lista completa

---

## 🔍 Verificar Instalación

```bash
# Activar environment
source venv/bin/activate

# Verificar paquetes instalados
pip list | grep -E "numpy|librosa|pyaudio|python-osc"

# Test rápido
python3 -c "import librosa, pyaudio, numpy; print('✅ All OK')"
```

---

## 🐛 Solución de Problemas

### PyAudio no se instala en macOS

```bash
# Instalar portaudio primero
brew install portaudio

# Reinstalar PyAudio
pip install --force-reinstall pyaudio
```

### PyAudio no se instala en Linux

```bash
# Instalar dependencias del sistema
sudo apt-get install portaudio19-dev python3-pyaudio

# Reinstalar
pip install --force-reinstall pyaudio
```

### librosa es muy lento

```bash
# Instalar numba para acelerar librosa
pip install numba
```

### Error: "No module named 'config_loader'"

```bash
# Asegurarse de estar en el directorio correcto
cd /path/to/realtime-stems-mixer

# Verificar que config_loader.py existe
ls -la config_loader.py
```

### Error: "stems directory not found"

```bash
# Verificar estructura de directorios
ls -la stems/
ls -la song-structures/

# Si no existen, crear y agregar stems
mkdir -p stems
```

---

## 🔄 Actualizar Dependencias

```bash
# Activar environment
source venv/bin/activate

# Actualizar todas las dependencias
pip install --upgrade -r requirements.txt

# O actualizar paquetes específicos
pip install --upgrade librosa numpy
```

---

## 🗑️ Limpiar Environment

```bash
# Desactivar environment (si está activo)
deactivate

# Eliminar environment completo
rm -rf venv

# Reinstalar desde cero
./setup_venv.sh
```

---

## 📚 Uso del Environment

### Activar

```bash
source venv/bin/activate
```

Verás el prompt cambiar a:
```
(venv) user@host:~/realtime-stems-mixer$
```

### Desactivar

```bash
deactivate
```

### Usar con Scripts

El script [run_performance_venv.sh](run_performance_venv.sh) activa automáticamente el environment:

```bash
./run_performance_venv.sh
```

---

## 🆚 venv vs Conda

| Aspecto | venv | Conda |
|---------|------|-------|
| **Instalación** | ✅ Incluido en Python | ❌ Requiere instalación |
| **Tamaño** | 🟢 ~50MB | 🔴 ~500MB+ |
| **Velocidad** | 🟢 Rápido | 🟡 Más lento |
| **Gestión** | 🟢 Simple | 🟡 Más complejo |
| **Dependencias Sistema** | ❌ Manual | ✅ Automático |

**Recomendación:** Usar **venv** para este proyecto (más ligero y simple).

---

## 📁 Estructura del Proyecto

```
realtime-stems-mixer/
├── venv/                      # Virtual environment (auto-creado)
├── stems/                     # Archivos de audio stems
├── song-structures/           # Estructuras JSON
├── performance_energy_mixer.py
├── config_loader.py
├── mixer_config.json
├── requirements.txt           # Dependencias Python
├── setup_venv.sh             # Script de instalación
├── run_performance_venv.sh   # Script de ejecución
└── SETUP_VENV.md            # Este archivo
```

---

## ✅ Checklist Post-Instalación

- [ ] `venv/` directorio existe
- [ ] Environment se activa correctamente
- [ ] `pip list` muestra librosa, pyaudio, numpy
- [ ] Test Python import funciona
- [ ] `./run_performance_venv.sh` inicia sin errores
- [ ] Audio se escucha correctamente

---

## 🎯 Próximos Pasos

Una vez instalado:

1. **Configurar audio**: Ver [AUDIO_CONFIG.md](AUDIO_CONFIG.md)
2. **Ejecutar performance**: `./run_performance_venv.sh`
3. **Enviar OSC messages**: Ver [PERFORMANCE_ENERGY_GUIDE.md](PERFORMANCE_ENERGY_GUIDE.md)

---

## 🔗 Enlaces Útiles

- [Python venv Documentation](https://docs.python.org/3/library/venv.html)
- [librosa Documentation](https://librosa.org/doc/latest/index.html)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/)
- [python-osc Documentation](https://python-osc.readthedocs.io/)
