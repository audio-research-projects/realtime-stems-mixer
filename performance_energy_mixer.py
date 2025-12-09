#!/usr/bin/env python3
"""
Eurovision Energy-Responsive Performance Mixer
Automatic performance that responds to crowd energy via OSC

Base stable: bass, drums, other stems
Vocals: change based on crowd energy/movement feedback
"""

import threading
import time
import random
import json
import numpy as np
import librosa
from pathlib import Path
import pyaudio
from pythonosc import dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from config_loader import ConfigLoader

@dataclass
class Song:
    """Song metadata"""
    name: str
    bpm: float
    stem_files: Dict[str, Path]
    sections: List[Dict] = field(default_factory=list)

@dataclass
class StemPlayer:
    """Individual stem player with real-time controls"""
    name: str
    audio_data: np.ndarray
    sample_rate: int
    original_bpm: float
    volume: float = 0.8
    position: int = 0
    playing: bool = True
    loop: bool = True

    def get_samples(self, num_samples: int, target_bpm: float) -> np.ndarray:
        """Get samples with real-time BPM adjustment"""
        if not self.playing or len(self.audio_data) == 0:
            return np.zeros(num_samples, dtype=np.float32)

        # Calculate playback rate for BPM change
        playback_rate = target_bpm / self.original_bpm if self.original_bpm > 0 else 1.0

        # Adjust sample count based on playback rate
        source_samples_needed = int(num_samples * playback_rate)

        # Get samples from current position
        if self.position + source_samples_needed <= len(self.audio_data):
            samples = self.audio_data[self.position:self.position + source_samples_needed]
            self.position += source_samples_needed
        else:
            # Handle end of audio - loop
            if self.loop:
                remaining = len(self.audio_data) - self.position
                first_part = self.audio_data[self.position:] if remaining > 0 else np.array([], dtype=np.float32)

                # Reset position and get rest
                loops_needed = (source_samples_needed - len(first_part)) // len(self.audio_data) + 1
                second_part = np.tile(self.audio_data, loops_needed)[:source_samples_needed - len(first_part)]

                samples = np.concatenate([first_part, second_part]) if len(first_part) > 0 else second_part
                self.position = len(second_part)
            else:
                samples = np.zeros(source_samples_needed, dtype=np.float32)

        # Time-stretch if needed (simple)
        if abs(playback_rate - 1.0) > 0.02:
            try:
                samples = librosa.effects.time_stretch(samples, rate=1.0/playback_rate)
            except:
                pass

        # Ensure exact output length
        if len(samples) != num_samples:
            if len(samples) > num_samples:
                samples = samples[:num_samples]
            else:
                samples = np.pad(samples, (0, num_samples - len(samples)))

        # Apply volume
        return samples * self.volume


class EnergyResponsivePerformance:
    """Smart performance that responds to crowd energy"""

    def __init__(self, stems_dir: str = "stems", structures_dir: str = "song-structures",
                 osc_port: int = 5005, config_file: str = "mixer_config.json",
                 auto_start: bool = True, base_bpm: float = 120.0):

        # Load configuration
        self.config_loader = ConfigLoader(config_file)
        self.config = self.config_loader.load_config()

        # Audio setup
        self.sample_rate = self.config.audio.sample_rate
        self.chunk_size = self.config.audio.chunk_size
        self.pyaudio = pyaudio.PyAudio()
        self.audio_stream = None

        # Directories
        self.stems_dir = Path(stems_dir)
        self.structures_dir = Path(structures_dir)

        # Performance state
        self.base_bpm = base_bpm
        self.current_energy = 0.5  # 0.0 = no movement, 1.0 = high energy
        self.energy_threshold_low = 0.3  # Below this = low energy
        self.energy_threshold_high = 0.7  # Above this = high energy
        self.master_volume = self.config.audio.master_volume
        self.settings_lock = threading.Lock()

        # Track management
        self.songs: Dict[str, Song] = {}
        self._load_songs()
        self.available_songs = list(self.songs.keys())
        self.vocal_tracks = []  # Songs available for vocal rotation

        # Active stem players
        self.base_stems: Dict[str, StemPlayer] = {}  # bass, drums, other
        self.current_vocal: Optional[StemPlayer] = None
        self.current_vocal_song_name = None
        self.vocal_repeat_count = 0
        self.max_vocal_repeats = 2

        # Energy monitoring
        self.last_energy_change = time.time()
        self.energy_stability_time = 10.0  # Seconds to wait before changing
        self.last_vocal_change = time.time()
        self.min_vocal_duration = 15.0  # Minimum seconds per vocal

        # Find vocal tracks
        for song_name, song in self.songs.items():
            if 'vocals' in song.stem_files:
                self.vocal_tracks.append(song_name)

        # OSC server for energy feedback
        self.osc_port = osc_port
        self.osc_server = None
        self._setup_osc_server()

        # Performance thread
        self.running = False
        self.performance_thread = threading.Thread(target=self._performance_loop, daemon=True)

        print(f"🎭🔥 ENERGY-RESPONSIVE EUROVISION PERFORMANCE 🔥🎭")
        print(f"🎵 Songs Available: {len(self.available_songs)}")
        print(f"🎤 Vocal Tracks: {len(self.vocal_tracks)}")
        print(f"🎛️ Base BPM: {self.base_bpm}")
        print(f"📡 OSC Control: localhost:{osc_port}")
        print(f"⚡ Energy-responsive: Vocals change based on crowd feedback")

        # Auto-start performance
        if auto_start:
            self._load_base_stems()

    def _load_songs(self):
        """Load song information from stems directory and structures"""
        print("🎵 Loading song library...")

        # Load structure JSON files
        song_structures = {}
        if self.structures_dir.exists():
            for json_file in self.structures_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    sections = []
                    for seg in data.get('segments', []):
                        sections.append({
                            'start': seg['start'],
                            'end': seg['end'],
                            'label': seg['label']
                        })

                    song_structures[json_file.stem] = {
                        'bpm': data.get('bpm', 120),
                        'sections': sections
                    }
                except Exception as e:
                    pass  # Skip invalid files

        # Load song directories
        if self.stems_dir.exists():
            for song_dir in self.stems_dir.iterdir():
                if song_dir.is_dir():
                    stem_files = {}
                    stem_types = ['bass', 'drums', 'vocals', 'piano', 'other']

                    for stem_type in stem_types:
                        stem_file = song_dir / f"{stem_type}.wav"
                        if stem_file.exists():
                            stem_files[stem_type] = stem_file

                    if len(stem_files) >= 2:
                        # Find matching structure
                        structure = None
                        for struct_name, struct_data in song_structures.items():
                            if song_dir.name in struct_name:
                                structure = struct_data
                                break

                        bpm = structure['bpm'] if structure else 120.0
                        sections = structure['sections'] if structure else []

                        song = Song(
                            name=song_dir.name,
                            bpm=bpm,
                            stem_files=stem_files,
                            sections=sections
                        )

                        self.songs[song_dir.name] = song

        print(f"✅ Loaded {len(self.songs)} songs")

    def _setup_osc_server(self):
        """Setup OSC server for energy feedback"""
        if not self.config.osc.enable_osc:
            return

        disp = dispatcher.Dispatcher()

        # Energy feedback from crowd monitoring system
        disp.map("/energy", self.handle_energy_change)
        disp.map("/movement", self.handle_energy_change)  # Alias

        # Manual controls
        disp.map("/bpm", self.handle_bpm_change)
        disp.map("/master_volume", self.handle_master_volume)
        disp.map("/status", lambda unused_addr: self._show_status())
        disp.map("/next_vocal", lambda unused_addr: self._force_vocal_change())

        try:
            self.osc_server = ThreadingOSCUDPServer((self.config.osc.host, self.osc_port), disp)
            osc_thread = threading.Thread(target=self.osc_server.serve_forever, daemon=True)
            osc_thread.start()
            print(f"📡 OSC server started on {self.config.osc.host}:{self.osc_port}")
        except Exception as e:
            print(f"❌ Failed to start OSC server: {e}")

    def _load_base_stems(self):
        """Load base stems (bass, drums, other) from compatible songs"""
        print("\n🎸 Loading base stems...")

        # Find songs close to target BPM
        compatible_songs = sorted(
            self.songs.items(),
            key=lambda x: abs(x[1].bpm - self.base_bpm)
        )[:10]

        base_types = ['bass', 'drums', 'other']

        for stem_type in base_types:
            for song_name, song in compatible_songs:
                if stem_type in song.stem_files:
                    stem_player = self._load_stem(song_name, stem_type)
                    if stem_player:
                        self.base_stems[stem_type] = stem_player
                        print(f"  ✅ {stem_type}: {song.name.split('(')[0].strip()} (BPM: {song.bpm:.0f})")
                        break

        print(f"✅ Loaded {len(self.base_stems)} base stems")

    def _load_stem(self, song_name: str, stem_type: str) -> Optional[StemPlayer]:
        """Load a single stem from a song"""
        if song_name not in self.songs:
            return None

        song = self.songs[song_name]

        if stem_type not in song.stem_files:
            return None

        try:
            # Load audio file
            audio_data, sr = librosa.load(
                song.stem_files[stem_type],
                sr=self.sample_rate,
                mono=True,
                dtype=np.float32
            )

            # Create stem player
            volume = self.config.mixing.stem_volumes.get(stem_type, 0.8)
            stem_player = StemPlayer(
                name=f"{song.name}_{stem_type}",
                audio_data=audio_data,
                sample_rate=sr,
                original_bpm=song.bpm,
                volume=volume
            )

            return stem_player

        except Exception as e:
            print(f"❌ Error loading {stem_type} from {song_name}: {e}")
            return None

    def _change_vocal(self, force: bool = False):
        """Change vocal track"""
        if not self.vocal_tracks:
            return

        # Check minimum duration
        time_since_change = time.time() - self.last_vocal_change
        if not force and time_since_change < self.min_vocal_duration:
            return

        # Find compatible vocals (similar BPM)
        compatible = []
        for song_name in self.vocal_tracks:
            song = self.songs[song_name]
            if abs(song.bpm - self.base_bpm) < self.base_bpm * 0.15:
                compatible.append(song_name)

        if not compatible:
            compatible = self.vocal_tracks.copy()

        # Select random vocal (avoid current)
        available = [s for s in compatible if s != self.current_vocal_song_name]
        if not available:
            available = compatible

        new_vocal_song_name = random.choice(available)

        # Load new vocal
        new_vocal = self._load_stem(new_vocal_song_name, 'vocals')
        if new_vocal:
            with self.settings_lock:
                self.current_vocal = new_vocal
                self.current_vocal_song_name = new_vocal_song_name

            self.last_vocal_change = time.time()
            self.vocal_repeat_count = 0

            song = self.songs[new_vocal_song_name]
            print(f"🎤 NEW VOCAL: {song.name.split('(')[0].strip()} (BPM: {song.bpm:.0f})")

    def _force_vocal_change(self):
        """Force immediate vocal change"""
        print("⚡ Forcing vocal change...")
        self._change_vocal(force=True)

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Real-time audio callback"""
        try:
            with self.settings_lock:
                current_bpm = self.base_bpm
                master_vol = self.master_volume
                base_stems = self.base_stems.copy()
                current_vocal = self.current_vocal

            # Mix base stems
            mixed_audio = np.zeros(frame_count, dtype=np.float32)

            for stem_player in base_stems.values():
                stem_samples = stem_player.get_samples(frame_count, current_bpm)
                mixed_audio += stem_samples

            # Add vocal if exists
            if current_vocal:
                vocal_samples = current_vocal.get_samples(frame_count, current_bpm)
                mixed_audio += vocal_samples

            # Apply master volume
            mixed_audio *= master_vol

            # Soft limiting to prevent clipping
            max_amp = np.max(np.abs(mixed_audio))
            if max_amp > 0.9:
                mixed_audio = np.tanh(mixed_audio / max_amp) * 0.9

            return (mixed_audio.astype(np.float32).tobytes(), pyaudio.paContinue)

        except Exception as e:
            print(f"❌ Audio callback error: {e}")
            return (np.zeros(frame_count, dtype=np.float32).tobytes(), pyaudio.paContinue)

    def _performance_loop(self):
        """Main performance loop - monitors energy and adapts"""
        print("\n⚡ ENERGY-RESPONSIVE PERFORMANCE LOOP STARTED")
        print("📊 Monitoring crowd energy...")

        last_status = time.time()

        while self.running:
            try:
                current_time = time.time()

                # Show periodic status
                if current_time - last_status > 30:
                    self._show_status()
                    last_status = current_time

                # Check energy and decide on vocal changes
                time_since_change = current_time - self.last_vocal_change
                time_stable = current_time - self.last_energy_change

                # Energy is LOW - change vocal to try something new
                if (self.current_energy < self.energy_threshold_low and
                    time_since_change > self.min_vocal_duration and
                    time_stable > self.energy_stability_time):

                    print(f"📉 LOW ENERGY ({self.current_energy:.2f}) - Trying new vocal...")
                    self._change_vocal()
                    self.last_energy_change = current_time

                # Energy is HIGH - keep or repeat current vocal
                elif self.current_energy > self.energy_threshold_high:
                    if self.vocal_repeat_count < self.max_vocal_repeats:
                        print(f"📈 HIGH ENERGY ({self.current_energy:.2f}) - Keeping vocal (repeat {self.vocal_repeat_count + 1})")
                        self.vocal_repeat_count += 1
                    else:
                        print(f"📈 HIGH ENERGY maintained - vocal repeated {self.max_vocal_repeats} times")
                    self.last_energy_change = current_time

                time.sleep(2.0)  # Check every 2 seconds

            except Exception as e:
                print(f"❌ Performance loop error: {e}")
                time.sleep(1.0)

    def _show_status(self):
        """Show current performance status"""
        print("\n🎭 PERFORMANCE STATUS")
        print("=" * 50)
        print(f"⚡ Current Energy: {self.current_energy:.2f}")
        print(f"🎵 Base BPM: {self.base_bpm:.1f}")
        print(f"🔊 Master Volume: {self.master_volume:.2f}")

        print(f"\n🎸 Base Stems (Stable):")
        for stem_type, stem_player in self.base_stems.items():
            status = "▶️" if stem_player.playing else "⏹️"
            print(f"  {status} {stem_type}: {stem_player.name}")

        print(f"\n🎤 Current Vocal:")
        if self.current_vocal_song_name:
            song = self.songs[self.current_vocal_song_name]
            print(f"  ▶️ {song.name.split('(')[0].strip()}")
            print(f"  📊 Repeat count: {self.vocal_repeat_count}/{self.max_vocal_repeats}")
        else:
            print("  (No vocal loaded)")

        time_since_change = time.time() - self.last_vocal_change
        print(f"\n⏱️ Time since vocal change: {time_since_change:.1f}s")
        print(f"📊 Energy thresholds: Low < {self.energy_threshold_low:.2f}, High > {self.energy_threshold_high:.2f}")
        print()

    # OSC Handlers
    def handle_energy_change(self, unused_addr, energy: float):
        """Handle energy feedback from crowd monitoring"""
        old_energy = self.current_energy
        self.current_energy = max(0.0, min(1.0, float(energy)))

        # Only print if significant change
        if abs(self.current_energy - old_energy) > 0.1:
            energy_emoji = "📉" if self.current_energy < self.energy_threshold_low else "📊" if self.current_energy < self.energy_threshold_high else "📈"
            print(f"{energy_emoji} Energy: {old_energy:.2f} → {self.current_energy:.2f}")

    def handle_bpm_change(self, unused_addr, bpm: float):
        """Handle BPM change"""
        bpm = max(60, min(200, bpm))
        with self.settings_lock:
            old_bpm = self.base_bpm
            self.base_bpm = bpm
        print(f"🎵 BPM: {old_bpm:.1f} → {bpm:.1f}")

    def handle_master_volume(self, unused_addr, volume: float):
        """Handle master volume change"""
        volume = max(0.0, min(1.0, volume))
        with self.settings_lock:
            self.master_volume = volume
        print(f"🔊 Master Volume: {volume:.2f}")

    def start(self):
        """Start the energy-responsive performance"""
        if self.running:
            print("⚠️ Already running!")
            return

        print("\n🚀 Starting Energy-Responsive Performance...")

        self.running = True

        # Start audio stream
        try:
            self.audio_stream = self.pyaudio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
            print(f"🔊 Audio stream started ({self.sample_rate} Hz)")
        except Exception as e:
            print(f"❌ Audio stream error: {e}")
            return

        # Load first vocal
        print("\n🎤 Loading initial vocal...")
        self._change_vocal(force=True)

        # Start monitoring loop
        self.performance_thread.start()

        print("\n🎉 PERFORMANCE IS LIVE!")
        print("\n🎭 CONTROLS:")
        print("OSC Messages (send to localhost:5005):")
        print("  /energy [0.0-1.0]      - Set crowd energy level")
        print("  /movement [0.0-1.0]    - Set crowd movement (alias)")
        print("  /bpm [value]           - Change base BPM")
        print("  /master_volume [0-1]   - Master volume")
        print("  /status                - Show status")
        print("  /next_vocal            - Force vocal change")
        print("\nCLI Commands:")
        print("  energy [0-1]  - Set energy")
        print("  bpm [value]   - Set BPM")
        print("  status        - Show status")
        print("  next          - Next vocal")
        print("  quit          - Exit")
        print()

        # CLI control
        while self.running:
            try:
                cmd = input("🎭 > ").strip().lower()
                if not cmd:
                    continue

                parts = cmd.split()
                command = parts[0]

                if command == "quit":
                    break
                elif command == "energy" and len(parts) == 2:
                    try:
                        energy = float(parts[1])
                        self.handle_energy_change(None, energy)
                    except ValueError:
                        print("❌ Invalid energy value")
                elif command == "bpm" and len(parts) == 2:
                    try:
                        bpm = float(parts[1])
                        self.handle_bpm_change(None, bpm)
                    except ValueError:
                        print("❌ Invalid BPM")
                elif command == "status":
                    self._show_status()
                elif command == "next":
                    self._force_vocal_change()
                else:
                    print("❌ Unknown command")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        self.stop()

    def stop(self):
        """Stop and cleanup"""
        print("\n🛑 Stopping Energy-Responsive Performance...")
        self.running = False

        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

        self.pyaudio.terminate()

        if self.osc_server:
            self.osc_server.shutdown()

        print("👋 Performance stopped!")


def main():
    performance = EnergyResponsivePerformance(
        base_bpm=120.0,
        auto_start=True
    )
    performance.start()


if __name__ == "__main__":
    print("🎭 Energy-Responsive Eurovision Performance")
    print("Direct audio playback with pyaudio/librosa")
    main()
