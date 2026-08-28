import json
import re

# Parse the JSON presets from user data
user_data_raw = '''
{
  "Cengklik": true, "Brimob01": true, "JurugTimur": true, "Sholikin01": true, "SekarpaceTimur": true,
  "Ngapeman01": true, "GenenganBarat": true, "JurugBarat": true, "Pajang": true, "GenenganSelatan": true,
  "JembatanTirtonadi": true, "PasarKembang": true, "RuasRingRoadBarat": true, "Kawatan": true, "Widuran": true,
  "CembenganUtara": true, "RingRoadBarat": true, "RingRoadTimur": true, "Ramayana": true, "Gilingan01": true,
  "FlyoverBarat": true, "Banjarsari": true, "FarokaTimur": true, "FarokaBarat": true, "FlyoverTimur": true,
  "UNS": true, "CembenganTimur": true, "UNSBarat": true, "CembenganSelatan": true, "CembenganBarat": true,
  "KlodranTimur": true, "SekarpaceUtara": true, "UNSTimur": true, "SekarpaceBarat": true, "BundaranTipes": true,
  "RingRoadSelatan": true, "RingRoadUtara": true, "GenenganUtara": true, "TuguWisnuUtara": true, "KertenUtara": true,
  "RuasRingRoadTimur": true, "Semanggi": true, "TuguWisnuTimur": true, "Klodran": true, "Mipitan": true,
  "DawungUtara": true, "Gemblegan": true, "KelurahanSumberSelatan": true, "KelurahanSumberBarat": true, "Gladag": true,
  "KelurahanSumberUtara": true, "Kabangan": true, "GendenganTimur": true, "Farokah": true, "LojiGandrung": true,
  "Sekarpace": true, "PasarPon01": true, "BalaiKota": true, "PGS": true, "KandangSapi": true,
  "Ursulin": true, "GembleganBarat": true, "PasarGede": true, "GembleganSelatan": true, "PanggungTimur": true,
  "GembleganTimur": true, "Cembengan": true, "GendenganBarat": true, "SMP18": true, "KelurahanSumberTimur": true,
  "OverpassSelatan": true, "OverpassBarat": true, "Kerten": true, "Rahayu01": true, "Sriwedari01": true,
  "Sraten": true, "RingRoad": true, "Ketandan": true, "Tipes": true, "Gendengan01": true,
  "VMSDPRD": true, "PanggungSelatan": true, "GembleganUtara": true, "PanggungUtara": true, "FajarIndahBarat": true,
  "TuguWisnu01": true, "FajarIndahUtara": true, "MijipinilihanLor": true, "PanggungBarat": true, "NgemplakUtara": true,
  "NgemplakTimur": true, "Jurug": true, "FajarIndahSelatan": true, "NgemplakSelatan": true, "NgemplakBarat": true,
  "KlodranBarat": true, "Mujahidin": true, "KelurahanSumber01": true, "FajarIndahTimur": true, "Makutho": true,
  "Balong": true, "BawahFlyoverPurwosari": true, "GondangWide": true, "ISIWide": true, "Balapan01": true,
  "PasarKliwon": true, "ISIPTZ": true, "GondangPTZ": true, "Agas": true, "SateSumber01": true,
  "WarungPelemTimur": true, "WarungPelemBarat": true, "Sangkrah": true, "Mojosongo": true, "Jongke": true,
  "Panggung": true, "BatuRono": true, "Tirtonadi01": true, "Purwosari": true, "Komplang01": true,
  "Baron": true, "WarungPelem": true, "GiriMulyo01": true, "Ngemplak": true, "FajarIndah": true,
  "GendenganUtara": true, "FlyOver": true, "OverpassManahan": true, "NononganWide": true, "GenenganTimur": true,
  "Nonongan": true, "RuasMakutho": true
}
'''

online_map = json.loads(user_data_raw)

# Read config.py
with open("backend/app/core/config.py", "r", encoding="utf-8") as f:
    content = f.read()

# Update CCTV_PRESETS in config.py
# Extract presets
# Format active ones first
def format_camel_to_title(name: str) -> str:
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1 \2', s)
    s = re.sub(r'(\D)(\d+)', r'\1 \2', s)
    return s.strip()

presets = []
for key in online_map.keys():
    title = format_camel_to_title(key)
    presets.append({
        "id": f"surakarta_{key.lower()}",
        "name": f"ATCS Surakarta — {title}",
        "location": f"{title}, Surakarta",
        "url": f"https://surakarta.atcsindonesia.info:8086/camera/{key}.flv"
    })

# Add synthetic fallback
presets.append({
    "id": "surakarta_demo",
    "name": "Mode Demo Offline",
    "location": "Offline Demo Stream",
    "url": "synthetic://demo"
})

new_config_code = f'''from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    PROJECT_NAME: str = "Smart Traffic Monitoring"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Video source: Live ATCS Surakarta FLV stream URL (Default: Balai Kota)
    VIDEO_STREAM_URL: str = "https://surakarta.atcsindonesia.info:8086/camera/BalaiKota.flv"
    FALLBACK_VIDEO_PATH: str = "sample_data/synthetic_traffic.mp4"
    ROI_PERSISTENCE_PATH: str = "default_roi.json"
    
    TARGET_FPS: int = 12
    STREAM_WIDTH: int = 640
    STREAM_HEIGHT: int = 360
    JPEG_QUALITY: int = 65
    
    # Tracking constants
    TTL_FRAME_PURGE: int = 60

    # Active Live CCTV Presets (ATCS Surakarta)
    CCTV_PRESETS: List[Dict[str, str]] = {json.dumps(presets, indent=4)}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = AppSettings()
'''

with open("backend/app/core/config.py", "w", encoding="utf-8") as f:
    f.write(new_config_code)

print(f"Successfully updated config.py with {len(presets)} active cameras!")
