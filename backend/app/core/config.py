from typing import List, Dict, Any
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
    CCTV_PRESETS: List[Dict[str, str]] = [
    {
        "id": "surakarta_pasar_klewer",
        "name": "ATCS Surakarta — Pasar Klewer",
        "location": "Pasar Klewer, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarKlewer.flv"
    },
    {
        "id": "surakarta_cengklik",
        "name": "ATCS Surakarta — Cengklik",
        "location": "Cengklik, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Cengklik.flv"
    },
    {
        "id": "surakarta_jurug_barat",
        "name": "ATCS Surakarta — Jurug Barat",
        "location": "Jurug Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/JurugBarat.flv"
    },
    {
        "id": "surakarta_jurug_timur",
        "name": "ATCS Surakarta — Jurug Timur",
        "location": "Jurug Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/JurugTimur.flv"
    },
    {
        "id": "surakarta_sholikin_01",
        "name": "ATCS Surakarta — Sholikin 01",
        "location": "Sholikin 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sholikin01.flv"
    },
    {
        "id": "surakarta_sekarpace_timur",
        "name": "ATCS Surakarta — Sekarpace Timur",
        "location": "Sekarpace Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SekarpaceTimur.flv"
    },
    {
        "id": "surakarta_widuran",
        "name": "ATCS Surakarta — Widuran",
        "location": "Widuran, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Widuran.flv"
    },
    {
        "id": "surakarta_pajang",
        "name": "ATCS Surakarta — Pajang",
        "location": "Pajang, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Pajang.flv"
    },
    {
        "id": "surakarta_kawatan",
        "name": "ATCS Surakarta — Kawatan",
        "location": "Kawatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Kawatan.flv"
    },
    {
        "id": "surakarta_ngapeman_01",
        "name": "ATCS Surakarta — Ngapeman 01",
        "location": "Ngapeman 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ngapeman01.flv"
    },
    {
        "id": "surakarta_pasar_kembang",
        "name": "ATCS Surakarta — Pasar Kembang",
        "location": "Pasar Kembang, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarKembang.flv"
    },
    {
        "id": "surakarta_genengan_selatan",
        "name": "ATCS Surakarta — Genengan Selatan",
        "location": "Genengan Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganSelatan.flv"
    },
    {
        "id": "surakarta_ring_road_barat",
        "name": "ATCS Surakarta — Ring Road Barat",
        "location": "Ring Road Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadBarat.flv"
    },
    {
        "id": "surakarta_genengan_barat",
        "name": "ATCS Surakarta — Genengan Barat",
        "location": "Genengan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganBarat.flv"
    },
    {
        "id": "surakarta_cembengan_selatan",
        "name": "ATCS Surakarta — Cembengan Selatan",
        "location": "Cembengan Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganSelatan.flv"
    },
    {
        "id": "surakarta_cembengan_timur",
        "name": "ATCS Surakarta — Cembengan Timur",
        "location": "Cembengan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganTimur.flv"
    },
    {
        "id": "surakarta_cembengan_utara",
        "name": "ATCS Surakarta — Cembengan Utara",
        "location": "Cembengan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganUtara.flv"
    },
    {
        "id": "surakarta_ruas_ring_road_barat",
        "name": "ATCS Surakarta — Ruas Ring Road Barat",
        "location": "Ruas Ring Road Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RuasRingRoadBarat.flv"
    },
    {
        "id": "surakarta_gilingan_01",
        "name": "ATCS Surakarta — Gilingan 01",
        "location": "Gilingan 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gilingan01.flv"
    },
    {
        "id": "surakarta_flyover_barat",
        "name": "ATCS Surakarta — Flyover Barat",
        "location": "Flyover Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FlyoverBarat.flv"
    },
    {
        "id": "surakarta_faroka_barat",
        "name": "ATCS Surakarta — Faroka Barat",
        "location": "Faroka Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FarokaBarat.flv"
    },
    {
        "id": "surakarta_faroka_timur",
        "name": "ATCS Surakarta — Faroka Timur",
        "location": "Faroka Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FarokaTimur.flv"
    },
    {
        "id": "surakarta_ring_road_timur",
        "name": "ATCS Surakarta — Ring Road Timur",
        "location": "Ring Road Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadTimur.flv"
    },
    {
        "id": "surakarta_uns",
        "name": "ATCS Surakarta — UNS",
        "location": "UNS, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/UNS.flv"
    },
    {
        "id": "surakarta_pasar_nusukan",
        "name": "ATCS Surakarta — Pasar Nusukan",
        "location": "Pasar Nusukan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarNusukan.flv"
    },
    {
        "id": "surakarta_flyover_timur",
        "name": "ATCS Surakarta — Flyover Timur",
        "location": "Flyover Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FlyoverTimur.flv"
    },
    {
        "id": "surakarta_uns_barat",
        "name": "ATCS Surakarta — UNS Barat",
        "location": "UNS Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/UNSBarat.flv"
    },
    {
        "id": "surakarta_sekarpace_barat",
        "name": "ATCS Surakarta — Sekarpace Barat",
        "location": "Sekarpace Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SekarpaceBarat.flv"
    },
    {
        "id": "surakarta_uns_timur",
        "name": "ATCS Surakarta — UNS Timur",
        "location": "UNS Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/UNSTimur.flv"
    },
    {
        "id": "surakarta_bundaran_tipes",
        "name": "ATCS Surakarta — Bundaran Tipes",
        "location": "Bundaran Tipes, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BundaranTipes.flv"
    },
    {
        "id": "surakarta_sekarpace_utara",
        "name": "ATCS Surakarta — Sekarpace Utara",
        "location": "Sekarpace Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SekarpaceUtara.flv"
    },
    {
        "id": "surakarta_ring_road_selatan",
        "name": "ATCS Surakarta — Ring Road Selatan",
        "location": "Ring Road Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadSelatan.flv"
    },
    {
        "id": "surakarta_ring_road_utara",
        "name": "ATCS Surakarta — Ring Road Utara",
        "location": "Ring Road Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadUtara.flv"
    },
    {
        "id": "surakarta_cembengan_barat",
        "name": "ATCS Surakarta — Cembengan Barat",
        "location": "Cembengan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganBarat.flv"
    },
    {
        "id": "surakarta_genengan_utara",
        "name": "ATCS Surakarta — Genengan Utara",
        "location": "Genengan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganUtara.flv"
    },
    {
        "id": "surakarta_kerten_utara",
        "name": "ATCS Surakarta — Kerten Utara",
        "location": "Kerten Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KertenUtara.flv"
    },
    {
        "id": "surakarta_tugu_wisnu_utara",
        "name": "ATCS Surakarta — Tugu Wisnu Utara",
        "location": "Tugu Wisnu Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuUtara.flv"
    },
    {
        "id": "surakarta_semanggi",
        "name": "ATCS Surakarta — Semanggi",
        "location": "Semanggi, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Semanggi.flv"
    },
    {
        "id": "surakarta_mipitan",
        "name": "ATCS Surakarta — Mipitan",
        "location": "Mipitan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Mipitan.flv"
    },
    {
        "id": "surakarta_ruas_ring_road_timur",
        "name": "ATCS Surakarta — Ruas Ring Road Timur",
        "location": "Ruas Ring Road Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RuasRingRoadTimur.flv"
    },
    {
        "id": "surakarta_kabangan",
        "name": "ATCS Surakarta — Kabangan",
        "location": "Kabangan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Kabangan.flv"
    },
    {
        "id": "surakarta_gladag",
        "name": "ATCS Surakarta — Gladag",
        "location": "Gladag, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gladag.flv"
    },
    {
        "id": "surakarta_tugu_wisnu_timur",
        "name": "ATCS Surakarta — Tugu Wisnu Timur",
        "location": "Tugu Wisnu Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuTimur.flv"
    },
    {
        "id": "surakarta_gemblegan",
        "name": "ATCS Surakarta — Gemblegan",
        "location": "Gemblegan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gemblegan.flv"
    },
    {
        "id": "surakarta_gendengan_timur",
        "name": "ATCS Surakarta — Gendengan Timur",
        "location": "Gendengan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GendenganTimur.flv"
    },
    {
        "id": "surakarta_sekarpace",
        "name": "ATCS Surakarta — Sekarpace",
        "location": "Sekarpace, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sekarpace.flv"
    },
    {
        "id": "surakarta_ramayana",
        "name": "ATCS Surakarta — Ramayana",
        "location": "Ramayana, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ramayana.flv"
    },
    {
        "id": "surakarta_dawung_utara",
        "name": "ATCS Surakarta — Dawung Utara",
        "location": "Dawung Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/DawungUtara.flv"
    },
    {
        "id": "surakarta_balai_kota",
        "name": "ATCS Surakarta — Balai Kota",
        "location": "Balai Kota, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BalaiKota.flv"
    },
    {
        "id": "surakarta_loji_gandrung",
        "name": "ATCS Surakarta — Loji Gandrung",
        "location": "Loji Gandrung, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/LojiGandrung.flv"
    },
    {
        "id": "surakarta_farokah",
        "name": "ATCS Surakarta — Farokah",
        "location": "Farokah, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Farokah.flv"
    },
    {
        "id": "surakarta_pasar_pon_01",
        "name": "ATCS Surakarta — Pasar Pon 01",
        "location": "Pasar Pon 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarPon01.flv"
    },
    {
        "id": "surakarta_ursulin",
        "name": "ATCS Surakarta — Ursulin",
        "location": "Ursulin, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ursulin.flv"
    },
    {
        "id": "surakarta_pgs",
        "name": "ATCS Surakarta — PGS",
        "location": "PGS, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PGS.flv"
    },
    {
        "id": "surakarta_pasar_gede",
        "name": "ATCS Surakarta — Pasar Gede",
        "location": "Pasar Gede, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarGede.flv"
    },
    {
        "id": "surakarta_kandang_sapi",
        "name": "ATCS Surakarta — Kandang Sapi",
        "location": "Kandang Sapi, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KandangSapi.flv"
    },
    {
        "id": "surakarta_gendengan_barat",
        "name": "ATCS Surakarta — Gendengan Barat",
        "location": "Gendengan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GendenganBarat.flv"
    },
    {
        "id": "surakarta_gemblegan_barat",
        "name": "ATCS Surakarta — Gemblegan Barat",
        "location": "Gemblegan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganBarat.flv"
    },
    {
        "id": "surakarta_gemblegan_timur",
        "name": "ATCS Surakarta — Gemblegan Timur",
        "location": "Gemblegan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganTimur.flv"
    },
    {
        "id": "surakarta_jembatan_tirtonadi",
        "name": "ATCS Surakarta — Jembatan Tirtonadi",
        "location": "Jembatan Tirtonadi, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/JembatanTirtonadi.flv"
    },
    {
        "id": "surakarta_overpass_barat",
        "name": "ATCS Surakarta — Overpass Barat",
        "location": "Overpass Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/OverpassBarat.flv"
    },
    {
        "id": "surakarta_overpass_selatan",
        "name": "ATCS Surakarta — Overpass Selatan",
        "location": "Overpass Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/OverpassSelatan.flv"
    },
    {
        "id": "surakarta_cembengan",
        "name": "ATCS Surakarta — Cembengan",
        "location": "Cembengan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Cembengan.flv"
    },
    {
        "id": "surakarta_panggung_timur",
        "name": "ATCS Surakarta — Panggung Timur",
        "location": "Panggung Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungTimur.flv"
    },
    {
        "id": "surakarta_gemblegan_selatan",
        "name": "ATCS Surakarta — Gemblegan Selatan",
        "location": "Gemblegan Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganSelatan.flv"
    },
    {
        "id": "surakarta_smp_18",
        "name": "ATCS Surakarta — SMP 18",
        "location": "SMP 18, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SMP18.flv"
    },
    {
        "id": "surakarta_tipes",
        "name": "ATCS Surakarta — Tipes",
        "location": "Tipes, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Tipes.flv"
    },
    {
        "id": "surakarta_sriwedari_01",
        "name": "ATCS Surakarta — Sriwedari 01",
        "location": "Sriwedari 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sriwedari01.flv"
    },
    {
        "id": "surakarta_ruas_makutho",
        "name": "ATCS Surakarta — Ruas Makutho",
        "location": "Ruas Makutho, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RuasMakutho.flv"
    },
    {
        "id": "surakarta_pasar_kliwon",
        "name": "ATCS Surakarta — Pasar Kliwon",
        "location": "Pasar Kliwon, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarKliwon.flv"
    },
    {
        "id": "surakarta_kerten",
        "name": "ATCS Surakarta — Kerten",
        "location": "Kerten, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Kerten.flv"
    },
    {
        "id": "surakarta_rahayu_01",
        "name": "ATCS Surakarta — Rahayu 01",
        "location": "Rahayu 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Rahayu01.flv"
    },
    {
        "id": "surakarta_sraten",
        "name": "ATCS Surakarta — Sraten",
        "location": "Sraten, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sraten.flv"
    },
    {
        "id": "surakarta_gendengan_01",
        "name": "ATCS Surakarta — Gendengan 01",
        "location": "Gendengan 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gendengan01.flv"
    },
    {
        "id": "surakarta_banjarsari",
        "name": "ATCS Surakarta — Banjarsari",
        "location": "Banjarsari, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Banjarsari.flv"
    },
    {
        "id": "surakarta_vmsdprd",
        "name": "ATCS Surakarta — VMSDPRD",
        "location": "VMSDPRD, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/VMSDPRD.flv"
    },
    {
        "id": "surakarta_panggung_selatan",
        "name": "ATCS Surakarta — Panggung Selatan",
        "location": "Panggung Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungSelatan.flv"
    },
    {
        "id": "surakarta_panggung_barat",
        "name": "ATCS Surakarta — Panggung Barat",
        "location": "Panggung Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungBarat.flv"
    },
    {
        "id": "surakarta_tugu_wisnu_01",
        "name": "ATCS Surakarta — Tugu Wisnu 01",
        "location": "Tugu Wisnu 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/TuguWisnu01.flv"
    },
    {
        "id": "surakarta_ring_road",
        "name": "ATCS Surakarta — Ring Road",
        "location": "Ring Road, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoad.flv"
    },
    {
        "id": "surakarta_panggung_utara",
        "name": "ATCS Surakarta — Panggung Utara",
        "location": "Panggung Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungUtara.flv"
    },
    {
        "id": "surakarta_mijipinilihan_lor",
        "name": "ATCS Surakarta — Mijipinilihan Lor",
        "location": "Mijipinilihan Lor, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/MijipinilihanLor.flv"
    },
    {
        "id": "surakarta_fajar_indah_barat",
        "name": "ATCS Surakarta — Fajar Indah Barat",
        "location": "Fajar Indah Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahBarat.flv"
    },
    {
        "id": "surakarta_fajar_indah_utara",
        "name": "ATCS Surakarta — Fajar Indah Utara",
        "location": "Fajar Indah Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahUtara.flv"
    },
    {
        "id": "surakarta_ketandan",
        "name": "ATCS Surakarta — Ketandan",
        "location": "Ketandan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ketandan.flv"
    },
    {
        "id": "surakarta_ngemplak_timur",
        "name": "ATCS Surakarta — Ngemplak Timur",
        "location": "Ngemplak Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakTimur.flv"
    },
    {
        "id": "surakarta_gemblegan_utara",
        "name": "ATCS Surakarta — Gemblegan Utara",
        "location": "Gemblegan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganUtara.flv"
    },
    {
        "id": "surakarta_ngemplak_utara",
        "name": "ATCS Surakarta — Ngemplak Utara",
        "location": "Ngemplak Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakUtara.flv"
    },
    {
        "id": "surakarta_ngemplak_barat",
        "name": "ATCS Surakarta — Ngemplak Barat",
        "location": "Ngemplak Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakBarat.flv"
    },
    {
        "id": "surakarta_fajar_indah_timur",
        "name": "ATCS Surakarta — Fajar Indah Timur",
        "location": "Fajar Indah Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahTimur.flv"
    },
    {
        "id": "surakarta_jurug",
        "name": "ATCS Surakarta — Jurug",
        "location": "Jurug, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Jurug.flv"
    },
    {
        "id": "surakarta_fajar_indah_selatan",
        "name": "ATCS Surakarta — Fajar Indah Selatan",
        "location": "Fajar Indah Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahSelatan.flv"
    },
    {
        "id": "surakarta_ngemplak_selatan",
        "name": "ATCS Surakarta — Ngemplak Selatan",
        "location": "Ngemplak Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakSelatan.flv"
    },
    {
        "id": "surakarta_bawah_flyover_purwosari",
        "name": "ATCS Surakarta — Bawah Flyover Purwosari",
        "location": "Bawah Flyover Purwosari, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BawahFlyoverPurwosari.flv"
    },
    {
        "id": "surakarta_sangkrah",
        "name": "ATCS Surakarta — Sangkrah",
        "location": "Sangkrah, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sangkrah.flv"
    },
    {
        "id": "surakarta_balong",
        "name": "ATCS Surakarta — Balong",
        "location": "Balong, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Balong.flv"
    },
    {
        "id": "surakarta_gondang_wide",
        "name": "ATCS Surakarta — Gondang Wide",
        "location": "Gondang Wide, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GondangWide.flv"
    },
    {
        "id": "surakarta_gondang_ptz",
        "name": "ATCS Surakarta — Gondang PTZ",
        "location": "Gondang PTZ, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GondangPTZ.flv"
    },
    {
        "id": "surakarta_isi_wide",
        "name": "ATCS Surakarta — ISI Wide",
        "location": "ISI Wide, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/ISIWide.flv"
    },
    {
        "id": "surakarta_isiptz",
        "name": "ATCS Surakarta — ISIPTZ",
        "location": "ISIPTZ, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/ISIPTZ.flv"
    },
    {
        "id": "surakarta_warung_pelem_barat",
        "name": "ATCS Surakarta — Warung Pelem Barat",
        "location": "Warung Pelem Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/WarungPelemBarat.flv"
    },
    {
        "id": "surakarta_warung_pelem_timur",
        "name": "ATCS Surakarta — Warung Pelem Timur",
        "location": "Warung Pelem Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/WarungPelemTimur.flv"
    },
    {
        "id": "surakarta_agas",
        "name": "ATCS Surakarta — Agas",
        "location": "Agas, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Agas.flv"
    },
    {
        "id": "surakarta_makutho",
        "name": "ATCS Surakarta — Makutho",
        "location": "Makutho, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Makutho.flv"
    },
    {
        "id": "surakarta_balapan_01",
        "name": "ATCS Surakarta — Balapan 01",
        "location": "Balapan 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv"
    },
    {
        "id": "surakarta_mojosongo",
        "name": "ATCS Surakarta — Mojosongo",
        "location": "Mojosongo, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Mojosongo.flv"
    },
    {
        "id": "surakarta_jongke",
        "name": "ATCS Surakarta — Jongke",
        "location": "Jongke, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Jongke.flv"
    },
    {
        "id": "surakarta_panggung",
        "name": "ATCS Surakarta — Panggung",
        "location": "Panggung, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Panggung.flv"
    },
    {
        "id": "surakarta_tirtonadi_01",
        "name": "ATCS Surakarta — Tirtonadi 01",
        "location": "Tirtonadi 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Tirtonadi01.flv"
    },
    {
        "id": "surakarta_purwosari",
        "name": "ATCS Surakarta — Purwosari",
        "location": "Purwosari, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Purwosari.flv"
    },
    {
        "id": "surakarta_batu_rono",
        "name": "ATCS Surakarta — Batu Rono",
        "location": "Batu Rono, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BatuRono.flv"
    },
    {
        "id": "surakarta_baron",
        "name": "ATCS Surakarta — Baron",
        "location": "Baron, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Baron.flv"
    },
    {
        "id": "surakarta_warung_pelem",
        "name": "ATCS Surakarta — Warung Pelem",
        "location": "Warung Pelem, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/WarungPelem.flv"
    },
    {
        "id": "surakarta_giri_mulyo_01",
        "name": "ATCS Surakarta — Giri Mulyo 01",
        "location": "Giri Mulyo 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GiriMulyo01.flv"
    },
    {
        "id": "surakarta_gading",
        "name": "ATCS Surakarta — Gading",
        "location": "Gading, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gading.flv"
    },
    {
        "id": "surakarta_fajar_indah",
        "name": "ATCS Surakarta — Fajar Indah",
        "location": "Fajar Indah, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndah.flv"
    },
    {
        "id": "surakarta_ngemplak",
        "name": "ATCS Surakarta — Ngemplak",
        "location": "Ngemplak, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ngemplak.flv"
    },
    {
        "id": "surakarta_overpass_manahan",
        "name": "ATCS Surakarta — Overpass Manahan",
        "location": "Overpass Manahan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/OverpassManahan.flv"
    },
    {
        "id": "surakarta_genengan_timur",
        "name": "ATCS Surakarta — Genengan Timur",
        "location": "Genengan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganTimur.flv"
    },
    {
        "id": "surakarta_pengadilan_sriwedari",
        "name": "ATCS Surakarta — Pengadilan Sriwedari",
        "location": "Pengadilan Sriwedari, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PengadilanSriwedari.flv"
    },
    {
        "id": "surakarta_gendengan_utara",
        "name": "ATCS Surakarta — Gendengan Utara",
        "location": "Gendengan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GendenganUtara.flv"
    },
    {
        "id": "surakarta_sekip",
        "name": "ATCS Surakarta — Sekip",
        "location": "Sekip, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sekip.flv"
    },
    {
        "id": "surakarta_tugu_wisnu_selatan",
        "name": "ATCS Surakarta — Tugu Wisnu Selatan",
        "location": "Tugu Wisnu Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuSelatan.flv"
    },
    {
        "id": "surakarta_fly_over",
        "name": "ATCS Surakarta — Fly Over",
        "location": "Fly Over, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FlyOver.flv"
    },
    {
        "id": "surakarta_pasar_nongko",
        "name": "ATCS Surakarta — Pasar Nongko",
        "location": "Pasar Nongko, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarNongko.flv"
    },
    {
        "id": "surakarta_pasar_legi",
        "name": "ATCS Surakarta — Pasar Legi",
        "location": "Pasar Legi, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarLegi.flv"
    },
    {
        "id": "surakarta_singosaren",
        "name": "ATCS Surakarta — Singosaren",
        "location": "Singosaren, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Singosaren.flv"
    },
    {
        "id": "surakarta_timuran",
        "name": "ATCS Surakarta — Timuran",
        "location": "Timuran, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Timuran.flv"
    },
    {
        "id": "surakarta_gedung_serbaguna_pucangsawit",
        "name": "ATCS Surakarta — Gedung Serbaguna Pucangsawit",
        "location": "Gedung Serbaguna Pucangsawit, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GedungSerbagunaPucangsawit.flv"
    },
    {
        "id": "surakarta_dawung_selatan",
        "name": "ATCS Surakarta — Dawung Selatan",
        "location": "Dawung Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/DawungSelatan.flv"
    },
    {
        "id": "surakarta_jembatan_mojo",
        "name": "ATCS Surakarta — Jembatan Mojo",
        "location": "Jembatan Mojo, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/JembatanMojo.flv"
    },
    {
        "id": "surakarta_juanda",
        "name": "ATCS Surakarta — Juanda",
        "location": "Juanda, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Juanda.flv"
    },
    {
        "id": "surakarta_masjid_agung",
        "name": "ATCS Surakarta — Masjid Agung",
        "location": "Masjid Agung, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/MasjidAgung.flv"
    },
    {
        "id": "surakarta_mlipahan",
        "name": "ATCS Surakarta — Mlipahan",
        "location": "Mlipahan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Mlipahan.flv"
    },
    {
        "id": "surakarta_pasar_beling",
        "name": "ATCS Surakarta — Pasar Beling",
        "location": "Pasar Beling, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarBeling.flv"
    },
    {
        "id": "surakarta_pasark_kliwon",
        "name": "ATCS Surakarta — Pasark Kliwon",
        "location": "Pasark Kliwon, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarkKliwon.flv"
    },
    {
        "id": "surakarta_genengan",
        "name": "ATCS Surakarta — Genengan",
        "location": "Genengan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Genengan.flv"
    },
    {
        "id": "surakarta_dprd",
        "name": "ATCS Surakarta — DPRD",
        "location": "DPRD, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/DPRD.flv"
    },
    {
        "id": "surakarta_kleco",
        "name": "ATCS Surakarta — Kleco",
        "location": "Kleco, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Kleco.flv"
    },
    {
        "id": "surakarta_spbu_pucangsawit",
        "name": "ATCS Surakarta — SPBU Pucangsawit",
        "location": "SPBU Pucangsawit, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SPBUPucangsawit.flv"
    },
    {
        "id": "surakarta_sudirman",
        "name": "ATCS Surakarta — Sudirman",
        "location": "Sudirman, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sudirman.flv"
    },
    {
        "id": "surakarta_nonongan",
        "name": "ATCS Surakarta — Nonongan",
        "location": "Nonongan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Nonongan.flv"
    },
    {
        "id": "surakarta_nonongan_wide",
        "name": "ATCS Surakarta — Nonongan Wide",
        "location": "Nonongan Wide, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NononganWide.flv"
    },
    {
        "id": "surakarta_brimob_01",
        "name": "ATCS Surakarta — Brimob 01",
        "location": "Brimob 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Brimob01.flv"
    },
    {
        "id": "surakarta_kelurahan_sumber_01",
        "name": "ATCS Surakarta — Kelurahan Sumber 01",
        "location": "Kelurahan Sumber 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KelurahanSumber01.flv"
    },
    {
        "id": "surakarta_klodran",
        "name": "ATCS Surakarta — Klodran",
        "location": "Klodran, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Klodran.flv"
    },
    {
        "id": "surakarta_sate_sumber_01",
        "name": "ATCS Surakarta — Sate Sumber 01",
        "location": "Sate Sumber 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SateSumber01.flv"
    },
    {
        "id": "surakarta_palang_joglo",
        "name": "ATCS Surakarta — Palang Joglo",
        "location": "Palang Joglo, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PalangJoglo.flv"
    },
    {
        "id": "surakarta_mujahidin",
        "name": "ATCS Surakarta — Mujahidin",
        "location": "Mujahidin, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Mujahidin.flv"
    },
    {
        "id": "surakarta_bundaran_baron",
        "name": "ATCS Surakarta — Bundaran Baron",
        "location": "Bundaran Baron, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BundaranBaron.flv"
    },
    {
        "id": "synthetic_loop",
        "name": "Synthetic Traffic Simulator (In-Memory Demo)",
        "location": "Simulasi Lalu Lintas Dua Arah",
        "url": "synthetic://traffic_simulation"
    }
]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = AppSettings()
