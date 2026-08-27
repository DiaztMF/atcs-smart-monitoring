from typing import List, Dict, Any
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
    CCTV_PRESETS: List[Dict[str, str]] = [
    {
        "id": "surakarta_cengklik",
        "name": "ATCS Surakarta \u2014 Cengklik",
        "location": "Cengklik, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Cengklik.flv"
    },
    {
        "id": "surakarta_brimob01",
        "name": "ATCS Surakarta \u2014 Brimob 01",
        "location": "Brimob 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Brimob01.flv"
    },
    {
        "id": "surakarta_jurugtimur",
        "name": "ATCS Surakarta \u2014 Jurug Timur",
        "location": "Jurug Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/JurugTimur.flv"
    },
    {
        "id": "surakarta_sholikin01",
        "name": "ATCS Surakarta \u2014 Sholikin 01",
        "location": "Sholikin 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sholikin01.flv"
    },
    {
        "id": "surakarta_sekarpacetimur",
        "name": "ATCS Surakarta \u2014 Sekarpace Timur",
        "location": "Sekarpace Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SekarpaceTimur.flv"
    },
    {
        "id": "surakarta_ngapeman01",
        "name": "ATCS Surakarta \u2014 Ngapeman 01",
        "location": "Ngapeman 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ngapeman01.flv"
    },
    {
        "id": "surakarta_genenganbarat",
        "name": "ATCS Surakarta \u2014 Genengan Barat",
        "location": "Genengan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganBarat.flv"
    },
    {
        "id": "surakarta_jurugbarat",
        "name": "ATCS Surakarta \u2014 Jurug Barat",
        "location": "Jurug Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/JurugBarat.flv"
    },
    {
        "id": "surakarta_pajang",
        "name": "ATCS Surakarta \u2014 Pajang",
        "location": "Pajang, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Pajang.flv"
    },
    {
        "id": "surakarta_genenganselatan",
        "name": "ATCS Surakarta \u2014 Genengan Selatan",
        "location": "Genengan Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganSelatan.flv"
    },
    {
        "id": "surakarta_jembatantirtonadi",
        "name": "ATCS Surakarta \u2014 Jembatan Tirtonadi",
        "location": "Jembatan Tirtonadi, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/JembatanTirtonadi.flv"
    },
    {
        "id": "surakarta_pasarkembang",
        "name": "ATCS Surakarta \u2014 Pasar Kembang",
        "location": "Pasar Kembang, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarKembang.flv"
    },
    {
        "id": "surakarta_ruasringroadbarat",
        "name": "ATCS Surakarta \u2014 Ruas Ring Road Barat",
        "location": "Ruas Ring Road Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RuasRingRoadBarat.flv"
    },
    {
        "id": "surakarta_kawatan",
        "name": "ATCS Surakarta \u2014 Kawatan",
        "location": "Kawatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Kawatan.flv"
    },
    {
        "id": "surakarta_widuran",
        "name": "ATCS Surakarta \u2014 Widuran",
        "location": "Widuran, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Widuran.flv"
    },
    {
        "id": "surakarta_cembenganutara",
        "name": "ATCS Surakarta \u2014 Cembengan Utara",
        "location": "Cembengan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganUtara.flv"
    },
    {
        "id": "surakarta_ringroadbarat",
        "name": "ATCS Surakarta \u2014 Ring Road Barat",
        "location": "Ring Road Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadBarat.flv"
    },
    {
        "id": "surakarta_ringroadtimur",
        "name": "ATCS Surakarta \u2014 Ring Road Timur",
        "location": "Ring Road Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadTimur.flv"
    },
    {
        "id": "surakarta_ramayana",
        "name": "ATCS Surakarta \u2014 Ramayana",
        "location": "Ramayana, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ramayana.flv"
    },
    {
        "id": "surakarta_gilingan01",
        "name": "ATCS Surakarta \u2014 Gilingan 01",
        "location": "Gilingan 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gilingan01.flv"
    },
    {
        "id": "surakarta_flyoverbarat",
        "name": "ATCS Surakarta \u2014 Flyover Barat",
        "location": "Flyover Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FlyoverBarat.flv"
    },
    {
        "id": "surakarta_banjarsari",
        "name": "ATCS Surakarta \u2014 Banjarsari",
        "location": "Banjarsari, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Banjarsari.flv"
    },
    {
        "id": "surakarta_farokatimur",
        "name": "ATCS Surakarta \u2014 Faroka Timur",
        "location": "Faroka Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FarokaTimur.flv"
    },
    {
        "id": "surakarta_farokabarat",
        "name": "ATCS Surakarta \u2014 Faroka Barat",
        "location": "Faroka Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FarokaBarat.flv"
    },
    {
        "id": "surakarta_flyovertimur",
        "name": "ATCS Surakarta \u2014 Flyover Timur",
        "location": "Flyover Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FlyoverTimur.flv"
    },
    {
        "id": "surakarta_uns",
        "name": "ATCS Surakarta \u2014 UNS",
        "location": "UNS, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/UNS.flv"
    },
    {
        "id": "surakarta_cembengantimur",
        "name": "ATCS Surakarta \u2014 Cembengan Timur",
        "location": "Cembengan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganTimur.flv"
    },
    {
        "id": "surakarta_unsbarat",
        "name": "ATCS Surakarta \u2014 UNS Barat",
        "location": "UNS Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/UNSBarat.flv"
    },
    {
        "id": "surakarta_cembenganselatan",
        "name": "ATCS Surakarta \u2014 Cembengan Selatan",
        "location": "Cembengan Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganSelatan.flv"
    },
    {
        "id": "surakarta_cembenganbarat",
        "name": "ATCS Surakarta \u2014 Cembengan Barat",
        "location": "Cembengan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/CembenganBarat.flv"
    },
    {
        "id": "surakarta_klodrantimur",
        "name": "ATCS Surakarta \u2014 Klodran Timur",
        "location": "Klodran Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KlodranTimur.flv"
    },
    {
        "id": "surakarta_sekarpaceutara",
        "name": "ATCS Surakarta \u2014 Sekarpace Utara",
        "location": "Sekarpace Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SekarpaceUtara.flv"
    },
    {
        "id": "surakarta_unstimur",
        "name": "ATCS Surakarta \u2014 UNS Timur",
        "location": "UNS Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/UNSTimur.flv"
    },
    {
        "id": "surakarta_sekarpacebarat",
        "name": "ATCS Surakarta \u2014 Sekarpace Barat",
        "location": "Sekarpace Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SekarpaceBarat.flv"
    },
    {
        "id": "surakarta_bundarantipes",
        "name": "ATCS Surakarta \u2014 Bundaran Tipes",
        "location": "Bundaran Tipes, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BundaranTipes.flv"
    },
    {
        "id": "surakarta_ringroadselatan",
        "name": "ATCS Surakarta \u2014 Ring Road Selatan",
        "location": "Ring Road Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadSelatan.flv"
    },
    {
        "id": "surakarta_ringroadutara",
        "name": "ATCS Surakarta \u2014 Ring Road Utara",
        "location": "Ring Road Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoadUtara.flv"
    },
    {
        "id": "surakarta_genenganutara",
        "name": "ATCS Surakarta \u2014 Genengan Utara",
        "location": "Genengan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganUtara.flv"
    },
    {
        "id": "surakarta_tuguwisnuutara",
        "name": "ATCS Surakarta \u2014 Tugu Wisnu Utara",
        "location": "Tugu Wisnu Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuUtara.flv"
    },
    {
        "id": "surakarta_kertenutara",
        "name": "ATCS Surakarta \u2014 Kerten Utara",
        "location": "Kerten Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KertenUtara.flv"
    },
    {
        "id": "surakarta_ruasringroadtimur",
        "name": "ATCS Surakarta \u2014 Ruas Ring Road Timur",
        "location": "Ruas Ring Road Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RuasRingRoadTimur.flv"
    },
    {
        "id": "surakarta_semanggi",
        "name": "ATCS Surakarta \u2014 Semanggi",
        "location": "Semanggi, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Semanggi.flv"
    },
    {
        "id": "surakarta_tuguwisnutimur",
        "name": "ATCS Surakarta \u2014 Tugu Wisnu Timur",
        "location": "Tugu Wisnu Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/TuguWisnuTimur.flv"
    },
    {
        "id": "surakarta_klodran",
        "name": "ATCS Surakarta \u2014 Klodran",
        "location": "Klodran, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Klodran.flv"
    },
    {
        "id": "surakarta_mipitan",
        "name": "ATCS Surakarta \u2014 Mipitan",
        "location": "Mipitan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Mipitan.flv"
    },
    {
        "id": "surakarta_dawungutara",
        "name": "ATCS Surakarta \u2014 Dawung Utara",
        "location": "Dawung Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/DawungUtara.flv"
    },
    {
        "id": "surakarta_gemblegan",
        "name": "ATCS Surakarta \u2014 Gemblegan",
        "location": "Gemblegan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gemblegan.flv"
    },
    {
        "id": "surakarta_kelurahansumberselatan",
        "name": "ATCS Surakarta \u2014 Kelurahan Sumber Selatan",
        "location": "Kelurahan Sumber Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KelurahanSumberSelatan.flv"
    },
    {
        "id": "surakarta_kelurahansumberbarat",
        "name": "ATCS Surakarta \u2014 Kelurahan Sumber Barat",
        "location": "Kelurahan Sumber Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KelurahanSumberBarat.flv"
    },
    {
        "id": "surakarta_gladag",
        "name": "ATCS Surakarta \u2014 Gladag",
        "location": "Gladag, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gladag.flv"
    },
    {
        "id": "surakarta_kelurahansumberutara",
        "name": "ATCS Surakarta \u2014 Kelurahan Sumber Utara",
        "location": "Kelurahan Sumber Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KelurahanSumberUtara.flv"
    },
    {
        "id": "surakarta_kabangan",
        "name": "ATCS Surakarta \u2014 Kabangan",
        "location": "Kabangan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Kabangan.flv"
    },
    {
        "id": "surakarta_gendengantimur",
        "name": "ATCS Surakarta \u2014 Gendengan Timur",
        "location": "Gendengan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GendenganTimur.flv"
    },
    {
        "id": "surakarta_farokah",
        "name": "ATCS Surakarta \u2014 Farokah",
        "location": "Farokah, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Farokah.flv"
    },
    {
        "id": "surakarta_lojigandrung",
        "name": "ATCS Surakarta \u2014 Loji Gandrung",
        "location": "Loji Gandrung, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/LojiGandrung.flv"
    },
    {
        "id": "surakarta_sekarpace",
        "name": "ATCS Surakarta \u2014 Sekarpace",
        "location": "Sekarpace, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sekarpace.flv"
    },
    {
        "id": "surakarta_pasarpon01",
        "name": "ATCS Surakarta \u2014 Pasar Pon 01",
        "location": "Pasar Pon 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarPon01.flv"
    },
    {
        "id": "surakarta_balaikota",
        "name": "ATCS Surakarta \u2014 Balai Kota",
        "location": "Balai Kota, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BalaiKota.flv"
    },
    {
        "id": "surakarta_pgs",
        "name": "ATCS Surakarta \u2014 PGS",
        "location": "PGS, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PGS.flv"
    },
    {
        "id": "surakarta_kandangsapi",
        "name": "ATCS Surakarta \u2014 Kandang Sapi",
        "location": "Kandang Sapi, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KandangSapi.flv"
    },
    {
        "id": "surakarta_ursulin",
        "name": "ATCS Surakarta \u2014 Ursulin",
        "location": "Ursulin, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ursulin.flv"
    },
    {
        "id": "surakarta_gembleganbarat",
        "name": "ATCS Surakarta \u2014 Gemblegan Barat",
        "location": "Gemblegan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganBarat.flv"
    },
    {
        "id": "surakarta_pasargede",
        "name": "ATCS Surakarta \u2014 Pasar Gede",
        "location": "Pasar Gede, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarGede.flv"
    },
    {
        "id": "surakarta_gembleganselatan",
        "name": "ATCS Surakarta \u2014 Gemblegan Selatan",
        "location": "Gemblegan Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganSelatan.flv"
    },
    {
        "id": "surakarta_panggungtimur",
        "name": "ATCS Surakarta \u2014 Panggung Timur",
        "location": "Panggung Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungTimur.flv"
    },
    {
        "id": "surakarta_gemblegantimur",
        "name": "ATCS Surakarta \u2014 Gemblegan Timur",
        "location": "Gemblegan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganTimur.flv"
    },
    {
        "id": "surakarta_cembengan",
        "name": "ATCS Surakarta \u2014 Cembengan",
        "location": "Cembengan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Cembengan.flv"
    },
    {
        "id": "surakarta_gendenganbarat",
        "name": "ATCS Surakarta \u2014 Gendengan Barat",
        "location": "Gendengan Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GendenganBarat.flv"
    },
    {
        "id": "surakarta_smp18",
        "name": "ATCS Surakarta \u2014 SMP 18",
        "location": "SMP 18, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SMP18.flv"
    },
    {
        "id": "surakarta_kelurahansumbertimur",
        "name": "ATCS Surakarta \u2014 Kelurahan Sumber Timur",
        "location": "Kelurahan Sumber Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KelurahanSumberTimur.flv"
    },
    {
        "id": "surakarta_overpassselatan",
        "name": "ATCS Surakarta \u2014 Overpass Selatan",
        "location": "Overpass Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/OverpassSelatan.flv"
    },
    {
        "id": "surakarta_overpassbarat",
        "name": "ATCS Surakarta \u2014 Overpass Barat",
        "location": "Overpass Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/OverpassBarat.flv"
    },
    {
        "id": "surakarta_kerten",
        "name": "ATCS Surakarta \u2014 Kerten",
        "location": "Kerten, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Kerten.flv"
    },
    {
        "id": "surakarta_rahayu01",
        "name": "ATCS Surakarta \u2014 Rahayu 01",
        "location": "Rahayu 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Rahayu01.flv"
    },
    {
        "id": "surakarta_sriwedari01",
        "name": "ATCS Surakarta \u2014 Sriwedari 01",
        "location": "Sriwedari 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sriwedari01.flv"
    },
    {
        "id": "surakarta_sraten",
        "name": "ATCS Surakarta \u2014 Sraten",
        "location": "Sraten, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sraten.flv"
    },
    {
        "id": "surakarta_ringroad",
        "name": "ATCS Surakarta \u2014 Ring Road",
        "location": "Ring Road, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RingRoad.flv"
    },
    {
        "id": "surakarta_ketandan",
        "name": "ATCS Surakarta \u2014 Ketandan",
        "location": "Ketandan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ketandan.flv"
    },
    {
        "id": "surakarta_tipes",
        "name": "ATCS Surakarta \u2014 Tipes",
        "location": "Tipes, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Tipes.flv"
    },
    {
        "id": "surakarta_gendengan01",
        "name": "ATCS Surakarta \u2014 Gendengan 01",
        "location": "Gendengan 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Gendengan01.flv"
    },
    {
        "id": "surakarta_vmsdprd",
        "name": "ATCS Surakarta \u2014 VMSDPRD",
        "location": "VMSDPRD, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/VMSDPRD.flv"
    },
    {
        "id": "surakarta_panggungselatan",
        "name": "ATCS Surakarta \u2014 Panggung Selatan",
        "location": "Panggung Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungSelatan.flv"
    },
    {
        "id": "surakarta_gembleganutara",
        "name": "ATCS Surakarta \u2014 Gemblegan Utara",
        "location": "Gemblegan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GembleganUtara.flv"
    },
    {
        "id": "surakarta_panggungutara",
        "name": "ATCS Surakarta \u2014 Panggung Utara",
        "location": "Panggung Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungUtara.flv"
    },
    {
        "id": "surakarta_fajarindahbarat",
        "name": "ATCS Surakarta \u2014 Fajar Indah Barat",
        "location": "Fajar Indah Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahBarat.flv"
    },
    {
        "id": "surakarta_tuguwisnu01",
        "name": "ATCS Surakarta \u2014 Tugu Wisnu 01",
        "location": "Tugu Wisnu 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/TuguWisnu01.flv"
    },
    {
        "id": "surakarta_fajarindahutara",
        "name": "ATCS Surakarta \u2014 Fajar Indah Utara",
        "location": "Fajar Indah Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahUtara.flv"
    },
    {
        "id": "surakarta_mijipinilihanlor",
        "name": "ATCS Surakarta \u2014 Mijipinilihan Lor",
        "location": "Mijipinilihan Lor, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/MijipinilihanLor.flv"
    },
    {
        "id": "surakarta_panggungbarat",
        "name": "ATCS Surakarta \u2014 Panggung Barat",
        "location": "Panggung Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PanggungBarat.flv"
    },
    {
        "id": "surakarta_ngemplakutara",
        "name": "ATCS Surakarta \u2014 Ngemplak Utara",
        "location": "Ngemplak Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakUtara.flv"
    },
    {
        "id": "surakarta_ngemplaktimur",
        "name": "ATCS Surakarta \u2014 Ngemplak Timur",
        "location": "Ngemplak Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakTimur.flv"
    },
    {
        "id": "surakarta_jurug",
        "name": "ATCS Surakarta \u2014 Jurug",
        "location": "Jurug, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Jurug.flv"
    },
    {
        "id": "surakarta_fajarindahselatan",
        "name": "ATCS Surakarta \u2014 Fajar Indah Selatan",
        "location": "Fajar Indah Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahSelatan.flv"
    },
    {
        "id": "surakarta_ngemplakselatan",
        "name": "ATCS Surakarta \u2014 Ngemplak Selatan",
        "location": "Ngemplak Selatan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakSelatan.flv"
    },
    {
        "id": "surakarta_ngemplakbarat",
        "name": "ATCS Surakarta \u2014 Ngemplak Barat",
        "location": "Ngemplak Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NgemplakBarat.flv"
    },
    {
        "id": "surakarta_klodranbarat",
        "name": "ATCS Surakarta \u2014 Klodran Barat",
        "location": "Klodran Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KlodranBarat.flv"
    },
    {
        "id": "surakarta_mujahidin",
        "name": "ATCS Surakarta \u2014 Mujahidin",
        "location": "Mujahidin, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Mujahidin.flv"
    },
    {
        "id": "surakarta_kelurahansumber01",
        "name": "ATCS Surakarta \u2014 Kelurahan Sumber 01",
        "location": "Kelurahan Sumber 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/KelurahanSumber01.flv"
    },
    {
        "id": "surakarta_fajarindahtimur",
        "name": "ATCS Surakarta \u2014 Fajar Indah Timur",
        "location": "Fajar Indah Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndahTimur.flv"
    },
    {
        "id": "surakarta_makutho",
        "name": "ATCS Surakarta \u2014 Makutho",
        "location": "Makutho, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Makutho.flv"
    },
    {
        "id": "surakarta_balong",
        "name": "ATCS Surakarta \u2014 Balong",
        "location": "Balong, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Balong.flv"
    },
    {
        "id": "surakarta_bawahflyoverpurwosari",
        "name": "ATCS Surakarta \u2014 Bawah Flyover Purwosari",
        "location": "Bawah Flyover Purwosari, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BawahFlyoverPurwosari.flv"
    },
    {
        "id": "surakarta_gondangwide",
        "name": "ATCS Surakarta \u2014 Gondang Wide",
        "location": "Gondang Wide, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GondangWide.flv"
    },
    {
        "id": "surakarta_isiwide",
        "name": "ATCS Surakarta \u2014 ISI Wide",
        "location": "ISI Wide, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/ISIWide.flv"
    },
    {
        "id": "surakarta_balapan01",
        "name": "ATCS Surakarta \u2014 Balapan 01",
        "location": "Balapan 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv"
    },
    {
        "id": "surakarta_pasarkliwon",
        "name": "ATCS Surakarta \u2014 Pasar Kliwon",
        "location": "Pasar Kliwon, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/PasarKliwon.flv"
    },
    {
        "id": "surakarta_isiptz",
        "name": "ATCS Surakarta \u2014 ISIPTZ",
        "location": "ISIPTZ, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/ISIPTZ.flv"
    },
    {
        "id": "surakarta_gondangptz",
        "name": "ATCS Surakarta \u2014 Gondang PTZ",
        "location": "Gondang PTZ, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GondangPTZ.flv"
    },
    {
        "id": "surakarta_agas",
        "name": "ATCS Surakarta \u2014 Agas",
        "location": "Agas, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Agas.flv"
    },
    {
        "id": "surakarta_satesumber01",
        "name": "ATCS Surakarta \u2014 Sate Sumber 01",
        "location": "Sate Sumber 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/SateSumber01.flv"
    },
    {
        "id": "surakarta_warungpelemtimur",
        "name": "ATCS Surakarta \u2014 Warung Pelem Timur",
        "location": "Warung Pelem Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/WarungPelemTimur.flv"
    },
    {
        "id": "surakarta_warungpelembarat",
        "name": "ATCS Surakarta \u2014 Warung Pelem Barat",
        "location": "Warung Pelem Barat, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/WarungPelemBarat.flv"
    },
    {
        "id": "surakarta_sangkrah",
        "name": "ATCS Surakarta \u2014 Sangkrah",
        "location": "Sangkrah, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Sangkrah.flv"
    },
    {
        "id": "surakarta_mojosongo",
        "name": "ATCS Surakarta \u2014 Mojosongo",
        "location": "Mojosongo, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Mojosongo.flv"
    },
    {
        "id": "surakarta_jongke",
        "name": "ATCS Surakarta \u2014 Jongke",
        "location": "Jongke, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Jongke.flv"
    },
    {
        "id": "surakarta_panggung",
        "name": "ATCS Surakarta \u2014 Panggung",
        "location": "Panggung, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Panggung.flv"
    },
    {
        "id": "surakarta_baturono",
        "name": "ATCS Surakarta \u2014 Batu Rono",
        "location": "Batu Rono, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/BatuRono.flv"
    },
    {
        "id": "surakarta_tirtonadi01",
        "name": "ATCS Surakarta \u2014 Tirtonadi 01",
        "location": "Tirtonadi 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Tirtonadi01.flv"
    },
    {
        "id": "surakarta_purwosari",
        "name": "ATCS Surakarta \u2014 Purwosari",
        "location": "Purwosari, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Purwosari.flv"
    },
    {
        "id": "surakarta_komplang01",
        "name": "ATCS Surakarta \u2014 Komplang 01",
        "location": "Komplang 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Komplang01.flv"
    },
    {
        "id": "surakarta_baron",
        "name": "ATCS Surakarta \u2014 Baron",
        "location": "Baron, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Baron.flv"
    },
    {
        "id": "surakarta_warungpelem",
        "name": "ATCS Surakarta \u2014 Warung Pelem",
        "location": "Warung Pelem, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/WarungPelem.flv"
    },
    {
        "id": "surakarta_girimulyo01",
        "name": "ATCS Surakarta \u2014 Giri Mulyo 01",
        "location": "Giri Mulyo 01, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GiriMulyo01.flv"
    },
    {
        "id": "surakarta_ngemplak",
        "name": "ATCS Surakarta \u2014 Ngemplak",
        "location": "Ngemplak, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Ngemplak.flv"
    },
    {
        "id": "surakarta_fajarindah",
        "name": "ATCS Surakarta \u2014 Fajar Indah",
        "location": "Fajar Indah, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FajarIndah.flv"
    },
    {
        "id": "surakarta_gendenganutara",
        "name": "ATCS Surakarta \u2014 Gendengan Utara",
        "location": "Gendengan Utara, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GendenganUtara.flv"
    },
    {
        "id": "surakarta_flyover",
        "name": "ATCS Surakarta \u2014 Fly Over",
        "location": "Fly Over, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/FlyOver.flv"
    },
    {
        "id": "surakarta_overpassmanahan",
        "name": "ATCS Surakarta \u2014 Overpass Manahan",
        "location": "Overpass Manahan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/OverpassManahan.flv"
    },
    {
        "id": "surakarta_nononganwide",
        "name": "ATCS Surakarta \u2014 Nonongan Wide",
        "location": "Nonongan Wide, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/NononganWide.flv"
    },
    {
        "id": "surakarta_genengantimur",
        "name": "ATCS Surakarta \u2014 Genengan Timur",
        "location": "Genengan Timur, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/GenenganTimur.flv"
    },
    {
        "id": "surakarta_nonongan",
        "name": "ATCS Surakarta \u2014 Nonongan",
        "location": "Nonongan, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/Nonongan.flv"
    },
    {
        "id": "surakarta_ruasmakutho",
        "name": "ATCS Surakarta \u2014 Ruas Makutho",
        "location": "Ruas Makutho, Surakarta",
        "url": "https://surakarta.atcsindonesia.info:8086/camera/RuasMakutho.flv"
    },
    {
        "id": "surakarta_demo",
        "name": "Mode Demo Offline",
        "location": "Offline Demo Stream",
        "url": "synthetic://demo"
    }
]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = AppSettings()
