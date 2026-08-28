import re
import json

urls_raw = """
https://surakarta.atcsindonesia.info:8086/camera/PasarKlewer.flv
https://surakarta.atcsindonesia.info:8086/camera/Cengklik.flv
https://surakarta.atcsindonesia.info:8086/camera/JurugBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/JurugTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/Sholikin01.flv
https://surakarta.atcsindonesia.info:8086/camera/SekarpaceTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/Widuran.flv
https://surakarta.atcsindonesia.info:8086/camera/Pajang.flv
https://surakarta.atcsindonesia.info:8086/camera/Kawatan.flv
https://surakarta.atcsindonesia.info:8086/camera/Ngapeman01.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarKembang.flv
https://surakarta.atcsindonesia.info:8086/camera/GenenganSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/RingRoadBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/GenenganBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/CembenganSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/CembenganTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/CembenganUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/RuasRingRoadBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/Gilingan01.flv
https://surakarta.atcsindonesia.info:8086/camera/FlyoverBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/FarokaBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/FarokaTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/RingRoadTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/UNS.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarNusukan.flv
https://surakarta.atcsindonesia.info:8086/camera/FlyoverTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/UNSBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/SekarpaceBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/UNSTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/BundaranTipes.flv
https://surakarta.atcsindonesia.info:8086/camera/SekarpaceUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/RingRoadSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/RingRoadUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/CembenganBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/GenenganUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/KertenUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/Semanggi.flv
https://surakarta.atcsindonesia.info:8086/camera/Mipitan.flv
https://surakarta.atcsindonesia.info:8086/camera/RuasRingRoadTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/Kabangan.flv
https://surakarta.atcsindonesia.info:8086/camera/Gladag.flv
https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/Gemblegan.flv
https://surakarta.atcsindonesia.info:8086/camera/GendenganTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/Sekarpace.flv
https://surakarta.atcsindonesia.info:8086/camera/Ramayana.flv
https://surakarta.atcsindonesia.info:8086/camera/DawungUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/BalaiKota.flv
https://surakarta.atcsindonesia.info:8086/camera/LojiGandrung.flv
https://surakarta.atcsindonesia.info:8086/camera/Farokah.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarPon01.flv
https://surakarta.atcsindonesia.info:8086/camera/Ursulin.flv
https://surakarta.atcsindonesia.info:8086/camera/PGS.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarGede.flv
https://surakarta.atcsindonesia.info:8086/camera/KandangSapi.flv
https://surakarta.atcsindonesia.info:8086/camera/GendenganBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/GembleganBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/GembleganTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/JembatanTirtonadi.flv
https://surakarta.atcsindonesia.info:8086/camera/OverpassBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/OverpassSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/Cembengan.flv
https://surakarta.atcsindonesia.info:8086/camera/PanggungTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/GembleganSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/SMP18.flv
https://surakarta.atcsindonesia.info:8086/camera/Tipes.flv
https://surakarta.atcsindonesia.info:8086/camera/Sriwedari01.flv
https://surakarta.atcsindonesia.info:8086/camera/RuasMakutho.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarKliwon.flv
https://surakarta.atcsindonesia.info:8086/camera/Kerten.flv
https://surakarta.atcsindonesia.info:8086/camera/Rahayu01.flv
https://surakarta.atcsindonesia.info:8086/camera/Sraten.flv
https://surakarta.atcsindonesia.info:8086/camera/Gendengan01.flv
https://surakarta.atcsindonesia.info:8086/camera/Banjarsari.flv
https://surakarta.atcsindonesia.info:8086/camera/VMSDPRD.flv
https://surakarta.atcsindonesia.info:8086/camera/PanggungSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/PanggungBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/TuguWisnu01.flv
https://surakarta.atcsindonesia.info:8086/camera/RingRoad.flv
https://surakarta.atcsindonesia.info:8086/camera/PanggungUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/MijipinilihanLor.flv
https://surakarta.atcsindonesia.info:8086/camera/FajarIndahBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/FajarIndahUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/Ketandan.flv
https://surakarta.atcsindonesia.info:8086/camera/NgemplakTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/GembleganUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/NgemplakUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/NgemplakBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/FajarIndahTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/Jurug.flv
https://surakarta.atcsindonesia.info:8086/camera/FajarIndahSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/NgemplakSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/BawahFlyoverPurwosari.flv
https://surakarta.atcsindonesia.info:8086/camera/Sangkrah.flv
https://surakarta.atcsindonesia.info:8086/camera/Balong.flv
https://surakarta.atcsindonesia.info:8086/camera/GondangWide.flv
https://surakarta.atcsindonesia.info:8086/camera/GondangPTZ.flv
https://surakarta.atcsindonesia.info:8086/camera/ISIWide.flv
https://surakarta.atcsindonesia.info:8086/camera/ISIPTZ.flv
https://surakarta.atcsindonesia.info:8086/camera/WarungPelemBarat.flv
https://surakarta.atcsindonesia.info:8086/camera/WarungPelemTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/Agas.flv
https://surakarta.atcsindonesia.info:8086/camera/Makutho.flv
https://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv
https://surakarta.atcsindonesia.info:8086/camera/Mojosongo.flv
https://surakarta.atcsindonesia.info:8086/camera/Jongke.flv
https://surakarta.atcsindonesia.info:8086/camera/Panggung.flv
https://surakarta.atcsindonesia.info:8086/camera/Tirtonadi01.flv
https://surakarta.atcsindonesia.info:8086/camera/Purwosari.flv
https://surakarta.atcsindonesia.info:8086/camera/BatuRono.flv
https://surakarta.atcsindonesia.info:8086/camera/Baron.flv
https://surakarta.atcsindonesia.info:8086/camera/WarungPelem.flv
https://surakarta.atcsindonesia.info:8086/camera/GiriMulyo01.flv
https://surakarta.atcsindonesia.info:8086/camera/Gading.flv
https://surakarta.atcsindonesia.info:8086/camera/FajarIndah.flv
https://surakarta.atcsindonesia.info:8086/camera/Ngemplak.flv
https://surakarta.atcsindonesia.info:8086/camera/OverpassManahan.flv
https://surakarta.atcsindonesia.info:8086/camera/GenenganTimur.flv
https://surakarta.atcsindonesia.info:8086/camera/PengadilanSriwedari.flv
https://surakarta.atcsindonesia.info:8086/camera/GendenganUtara.flv
https://surakarta.atcsindonesia.info:8086/camera/Sekip.flv
https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/FlyOver.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarNongko.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarLegi.flv
https://surakarta.atcsindonesia.info:8086/camera/Singosaren.flv
https://surakarta.atcsindonesia.info:8086/camera/Timuran.flv
https://surakarta.atcsindonesia.info:8086/camera/GedungSerbagunaPucangsawit.flv
https://surakarta.atcsindonesia.info:8086/camera/DawungSelatan.flv
https://surakarta.atcsindonesia.info:8086/camera/JembatanMojo.flv
https://surakarta.atcsindonesia.info:8086/camera/Juanda.flv
https://surakarta.atcsindonesia.info:8086/camera/MasjidAgung.flv
https://surakarta.atcsindonesia.info:8086/camera/Mlipahan.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarBeling.flv
https://surakarta.atcsindonesia.info:8086/camera/PasarkKliwon.flv
https://surakarta.atcsindonesia.info:8086/camera/Genengan.flv
https://surakarta.atcsindonesia.info:8086/camera/DPRD.flv
https://surakarta.atcsindonesia.info:8086/camera/Kleco.flv
https://surakarta.atcsindonesia.info:8086/camera/SPBUPucangsawit.flv
https://surakarta.atcsindonesia.info:8086/camera/Sudirman.flv
https://surakarta.atcsindonesia.info:8086/camera/Nonongan.flv
https://surakarta.atcsindonesia.info:8086/camera/NononganWide.flv
https://surakarta.atcsindonesia.info:8086/camera/Brimob01.flv
https://surakarta.atcsindonesia.info:8086/camera/KelurahanSumber01.flv
https://surakarta.atcsindonesia.info:8086/camera/Klodran.flv
https://surakarta.atcsindonesia.info:8086/camera/SateSumber01.flv
https://surakarta.atcsindonesia.info:8086/camera/PalangJoglo.flv
https://surakarta.atcsindonesia.info:8086/camera/Mujahidin.flv
https://surakarta.atcsindonesia.info:8086/camera/BundaranBaron.flv
"""

def format_name(raw_name):
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', raw_name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1 \2', s)
    s = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', s)
    s = s.replace('U N S', 'UNS').replace('P G S', 'PGS').replace('V M S', 'VMS').replace('D P R D', 'DPRD')
    s = s.replace('S M P', 'SMP').replace('P T Z', 'PTZ').replace('I S I', 'ISI').replace('S P B U', 'SPBU')
    return s.strip()

presets = []
seen = set()
for line in urls_raw.strip().splitlines():
    u = line.strip()
    if not u or u in seen:
        continue
    seen.add(u)
    raw_name = u.split('/')[-1].replace('.flv', '')
    human_name = format_name(raw_name)
    preset_id = re.sub(r'[^a-z0-9_]', '_', human_name.lower().replace(' ', '_'))
    presets.append({
        'id': f'surakarta_{preset_id}',
        'name': f'ATCS Surakarta — {human_name}',
        'location': f'{human_name}, Surakarta',
        'url': u
    })

presets.append({
    'id': 'synthetic_loop',
    'name': 'Synthetic Traffic Simulator (In-Memory Demo)',
    'location': 'Simulasi Lalu Lintas Dua Arah',
    'url': 'synthetic://traffic_simulation'
})

presets_repr = json.dumps(presets, indent=4, ensure_ascii=False)

content = '''from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    PROJECT_NAME: str = "Smart Traffic Monitoring"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Video source: Live ATCS Surakarta FLV stream URL or local fallback
    VIDEO_STREAM_URL: str = "https://surakarta.atcsindonesia.info:8086/camera/BalaiKota.flv"
    FALLBACK_VIDEO_PATH: str = "sample_data/synthetic_traffic.mp4"
    ROI_PERSISTENCE_PATH: str = "default_roi.json"
    
    TARGET_FPS: int = 12
    STREAM_WIDTH: int = 640
    STREAM_HEIGHT: int = 360
    JPEG_QUALITY: int = 65
    
    # Tracking constants
    TTL_FRAME_PURGE: int = 60

    # 150 Pre-configured CCTV Presets (ATCS Surakarta & Fallback)
    CCTV_PRESETS: List[Dict[str, str]] = ''' + presets_repr + '''
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = AppSettings()
'''

with open('backend/app/core/config.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated backend/app/core/config.py with {len(presets)} presets successfully.")
