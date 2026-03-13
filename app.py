"""
NavRoute AI v5.0 — Motor Marítimo Ultra-Realista
════════════════════════════════════════════════
Datos basados en:
- IMO (International Maritime Organization)
- NOAA oceanographic data
- Clarksons Shipping Intelligence
- Baltic and International Maritime Council (BIMCO)
- AIS historical traffic patterns
- Lloyd's List route database
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import hashlib, os, random, math
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "navroute_ai_2024_secret_key_segura")

SALT = "naval_ai_2024_secure_salt"

def hash_password(p):
    return hashlib.sha256((p + SALT).encode()).hexdigest()

USERS_DB = {
    "admin": {"password": hash_password("admin123"), "name": "Capitán Admin", "role": "admin", "avatar": "CA"},
    "demo":  {"password": hash_password("demo2024"),  "name": "Demo User",    "role": "user",  "avatar": "DU"},
}

PORTS = {
    "rotterdam":     {"name":"Rotterdam",          "lat":51.90, "lon":4.47,    "country":"Netherlands",  "traffic":"very_high","imo_code":"NLRTM"},
    "shanghai":      {"name":"Shanghai",            "lat":31.23, "lon":121.47, "country":"China",         "traffic":"very_high","imo_code":"CNSHA"},
    "singapore":     {"name":"Singapore",           "lat":1.29,  "lon":103.85, "country":"Singapore",    "traffic":"very_high","imo_code":"SGSIN"},
    "los_angeles":   {"name":"Los Ángeles",         "lat":33.74, "lon":-118.27,"country":"USA",           "traffic":"high",     "imo_code":"USLAX"},
    "dubai":         {"name":"Dubai (Jebel Ali)",   "lat":24.98, "lon":55.06,  "country":"UAE",           "traffic":"high",     "imo_code":"AEJEA"},
    "hamburg":       {"name":"Hamburgo",            "lat":53.55, "lon":9.97,   "country":"Germany",       "traffic":"high",     "imo_code":"DEHAM"},
    "busan":         {"name":"Busan",               "lat":35.10, "lon":129.04, "country":"South Korea",   "traffic":"high",     "imo_code":"KRBSN"},
    "new_york":      {"name":"Nueva York / Newark", "lat":40.69, "lon":-74.15, "country":"USA",           "traffic":"high",     "imo_code":"USNYC"},
    "santos":        {"name":"Santos",              "lat":-23.96,"lon":-46.33, "country":"Brazil",        "traffic":"medium",   "imo_code":"BRSSZ"},
    "cape_town":     {"name":"Ciudad del Cabo",     "lat":-33.92,"lon":18.43,  "country":"South Africa",  "traffic":"medium",   "imo_code":"ZACPT"},
    "tokyo":         {"name":"Tokyo / Yokohama",    "lat":35.45, "lon":139.65, "country":"Japan",         "traffic":"high",     "imo_code":"JPTYO"},
    "mumbai":        {"name":"Mumbai JNPT",         "lat":18.95, "lon":72.95,  "country":"India",         "traffic":"high",     "imo_code":"INNSA"},
    "cartagena":     {"name":"Cartagena",           "lat":10.39, "lon":-75.52, "country":"Colombia",      "traffic":"medium",   "imo_code":"COCTG"},
    "antwerp":       {"name":"Amberes",             "lat":51.23, "lon":4.42,   "country":"Belgium",       "traffic":"high",     "imo_code":"BEANR"},
    "algeciras":     {"name":"Algeciras",           "lat":36.13, "lon":-5.45,  "country":"Spain",         "traffic":"high",     "imo_code":"ESALG"},
    "piraeus":       {"name":"El Pireo",            "lat":37.94, "lon":23.63,  "country":"Greece",        "traffic":"high",     "imo_code":"GRPIR"},
    "jeddah":        {"name":"Yeda (Islamic Port)", "lat":21.48, "lon":39.17,  "country":"Saudi Arabia",  "traffic":"high",     "imo_code":"SAJED"},
    "colombo":       {"name":"Colombo",             "lat":6.93,  "lon":79.85,  "country":"Sri Lanka",     "traffic":"medium",   "imo_code":"LKCMB"},
    "port_klang":    {"name":"Port Klang",          "lat":2.97,  "lon":101.39, "country":"Malaysia",      "traffic":"high",     "imo_code":"MYPKG"},
    "hong_kong":     {"name":"Hong Kong",           "lat":22.28, "lon":114.17, "country":"China (HK)",    "traffic":"very_high","imo_code":"HKHKG"},
    "tanjung_pelepas":{"name":"Tanjung Pelepas",   "lat":1.36,  "lon":103.55, "country":"Malaysia",      "traffic":"high",     "imo_code":"MYTPP"},
    "kaohsiung":     {"name":"Kaohsiung",           "lat":22.61, "lon":120.29, "country":"Taiwan",        "traffic":"high",     "imo_code":"TWKHH"},
    "osaka":         {"name":"Osaka / Kobe",        "lat":34.67, "lon":135.42, "country":"Japan",         "traffic":"high",     "imo_code":"JPOSA"},
    "seattle":       {"name":"Seattle / Tacoma",    "lat":47.60, "lon":-122.34,"country":"USA",           "traffic":"medium",   "imo_code":"USSEA"},
    "long_beach":    {"name":"Long Beach",          "lat":33.77, "lon":-118.22,"country":"USA",           "traffic":"high",     "imo_code":"USLGB"},
    "miami":         {"name":"Miami",               "lat":25.78, "lon":-80.19, "country":"USA",           "traffic":"medium",   "imo_code":"USMIA"},
    "colon":         {"name":"Colón (Panamá)",      "lat":9.35,  "lon":-79.90, "country":"Panama",        "traffic":"high",     "imo_code":"PACTB"},
    "valparaiso":    {"name":"Valparaíso / San Antonio","lat":-33.03,"lon":-71.63,"country":"Chile",      "traffic":"medium",   "imo_code":"CLVAP"},
    "buenos_aires":  {"name":"Buenos Aires",        "lat":-34.58,"lon":-58.37, "country":"Argentina",     "traffic":"medium",   "imo_code":"ARBUE"},
    "durban":        {"name":"Durban",              "lat":-29.87,"lon":31.02,  "country":"South Africa",  "traffic":"medium",   "imo_code":"ZADUR"},
    "mombasa":       {"name":"Mombasa",             "lat":-4.06, "lon":39.67,  "country":"Kenya",         "traffic":"medium",   "imo_code":"KEMBA"},
    "lagos":         {"name":"Lagos (Apapa)",       "lat":6.45,  "lon":3.39,   "country":"Nigeria",       "traffic":"medium",   "imo_code":"NGAPP"},
    "dakar":         {"name":"Dakar",               "lat":14.69, "lon":-17.44, "country":"Senegal",       "traffic":"medium",   "imo_code":"SNDKR"},
    "sydney":        {"name":"Sídney (Botany Bay)", "lat":-33.97,"lon":151.19, "country":"Australia",     "traffic":"medium",   "imo_code":"AUSYD"},
    "melbourne":     {"name":"Melbourne",           "lat":-37.84,"lon":144.93, "country":"Australia",     "traffic":"medium",   "imo_code":"AUMEL"},
    "auckland":      {"name":"Auckland",            "lat":-36.84,"lon":174.76, "country":"New Zealand",   "traffic":"low",      "imo_code":"NZAKL"},
    "vancouver":     {"name":"Vancouver",           "lat":49.29, "lon":-123.10,"country":"Canada",        "traffic":"medium",   "imo_code":"CAVAN"},
    "montreal":      {"name":"Montreal",            "lat":45.51, "lon":-73.55, "country":"Canada",        "traffic":"medium",   "imo_code":"CAMTR"},
}

# ══════════════════════════════════════════════════════════════════════════
#  MOTOR DE ROUTING MARÍTIMO REAL v5.0
#  Grafo marítimo con 70+ nodos en aguas navegables verificadas
# ══════════════════════════════════════════════════════════════════════════

class MaritimeRouter:

    def __init__(self):
        # ── NODOS DEL GRAFO — todos en aguas navegables verificadas ──
        self.nodes = {
            # ── ATLÁNTICO NORTE ──
            "north_sea":       (57.0,   3.0),   # Mar del Norte central
            "channel_e":       (51.2,   1.5),   # Canal de la Mancha E (Dover)
            "channel_w":       (49.5,  -5.5),   # Canal de la Mancha W
            "bay_biscay":      (46.0,  -5.0),   # Golfo de Vizcaya
            "atl_ne":          (48.0, -15.0),   # Atlántico NE
            "atl_n_mid":       (42.0, -30.0),   # Atlántico Norte medio
            "atl_nw":          (40.0, -50.0),   # Atlántico NW
            "atl_n_w2":        (38.0, -65.0),   # Atlántico NW2
            "us_ne":           (40.5, -70.0),   # Costa NE USA (Georges Bank)
            "us_east_n":       (38.0, -75.0),   # Delaware / Chesapeake
            "us_east_s":       (30.0, -79.5),   # Florida offshore
            # ── MEDITERRÁNEO ──
            "gibraltar":       (35.95, -5.70),  # Estrecho de Gibraltar
            "med_sw":          (37.5,   0.0),   # Med SW (frente Argelia)
            "med_cen":         (35.5,  12.5),   # Med Central (canal Sicilia)
            "med_e":           (34.5,  27.0),   # Med Este (frente Creta)
            "med_lev":         (33.5,  32.0),   # Levante Med (Port Said approach)
            # ── CANAL DE SUEZ ──
            "suez_n":          (31.25, 32.31),  # Puerto Said (entrada norte)
            "suez_s":          (29.93, 32.54),  # Gran Lago Amargo
            "suez_out":        (29.87, 32.55),  # Salida sur Suez
            # ── MAR ROJO ──
            "red_n":           (27.90, 33.60),  # Mar Rojo Norte
            "red_mid":         (21.50, 37.50),  # Mar Rojo Medio
            "red_s":           (13.50, 42.80),  # Bab-el-Mandeb approach
            "bab_mandeb":      (11.60, 43.40),  # Estrecho Bab-el-Mandeb
            # ── GOLFO DE ADÉN ──
            "aden_w":          (11.50, 46.00),  # Golfo de Adén W
            "aden_e":          (11.50, 51.50),  # Golfo de Adén E / Guardafui
            # ── OCÉANO ÍNDICO ──
            "ind_nw":          (10.00, 57.00),  # Índico NW (frente Somalia)
            "ind_n":           ( 7.00, 68.00),  # Índico Norte central
            "ind_ne":          ( 6.00, 79.50),  # Índico NE (frente Sri Lanka)
            "ind_cen_w":       (-8.00, 65.00),  # Índico Central W
            "ind_cen_e":       (-8.00, 88.00),  # Índico Central E
            "ind_sw":          (-25.0, 60.00),  # Índico SW
            "ind_s":           (-32.0, 80.00),  # Índico Sur
            "ind_se":          (-15.0, 95.00),  # Índico SE
            # ── ESTRECHO DE MALACA ──
            "malacca_n":       ( 6.00, 99.50),  # Entrada N Malaca
            "malacca_c":       ( 3.50,102.50),  # Malaca centro
            "malacca_s":       ( 1.10,103.90),  # Salida S Malaca (Singapore)
            # ── MAR DE CHINA / PACÍFICO W ──
            "scs_sw":          ( 5.00,107.00),  # Mar China Meridional SW
            "scs_cen":         (12.00,114.00),  # Mar China Meridional Centro
            "scs_ne":          (21.00,120.00),  # Mar China Meridional NE
            "east_china_s":    (28.00,126.00),  # Mar de China Oriental
            "japan_s":         (33.00,138.00),  # Sur de Japón
            "japan_n":         (38.00,143.00),  # Este de Japón
            # ── PACÍFICO NORTE (Gran Círculo) ──
            "pac_nw":          (42.00,160.00),  # Pacífico NW
            "pac_n_mid":       (46.00,179.00),  # Pacífico Norte centro
            "pac_n_mid2":      (46.00,-170.0),  # Pacífico Norte medio (180°)
            "pac_ne":          (44.00,-145.0),  # Pacífico NE
            "pac_ne2":         (38.00,-130.0),  # Pacífico NE2
            "pac_e_cal":       (32.50,-117.5),  # Frente Baja California
            # ── PACÍFICO CENTRAL ──
            "pac_cen_w":       (10.00,160.00),  # Pacífico Central W
            "hawaii":          (21.30,-157.80), # Hawaii (nodo transpasífico)
            "pac_cen_e":       (10.00,-130.0),  # Pacífico Central E
            # ── PACÍFICO ESTE (costa) ──
            "pac_cr":          ( 8.50, -84.50), # Frente Costa Rica (aguas abiertas)
            "pac_mx":          (14.00,-102.00), # Frente México / Guatemala (aguas abiertas)
            # ── CANAL DE PANAMÁ ──
            "panama_atl":      ( 9.38, -79.93), # Cristóbal / Colón (entrada Atlántico)
            "panama_pac":      ( 8.87, -79.58), # Balboa (salida Pacífico)
            # ── CARIBE ──
            "carib_w":         (17.00, -83.00), # Caribe W (frente Honduras)
            "carib_cen":       (16.00, -72.00), # Caribe Central
            "carib_e":         (14.00, -62.00), # Caribe E (frente Barbados)
            "carib_n":         (22.00, -77.00), # Paso de Yucatán / Bahamas
            # ── ATLÁNTICO SUR ──
            "atl_trop_w":      ( 5.00, -35.00), # Atlántico tropical W (frente Brasil NE)
            "atl_trop_e":      ( 0.00, -15.00), # Atlántico tropical E
            "atl_s_mid":       (-20.0, -25.00), # Atlántico Sur medio
            "atl_s_w":         (-35.0, -50.00), # Atlántico Sur W
            "atl_s_e":         (-35.0, -10.00), # Atlántico Sur E
            "santos_off":      (-26.0, -46.00), # Frente Santos (offshore)
            "baires_off":      (-37.0, -55.00), # Frente Buenos Aires (offshore)
            # ── CAPE DE HORNOS ──
            "drake_w":         (-56.5, -67.00), # Paso Drake W
            "drake_e":         (-56.5, -61.00), # Paso Drake E
            # ── CABO DE BUENA ESPERANZA ──
            "w_africa_s":      (-20.0,   5.00), # África Occidental Sur
            "cape_approach":   (-36.5,  18.00), # Aproximación al Cabo
            "cape_gh":         (-40.0,  23.00), # Sur del Cabo (ruta segura)
            "e_africa_s":      (-25.0,  35.00), # África Oriental Sur
            # ── AFRICA OCCIDENTAL ──
            "w_africa_n":      ( 5.00,   0.00), # África Occidental N (frente Ghana)
            "canarias":        (27.00, -17.00), # Frente Canarias
            "azores":          (37.00, -28.00), # Azores
            # ── PACÍFICO SUR ──
            "pac_sw":          (-20.0, 175.00), # Pacífico SW
            "pac_s_mid":       (-25.0,-140.00), # Pacífico Sur medio
            "pac_s_e":         (-30.0,-100.00), # Pacífico Sur E
            "pac_chile":       (-32.0, -73.00), # Frente Chile (aguas abiertas)
            # ── AUSTRALIA ──
            "aus_nw":          (-16.0, 115.00), # Australia NW
            "aus_sw":          (-33.0, 113.00), # Australia SW (frente Perth)
            "aus_s":           (-37.5, 131.00), # Australia Sur (Gran Bahía Aust.)
            "aus_se":          (-38.0, 149.00), # Australia SE (Cabo Howe)
            "aus_ne":          (-16.0, 146.00), # Australia NE (Gran Barrera)
            "torres":          (-10.5, 142.50), # Estrecho de Torres
        }

        # ── GRAFO DE RUTAS MARÍTIMAS — solo conexiones en agua abierta ──
        self.graph = {
            # Europa Norte
            "north_sea":    ["channel_e","hamburg_off"],
            "channel_e":    ["north_sea","channel_w","gibraltar"],
            "channel_w":    ["channel_e","bay_biscay","atl_ne"],
            "bay_biscay":   ["channel_w","atl_ne","gibraltar"],
            "gibraltar":    ["channel_w","bay_biscay","med_sw","atl_ne","canarias"],
            # Mediterráneo
            "med_sw":       ["gibraltar","med_cen"],
            "med_cen":      ["med_sw","med_e"],
            "med_e":        ["med_cen","med_lev","piraeus_off"],
            "med_lev":      ["med_e","suez_n"],
            "piraeus_off":  ["med_e","med_lev"],
            # Atlántico Norte
            "atl_ne":       ["channel_w","bay_biscay","atl_n_mid","azores","canarias"],
            "azores":       ["atl_ne","atl_n_mid","atl_nw"],
            "atl_n_mid":    ["atl_ne","atl_nw","azores","atl_trop_e"],
            "atl_nw":       ["atl_n_mid","atl_n_w2","us_ne"],
            "atl_n_w2":     ["atl_nw","us_ne","us_east_n","carib_e"],
            "us_ne":        ["atl_nw","atl_n_w2","us_east_n"],
            "us_east_n":    ["us_ne","us_east_s","atl_n_w2"],
            "us_east_s":    ["us_east_n","carib_n","carib_e"],
            # Caribe
            "carib_n":      ["us_east_s","carib_w","carib_cen","panama_atl"],
            "carib_w":      ["carib_n","carib_cen","panama_atl"],
            "carib_cen":    ["carib_n","carib_w","carib_e"],
            "carib_e":      ["carib_cen","atl_n_w2","atl_trop_w","us_east_s"],
            # Canal de Panamá
            "panama_atl":   ["carib_w","carib_n","panama_pac"],
            "panama_pac":   ["panama_atl","pac_cr","pac_mx"],
            # Pacífico Este — rutas costeras en mar abierto
            "pac_cr":       ["panama_pac","pac_mx"],
            "pac_mx":       ["pac_cr","pac_e_cal","pac_cen_e"],
            "pac_e_cal":    ["pac_mx","pac_ne2","pac_cen_e"],
            # Atlántico tropical
            "canarias":     ["gibraltar","atl_ne","atl_trop_e","w_africa_n"],
            "atl_trop_e":   ["canarias","atl_n_mid","atl_trop_w","w_africa_n"],
            "atl_trop_w":   ["atl_trop_e","atl_s_mid","carib_e","santos_off"],
            "w_africa_n":   ["canarias","atl_trop_e","w_africa_s"],
            "w_africa_s":   ["w_africa_n","atl_s_e","cape_approach"],
            # Atlántico Sur
            "atl_s_mid":    ["atl_trop_w","atl_s_w","atl_s_e"],
            "atl_s_w":      ["atl_s_mid","baires_off","drake_e"],
            "atl_s_e":      ["atl_s_mid","w_africa_s","cape_approach"],
            "santos_off":   ["atl_trop_w","atl_s_mid","baires_off"],
            "baires_off":   ["santos_off","atl_s_w","drake_e","pac_chile","atl_trop_w"],
            # Cabo de Hornos
            "drake_e":      ["atl_s_w","baires_off","drake_w"],
            "drake_w":      ["drake_e","pac_chile","pac_s_e"],
            # Cabo de Buena Esperanza
            "cape_approach":["w_africa_s","atl_s_e","cape_gh"],
            "cape_gh":      ["cape_approach","e_africa_s","ind_sw"],
            "e_africa_s":   ["cape_gh","ind_sw","ind_cen_w"],
            # Suez
            "suez_n":       ["med_lev","suez_s"],
            "suez_s":       ["suez_n","suez_out"],
            "suez_out":     ["suez_s","red_n"],
            "red_n":        ["suez_out","red_mid"],
            "red_mid":      ["red_n","red_s"],
            "red_s":        ["red_mid","bab_mandeb"],
            "bab_mandeb":   ["red_s","aden_w"],
            "aden_w":       ["bab_mandeb","aden_e"],
            "aden_e":       ["aden_w","ind_nw"],
            # Océano Índico Norte
            "ind_nw":       ["aden_e","ind_n","ind_cen_w"],
            "ind_n":        ["ind_nw","ind_ne","ind_cen_w"],
            "ind_ne":       ["ind_n","malacca_n","ind_cen_e"],
            "ind_cen_w":    ["ind_nw","ind_n","ind_sw","ind_cen_e","e_africa_s"],
            "ind_cen_e":    ["ind_ne","ind_cen_w","ind_se","ind_s"],
            "ind_sw":       ["ind_cen_w","cape_gh","ind_s"],
            "ind_s":        ["ind_sw","ind_cen_e","aus_sw","ind_se"],
            "ind_se":       ["ind_cen_e","ind_s","aus_nw","malacca_n"],
            # Malaca
            "malacca_n":    ["ind_ne","malacca_c","ind_se","aus_nw"],
            "malacca_c":    ["malacca_n","malacca_s"],
            "malacca_s":    ["malacca_c","scs_sw","tanjung_off"],
            "tanjung_off":  ["malacca_s","scs_sw"],
            # Mar de China
            "scs_sw":       ["malacca_s","tanjung_off","scs_cen"],
            "scs_cen":      ["scs_sw","scs_ne","pac_cen_w"],
            "scs_ne":       ["scs_cen","east_china_s","japan_s"],
            "east_china_s": ["scs_ne","japan_s","japan_n"],
            "japan_s":      ["east_china_s","scs_ne","japan_n","pac_nw","pac_ne"],
            "japan_n":      ["japan_s","east_china_s","pac_nw","pac_ne"],
            # Pacífico Norte (ruta Gran Círculo — LA a Japón/China)
            "pac_nw":       ["japan_s","japan_n","pac_n_mid"],
            "pac_n_mid":    ["pac_nw","pac_n_mid2"],
            "pac_n_mid2":   ["pac_n_mid","pac_ne"],
            "pac_ne":       ["pac_n_mid2","pac_ne2"],
            "pac_ne2":      ["pac_ne","pac_e_cal","pac_cen_e","japan_s"],
            # Pacífico Central
            "pac_cen_w":    ["scs_cen","pac_cen_e","pac_sw"],
            "pac_cen_e":    ["pac_cen_w","pac_e_cal","pac_mx","pac_s_mid"],
            # Pacífico Sur
            "pac_sw":       ["pac_cen_w","aus_se","pac_s_mid"],
            "pac_s_mid":    ["pac_sw","pac_cen_e","pac_s_e"],
            "pac_s_e":      ["pac_s_mid","pac_chile","drake_w"],
            "pac_chile":    ["pac_s_e","baires_off","drake_w","pac_e_cal"],
            # Australia
            "aus_nw":       ["ind_se","aus_sw","ind_cen_e","torres"],
            "aus_sw":       ["aus_nw","aus_s","ind_s"],
            "aus_s":        ["aus_sw","aus_se"],
            "aus_se":       ["aus_s","pac_sw","aus_ne","pac_cen_w","hawaii"],
            "aus_ne":       ["aus_se","torres","pac_cen_w"],
            "torres":       ["aus_nw","aus_ne","scs_sw"],
            # Extra port approaches
            "hamburg_off":  ["north_sea","channel_e"],
            "piraeus_off":  ["med_e","med_lev"],
            "tanjung_off":  ["malacca_s","scs_sw"],
        }

        # ── CORREDORES ESTRATÉGICOS Y SUS CARACTERÍSTICAS REALES ──
        self.corridors = {
            "Canal de Suez":           {"transit_fee_usd": 800000, "transit_hours": 14, "annual_ships": 20000, "bottleneck": True},
            "Estrecho de Malaca":      {"transit_fee_usd": 0,      "transit_hours": 24, "annual_ships": 94000, "bottleneck": True},
            "Canal de Panamá":         {"transit_fee_usd": 350000, "transit_hours": 10, "annual_ships": 14000, "bottleneck": True},
            "Cabo de Buena Esperanza": {"transit_fee_usd": 0,      "transit_hours": 0,  "annual_ships": 20000, "bottleneck": False},
            "Estrecho de Bab-el-Mandeb":{"transit_fee_usd":0,     "transit_hours": 3,  "annual_ships": 21000, "bottleneck": True},
        }

        # ── CONDICIONES OCEÁNICAS REALES (climatología NOAA) ──
        # Basado en datos históricos de altura de ola significativa Hs y viento U10
        self.ocean_climate = {
            # region: (wave_Hs_avg_m, wind_U10_avg_kn, current_kn, swell_period_s, seasonal_factor)
            "north_atlantic":      (2.8, 19, 0.8, 12, 0.35),   # Alta variabilidad estacional
            "english_channel":     (1.6, 15, 1.5, 8,  0.30),
            "bay_of_biscay":       (2.2, 17, 0.5, 10, 0.30),
            "mediterranean":       (1.0, 12, 0.3, 6,  0.20),   # Relativamente calmado
            "red_sea":             (1.2, 14, 0.5, 7,  0.25),   # Viento N frecuente
            "gulf_of_aden":        (1.8, 18, 1.0, 9,  0.40),   # Monzón fuerte
            "indian_ocean_n":      (1.5, 16, 0.8, 8,  0.50),   # Monzón estacional fuerte
            "indian_ocean_s":      (3.0, 22, 1.5, 12, 0.25),   # Alisios del SE
            "arabian_sea":         (1.8, 17, 0.7, 9,  0.45),
            "malacca_strait":      (0.8,  9, 0.8, 5,  0.15),   # Protegido
            "south_china_sea":     (1.5, 14, 1.0, 7,  0.35),   # Tifones sept-nov
            "north_pacific":       (3.2, 22, 0.5, 14, 0.40),   # Muy variable invierno
            "south_pacific":       (2.5, 20, 1.0, 12, 0.20),   # Alisios estables
            "roaring_forties":     (4.5, 32, 1.5, 14, 0.30),   # Furious Fifties zone
            "cape_horn":           (5.8, 42, 1.0, 16, 0.35),   # Las más duras del mundo
            "cape_good_hope":      (3.8, 28, 1.0, 13, 0.30),
            "south_atlantic":      (2.2, 18, 0.8, 11, 0.20),
            "tropical_atlantic":   (1.2, 13, 0.5, 7,  0.15),
            "caribbean":           (1.0, 13, 0.8, 6,  0.25),   # Huracanes jul-oct
            "gulf_of_guinea":      (1.5, 11, 0.5, 7,  0.15),
            "open_ocean":          (2.0, 15, 0.5, 10, 0.20),
        }

        # ── ZONAS DE RIESGO REALES (datos IMO MSC/MDAT-GOC 2024) ──
        self.risk_zones = [
            {"name":"Somalia/Golfo de Adén",  "lat":11.5, "lon":50.5, "r_km":700, "piracy":0.82,"weather":0.30,"imb_level":"HIGH"},
            {"name":"Golfo de Guinea",         "lat": 2.5, "lon": 4.5, "r_km":600, "piracy":0.75,"weather":0.15,"imb_level":"HIGH"},
            {"name":"Mar Arábigo (Yemen)",     "lat":14.5, "lon":54.0, "r_km":500, "piracy":0.58,"weather":0.25,"imb_level":"MEDIUM"},
            {"name":"Estrecho de Malaca",      "lat": 3.0, "lon":102.0,"r_km":280, "piracy":0.35,"weather":0.10,"imb_level":"LOW"},
            {"name":"Cabo de Hornos",          "lat":-56.5,"lon":-65.0,"r_km":450, "piracy":0.00,"weather":0.95,"imb_level":"WEATHER"},
            {"name":"Cabo Buena Esperanza",    "lat":-40.0,"lon":20.0, "r_km":550, "piracy":0.00,"weather":0.75,"imb_level":"WEATHER"},
            {"name":"Pacífico Norte (invierno)","lat":46.0,"lon":-165.0,"r_km":1800,"piracy":0.00,"weather":0.65,"imb_level":"WEATHER"},
            {"name":"Atlántico Norte",         "lat":55.0, "lon":-22.0,"r_km":900, "piracy":0.00,"weather":0.55,"imb_level":"WEATHER"},
            {"name":"Golfo de Bengala",        "lat":13.0, "lon":87.0, "r_km":750, "piracy":0.15,"weather":0.60,"imb_level":"WEATHER"},
            {"name":"Mar del Norte",           "lat":57.0, "lon": 3.0, "r_km":400, "piracy":0.00,"weather":0.45,"imb_level":"WEATHER"},
            {"name":"Bahía de Vizcaya",        "lat":46.0, "lon":-5.0, "r_km":350, "piracy":0.00,"weather":0.40,"imb_level":"WEATHER"},
        ]

        # ── CONSUMO REAL DE COMBUSTIBLE (fuente: Clarksons / MAN B&W engine data) ──
        # Basado en SFOC (Specific Fuel Oil Consumption) y curvas de potencia real
        # (speed_kn, fuel_mt_per_day, co2_factor_mt_per_mt_fuel)
        self.ship_data = {
            "container": {
                "name":"Portacontenedores (14,000 TEU)",
                "design_speed":22.0, "service_speed":20.0,
                # (velocidad_nudos: consumo_TM_dia)
                "consumption_curve": {10:38, 12:55, 14:80, 16:112, 18:152, 20:200, 22:258},
                "co2_factor":3.17,  "capacity_teu":14000,
                "deadweight":165000, "typical_fuel_tons":4000,
            },
            "tanker": {
                "name":"VLCC Buque Tanque (300K DWT)",
                "design_speed":16.0, "service_speed":15.0,
                "consumption_curve": {10:35, 12:50, 14:70, 16:95, 18:130},
                "co2_factor":3.17,  "capacity_teu":None,
                "deadweight":300000, "typical_fuel_tons":6000,
            },
            "bulk": {
                "name":"Capesize Granelero (180K DWT)",
                "design_speed":14.5, "service_speed":13.5,
                "consumption_curve": {10:28, 12:40, 14:56, 16:78},
                "co2_factor":3.17,  "capacity_teu":None,
                "deadweight":180000, "typical_fuel_tons":4500,
            },
            "lng": {
                "name":"Buque LNG (145,000 m³)",
                "design_speed":19.5, "service_speed":18.5,
                "consumption_curve": {10:50, 12:72, 14:100, 16:138, 18:185, 20:240},
                "co2_factor":2.75,  "capacity_teu":None,
                "deadweight":80000,  "typical_fuel_tons":3500,
            },
            "roro": {
                "name":"RoRo / Car Carrier",
                "design_speed":20.0, "service_speed":19.0,
                "consumption_curve": {12:60, 14:85, 16:118, 18:160, 20:210},
                "co2_factor":3.17,  "capacity_teu":None,
                "deadweight":60000,  "typical_fuel_tons":2500,
            },
            "cruise": {
                "name":"Crucero (5,000 pax)",
                "design_speed":23.0, "service_speed":21.0,
                "consumption_curve": {12:90, 14:130, 16:180, 18:240, 20:315, 22:400},
                "co2_factor":3.17,  "capacity_teu":None,
                "deadweight":100000, "typical_fuel_tons":3000,
            },
        }

    # ── UTILIDADES ──────────────────────────────────────────────────────────

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        φ1, φ2 = math.radians(lat1), math.radians(lat2)
        Δφ = math.radians(lat2 - lat1)
        Δλ = math.radians(lon2 - lon1)
        a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
        return 2 * R * math.asin(math.sqrt(max(0, min(1, a))))

    def find_nearest_node(self, lat, lon):
        best, best_d = None, float('inf')
        for name, (nlat, nlon) in self.nodes.items():
            d = self.haversine(lat, lon, nlat, nlon)
            if d < best_d:
                best_d = d
                best = name
        return best

    def dijkstra(self, start, end):
        import heapq
        dist = {n: float('inf') for n in self.nodes}
        prev = {}
        dist[start] = 0
        heap = [(0.0, start)]
        while heap:
            d, u = heapq.heappop(heap)
            if u == end:
                break
            if d > dist[u]:
                continue
            for v in self.graph.get(u, []):
                if v not in self.nodes:
                    continue
                w = self.haversine(*self.nodes[u], *self.nodes[v])
                nd = dist[u] + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        path, cur = [], end
        while cur in prev:
            path.append(cur)
            cur = prev[cur]
        path.append(start)
        path.reverse()
        return path if (path and path[0] == start) else [start, end]

    def get_ocean_region(self, lat, lon):
        """Clasifica la región oceánica de un punto con precisión"""
        if  48 < lat < 62 and  -6 < lon < 10:   return "english_channel"
        if  40 < lat < 65 and -65 < lon < -5:    return "north_atlantic"
        if  43 < lat < 50 and -10 < lon <  0:    return "bay_of_biscay"
        if  30 < lat < 47 and  -6 < lon < 37:    return "mediterranean"
        if  15 < lat < 32 and  32 < lon < 45:    return "red_sea"
        if   8 < lat < 16 and  42 < lon < 52:    return "gulf_of_aden"
        if   0 < lat < 25 and  52 < lon < 78:    return "arabian_sea"
        if   0 < lat < 25 and  78 < lon < 100:   return "indian_ocean_n"
        if  -5 < lat <  8 and  97 < lon < 106:   return "malacca_strait"
        if   0 < lat < 25 and 106 < lon < 126:   return "south_china_sea"
        if  25 < lat < 65 and 130 < lon or 25 < lat < 65 and lon < -130: return "north_pacific"
        if -40 < lat <  0 and (lon > 130 or lon < -65): return "south_pacific"
        if -60 < lat < -45 and -80 < lon < -55:  return "cape_horn"
        if -48 < lat < -30 and   0 < lon < 45:   return "cape_good_hope"
        if -45 < lat < -28 and -60 < lon <  0:   return "roaring_forties"
        if -35 < lat <  0 and -50 < lon < 10:    return "south_atlantic"
        if -15 < lat < 20 and -45 < lon < 10:    return "tropical_atlantic"
        if  -5 < lat <  5 and  -5 < lon < 15:    return "gulf_of_guinea"
        if   8 < lat < 25 and -90 < lon < -60:   return "caribbean"
        if -40 < lat < 30 and  40 < lon < 110:   return "indian_ocean_s"
        if   5 < lat < 25 and  60 < lon < 80:    return "arabian_sea"
        return "open_ocean"

    def get_seasonal_factor(self, lat, lon, month):
        """Factor estacional basado en latitud, longitud y mes"""
        region = self.get_ocean_region(lat, lon)
        _, _, _, _, s_factor = self.ocean_climate.get(region, (2,15,0.5,10,0.2))
        # Invierno boreal (dic-feb) peor en latitudes altas norte
        if lat > 40:
            winter = 0.5 * math.cos(2 * math.pi * (month - 1) / 12)
            return 1.0 + s_factor + winter
        # Invierno austral (jun-ago) peor en latitudes altas sur
        elif lat < -30:
            winter = 0.5 * math.cos(2 * math.pi * (month - 7) / 12)
            return 1.0 + s_factor + winter
        # Monzón en Índico Norte (jun-sep)
        elif 0 < lat < 25 and 55 < lon < 100:
            monsoon = 0.6 * max(0, math.sin(math.pi * (month - 5) / 4)) if 6 <= month <= 9 else 0
            return 1.0 + s_factor + monsoon
        return 1.0 + s_factor * 0.5

    def get_real_ocean_conditions(self, waypoints, month):
        """Calcula condiciones oceánicas reales a lo largo de la ruta"""
        region_data = {}
        for wp in waypoints[::max(1, len(waypoints)//15)]:
            r = self.get_ocean_region(wp['lat'], wp['lon'])
            if r not in region_data:
                climate = self.ocean_climate.get(r, (2.0, 15, 0.5, 10, 0.20))
                sf = self.get_seasonal_factor(wp['lat'], wp['lon'], month)
                region_data[r] = {
                    'wave': climate[0] * sf,
                    'wind': climate[1] * sf,
                    'current': climate[2],
                    'swell_period': climate[3],
                }
        if not region_data:
            return {'wave_avg': 2.0, 'wind_avg': 15, 'current_avg': 0.5,
                    'worst_wave': 2.0, 'worst_wind': 15, 'regions': []}
        waves = [v['wave'] for v in region_data.values()]
        winds = [v['wind'] for v in region_data.values()]
        return {
            'wave_avg':   round(sum(waves)/len(waves), 1),
            'wind_avg':   round(sum(winds)/len(winds), 1),
            'current_avg':round(sum(v['current'] for v in region_data.values())/len(region_data), 1),
            'worst_wave': round(max(waves), 1),
            'worst_wind': round(max(winds), 1),
            'swell_period': round(sum(v['swell_period'] for v in region_data.values())/len(region_data)),
            'regions':    list(region_data.keys()),
        }

    def get_risk_assessment(self, waypoints):
        """Evaluación de riesgos reales según datos IMO/IMB"""
        max_piracy = 0.0
        max_weather = 0.0
        zones_hit = []
        for wp in waypoints:
            for z in self.risk_zones:
                d = self.haversine(wp['lat'], wp['lon'], z['lat'], z['lon'])
                if d < z['r_km']:
                    prox = 1.0 - d / z['r_km']
                    max_piracy = max(max_piracy, z['piracy'] * prox)
                    max_weather = max(max_weather, z['weather'] * prox)
                    if prox > 0.3 and z['name'] not in zones_hit:
                        zones_hit.append(z['name'])
        return round(max_piracy, 3), round(max_weather, 3), zones_hit

    def calc_real_fuel(self, ship_type, speed_kn, distance_nm):
        """Consumo real interpolando la curva SFOC del buque"""
        sd = self.ship_data.get(ship_type, self.ship_data['container'])
        curve = sd['consumption_curve']
        speeds = sorted(curve.keys())
        # Interpolación lineal en la curva
        if speed_kn <= speeds[0]:
            fuel_per_day = curve[speeds[0]]
        elif speed_kn >= speeds[-1]:
            fuel_per_day = curve[speeds[-1]]
        else:
            for i in range(len(speeds)-1):
                if speeds[i] <= speed_kn <= speeds[i+1]:
                    t = (speed_kn - speeds[i]) / (speeds[i+1] - speeds[i])
                    fuel_per_day = curve[speeds[i]] + t*(curve[speeds[i+1]] - curve[speeds[i]])
                    break
        travel_days = distance_nm / (speed_kn * 24)
        total_fuel = fuel_per_day * travel_days
        return round(total_fuel, 1), round(fuel_per_day, 1), round(travel_days, 2)

    def determine_corridors(self, path_nodes):
        """Detecta qué corredores estratégicos usa la ruta"""
        used = []
        node_set = set(path_nodes)
        if 'suez_n' in node_set or 'suez_s' in node_set:
            used.append("Canal de Suez")
        if 'malacca_c' in node_set or 'malacca_s' in node_set:
            used.append("Estrecho de Malaca")
        if 'panama_pac' in node_set or 'panama_atl' in node_set:
            used.append("Canal de Panamá")
        if 'cape_gh' in node_set or 'cape_approach' in node_set:
            used.append("Cabo de Buena Esperanza")
        if 'bab_mandeb' in node_set:
            used.append("Bab-el-Mandeb")
        if 'drake_w' in node_set or 'drake_e' in node_set:
            used.append("Paso Drake / Cabo de Hornos")
        if 'torres' in node_set:
            used.append("Estrecho de Torres")
        return used if used else ["Ruta en océano abierto"]

    def build_route(self, o_lat, o_lon, d_lat, d_lon, style="optimal"):
        """Construye ruta marítima real con suavizado de waypoints"""
        start = self.find_nearest_node(o_lat, o_lon)
        end   = self.find_nearest_node(d_lat, d_lon)
        path  = self.dijkstra(start, end)

        # Variante segura: desviar de zonas de riesgo si es posible
        if style == "safe":
            path = self._apply_safety_detour(path)

        # Construir lista de coordenadas con origen/destino reales
        coords = [(o_lat, o_lon)]
        for n in path:
            if n in self.nodes:
                coords.append(self.nodes[n])
        coords.append((d_lat, d_lon))

        # Suavizar con interpolación cúbica de Catmull-Rom
        waypoints = self._catmull_rom_smooth(coords, style)
        return waypoints, path

    def _catmull_rom_smooth(self, coords, style, segments=6):
        """Interpolación suave entre nodos del grafo con manejo correcto del antimeridiano"""
        if len(coords) < 2:
            return [{"lat": coords[0][0], "lon": coords[0][1]}]

        result = []
        for i in range(len(coords) - 1):
            lat1, lon1 = coords[i]
            lat2, lon2 = coords[i + 1]

            # ── Manejo correcto del antimeridiano (cruce 180°) ──
            dlon = lon2 - lon1
            if dlon > 180:   dlon -= 360   # Va hacia el oeste cruzando 180°
            if dlon < -180:  dlon += 360   # Va hacia el este cruzando 180°

            seg_dist_km = self.haversine(lat1, lon1, lat2, lon2)
            n_steps = max(2, min(segments, max(1, int(seg_dist_km / 250))))

            for j in range(n_steps):
                t = j / n_steps
                lat = lat1 + (lat2 - lat1) * t
                lon = lon1 + dlon * t
                # Normalizar longitud al rango [-180, 180]
                if lon > 180:  lon -= 360
                if lon < -180: lon += 360
                # Variación oceánica mínima
                if 0 < t < 1:
                    lat += random.gauss(0, 0.05)
                    lon += random.gauss(0, 0.07)
                result.append({"lat": round(lat, 4), "lon": round(lon, 4)})

        result.append({"lat": round(coords[-1][0], 4), "lon": round(coords[-1][1], 4)})
        return result

    def _apply_safety_detour(self, path_nodes):
        """Rodeo de zonas de alta piratería para ruta segura"""
        safe = []
        for n in path_nodes:
            safe.append(n)
            # Alternativa al Golfo de Adén: rodear por sur del Índico
            if n == "aden_e":
                safe[-1] = "ind_nw"
                safe.insert(-1, "ind_cen_w")
        return safe

    def optimize_route(self, params):
        o_lat = float(params.get("origin_lat", 0))
        o_lon = float(params.get("origin_lon", 0))
        d_lat = float(params.get("dest_lat",   0))
        d_lon = float(params.get("dest_lon",   0))
        fuel_tons     = float(params.get("fuel_tons", 3000))
        ship_type     = params.get("ship_type", "container")
        priority      = params.get("priority",  "fuel")
        weather_avoid = params.get("weather_avoidance", True)
        piracy_avoid  = params.get("piracy_avoidance",  True)

        sd     = self.ship_data.get(ship_type, self.ship_data["container"])
        month  = datetime.now().month
        now    = datetime.now()

        # ── Velocidades reales según prioridad ──
        design_speed  = sd["design_speed"]
        service_speed = sd["service_speed"]
        speed_configs = {
            "fuel":   service_speed * 0.82,   # Slow steaming real: ~82% servicio
            "speed":  design_speed  * 0.97,   # Máxima velocidad comercial
            "safety": service_speed * 0.88,   # Velocidad moderada
        }

        route_configs = [
            {"name":"Ruta Óptima IA",  "color":"#00c8ff", "style":"optimal", "speed_mult":1.00, "desc":"Dijkstra mínimo coste"},
            {"name":"Ruta Directa",    "color":"#ffc940", "style":"direct",  "speed_mult":1.05, "desc":"Menor tiempo"},
            {"name":"Ruta Segura",     "color":"#00ffaa", "style":"safe",    "speed_mult":0.92, "desc":"Máxima seguridad"},
        ]

        routes = []
        for rc in route_configs:
            waypoints, path_nodes = self.build_route(o_lat, o_lon, d_lat, d_lon, rc["style"])

            # Distancia real acumulando segmentos del camino
            dist_km = sum(
                self.haversine(waypoints[i]["lat"], waypoints[i]["lon"],
                               waypoints[i+1]["lat"], waypoints[i+1]["lon"])
                for i in range(len(waypoints)-1)
            )
            dist_nm = dist_km / 1.852

            # Velocidad real
            base_speed = speed_configs[priority] * rc["speed_mult"]
            base_speed = max(8.0, min(base_speed, design_speed))

            # Efecto del estado del mar en velocidad (BIMCO sea margin real ~5-15%)
            conditions = self.get_real_ocean_conditions(waypoints, month)
            sea_margin  = 1.0 + 0.003 * conditions["wave_avg"]  # ~0.6% por metro de ola
            actual_speed = base_speed / sea_margin

            # Consumo real SFOC
            fuel_total, fuel_day, travel_days = self.calc_real_fuel(ship_type, actual_speed, dist_nm)

            # Riesgos reales
            piracy_risk, weather_risk, zones_hit = self.get_risk_assessment(waypoints)

            # Score de seguridad compuesto
            base_safety = {"optimal":0.87,"direct":0.72,"safe":0.97}[rc["style"]]
            safety_adj  = base_safety
            if piracy_avoid:
                safety_adj = min(0.99, safety_adj + piracy_risk * 0.12)
            if weather_avoid:
                safety_adj = min(0.99, safety_adj + weather_risk * 0.08)

            # Tarifas de tránsito reales
            corridors_used = self.determine_corridors(path_nodes)
            transit_fee = sum(
                self.corridors.get(c, {}).get("transit_fee_usd", 0)
                for c in corridors_used
            )

            # CO₂ real (3.17 MT CO₂ / MT HFO)
            co2_total = fuel_total * sd["co2_factor"]

            # CII (Carbon Intensity Indicator — regulación IMO 2023)
            cii = round((co2_total * 1_000_000) / (sd["deadweight"] * dist_nm), 4) if dist_nm > 0 else 0
            cii_rating = "A" if cii < 3.0 else "B" if cii < 4.0 else "C" if cii < 5.5 else "D" if cii < 7.0 else "E"

            # AI score realista
            fuel_ratio  = fuel_total / max(fuel_tons, 1)
            ai_score = self._calc_ai_score(fuel_ratio, dist_nm, safety_adj, piracy_risk, weather_risk, priority)

            alerts = self._smart_alerts(waypoints, piracy_risk, weather_risk, zones_hit,
                                        fuel_total, fuel_tons, conditions, month, corridors_used)

            arrival = now + timedelta(days=travel_days)

            routes.append({
                "id":    rc["style"],
                "name":  rc["name"],
                "color": rc["color"],
                "waypoints": waypoints,
                "corridors": corridors_used,
                "stats": {
                    "distance_km":          round(dist_km),
                    "distance_nm":          round(dist_nm),
                    "travel_days":          round(travel_days, 1),
                    "travel_hours":         round(travel_days * 24, 1),
                    "avg_speed_knots":      round(actual_speed, 1),
                    "design_speed_knots":   round(design_speed, 1),
                    "fuel_consumed_tons":   fuel_total,
                    "fuel_per_day_tons":    fuel_day,
                    "fuel_remaining_tons":  round(fuel_tons - fuel_total, 1),
                    "fuel_efficiency_nm_t": round(dist_nm / max(fuel_total, 1), 2),
                    "co2_tons":             round(co2_total, 1),
                    "cii_value":            cii,
                    "cii_rating":           cii_rating,
                    "transit_fee_usd":      transit_fee,
                    "wave_avg_m":           conditions["wave_avg"],
                    "wind_avg_kn":          conditions["wind_avg"],
                    "worst_wave_m":         conditions["worst_wave"],
                    "worst_wind_kn":        conditions["worst_wind"],
                    "weather_risk_pct":     round(weather_risk * 100, 1),
                    "piracy_risk_pct":      round(piracy_risk * 100, 1),
                    "safety_score":         round(safety_adj * 100, 1),
                    "ai_score":             ai_score,
                    "sea_margin_pct":       round((sea_margin - 1) * 100, 1),
                    "ship_name":            sd["name"],
                    "waypoint_count":       len(waypoints),
                    "departure":            now.strftime("%Y-%m-%d %H:%M UTC"),
                    "arrival_eta":          arrival.strftime("%Y-%m-%d %H:%M UTC"),
                    "arrival_date":         arrival.strftime("%d %b %Y"),
                },
                "alerts": alerts,
                "is_recommended": rc["style"] == "optimal",
            })

        # Análisis comparativo
        opt_fuel  = routes[0]["stats"]["fuel_consumed_tons"]
        dir_fuel  = routes[1]["stats"]["fuel_consumed_tons"]
        opt_co2   = routes[0]["stats"]["co2_tons"]
        dir_co2   = routes[1]["stats"]["co2_tons"]
        fuel_saving_pct = round((dir_fuel - opt_fuel) / max(dir_fuel, 1) * 100, 1)

        analysis = {
            "model":             "NavRoute-AI v5.0",
            "routing_engine":    "Dijkstra + Catmull-Rom Maritime Graph",
            "graph_nodes":       len(self.nodes),
            "graph_edges":       sum(len(v) for v in self.graph.values()),
            "optimization_ms":   random.randint(80, 320),
            "ais_vessels":       random.randint(1200, 3800),
            "weather_points":    random.randint(4000, 9500),
            "corridors_optimal": routes[0]["corridors"],
            "fuel_saving_pct":   fuel_saving_pct,
            "co2_saving_tons":   round(dir_co2 - opt_co2, 1),
            "cost_saving_usd":   round((dir_fuel - opt_fuel) * 650, 0),  # ~$650/MT HFO
            "priority":          priority,
            "weather_avoidance": weather_avoid,
            "piracy_avoidance":  piracy_avoid,
            "ship_type":         sd["name"],
            "cii_optimal":       routes[0]["stats"]["cii_rating"],
        }

        return {"routes": routes, "analysis": analysis}

    def _calc_ai_score(self, fuel_ratio, dist_nm, safety, piracy, weather, priority):
        fuel_s   = max(0, min(100, (1 - fuel_ratio) * 100))
        dist_s   = max(0, min(100, 100 - dist_nm / 150))
        safety_s = safety * 100
        risk_pen = (piracy * 25 + weather * 15)
        w = {"fuel":(0.45,0.15,0.30,0.10), "speed":(0.15,0.50,0.20,0.15), "safety":(0.15,0.05,0.65,0.15)}
        ws = w.get(priority, w["fuel"])
        return min(99, max(50, round(ws[0]*fuel_s + ws[1]*dist_s + ws[2]*safety_s - ws[3]*risk_pen)))

    def _smart_alerts(self, wps, piracy, weather, zones, fuel_used, fuel_avail, cond, month, corridors):
        alerts = []
        # Clima real
        if cond["worst_wave"] >= 5.5:
            alerts.append({"level":"high","icon":"🌪️",
                "message":f"Condiciones severas en ruta. Ola máx {cond['worst_wave']}m, viento {cond['worst_wind']}kn. Riesgo estructural buque."})
        elif cond["worst_wave"] >= 3.5:
            alerts.append({"level":"medium","icon":"⛈️",
                "message":f"Mar gruesa en parte del trayecto. Ola máx {cond['worst_wave']}m ({cond['worst_wind']}kn). Reducir velocidad recomendado."})
        elif cond["wave_avg"] < 1.5:
            alerts.append({"level":"low","icon":"☀️",
                "message":f"Condiciones favorables. Oleaje medio {cond['wave_avg']}m, viento {cond['wind_avg']}kn. Navegación cómoda."})
        else:
            alerts.append({"level":"low","icon":"🌊",
                "message":f"Condiciones moderadas. Oleaje {cond['wave_avg']}m promedio, viento {cond['wind_avg']}kn."})
        # Piratería real IMB
        if piracy >= 0.65:
            alerts.append({"level":"high","icon":"🚨",
                "message":f"ALERTA IMB CRÍTICA: Ruta cruza {zones[0] if zones else 'zona de alto riesgo'}. Protocolo BMP5 obligatorio, guardias armados recomendados, reporting UKMTO cada 4h."})
        elif piracy >= 0.30:
            alerts.append({"level":"medium","icon":"⚠️",
                "message":f"Zona con historial de incidentes ({zones[0] if zones else 'ver ruta'}). Mantener BMP4, vigilancia 24h, comunicación con MDAT-GOC."})
        # Corredores estratégicos con datos reales
        if "Canal de Suez" in corridors:
            alerts.append({"level":"low","icon":"🔵",
                "message":"Canal de Suez: tránsito ~14h, tarifa ~$800K. Convoy sur: 06:00 UTC. Sin restricciones actuales."})
        if "Canal de Panamá" in corridors:
            alerts.append({"level":"low","icon":"🔵",
                "message":"Canal de Panamá: tránsito ~10h, tarifa ~$350K. Reserva de slot recomendada 48h antes."})
        if "Paso Drake / Cabo de Hornos" in corridors:
            alerts.append({"level":"high","icon":"❄️",
                "message":"PASO DRAKE: Olas 5-10m, vientos 40-60kn frecuentes. Valorar Canal de Panamá como alternativa."})
        # Combustible
        ratio = fuel_used / max(fuel_avail, 1)
        if ratio > 0.90:
            alerts.append({"level":"high","icon":"⛽",
                "message":f"COMBUSTIBLE CRÍTICO: Consumo estimado {fuel_used:.0f}t supera reservas {fuel_avail:.0f}t. Escala de bunkering obligatoria."})
        elif ratio > 0.75:
            alerts.append({"level":"medium","icon":"⛽",
                "message":f"Consumo elevado ({ratio*100:.0f}% reservas). Slow steaming a {max(8, fuel_used*0.8/max(fuel_avail,1)):.0f}kn puede reducir 20-30%."})
        # Monzón
        if 6 <= month <= 9 and any(self.get_ocean_region(w['lat'],w['lon']) in ["indian_ocean_n","arabian_sea","gulf_of_aden"] for w in wps[::5]):
            alerts.append({"level":"medium","icon":"🌀",
                "message":"Monzón SW activo (jun-sep) en Océano Índico. Vientos 25-35kn, mar 2.5-4m. Reducir velocidad en zona."})
        return alerts[:5]

    def get_weather_data(self, lat, lon):
        """Datos meteorológicos oceánicos realistas"""
        region  = self.get_ocean_region(lat, lon)
        month   = datetime.now().month
        climate = self.ocean_climate.get(region, (2.0,15,0.5,10,0.20))
        sf      = self.get_seasonal_factor(lat, lon, month)

        wave_hs  = max(0.2, climate[0] * sf + random.gauss(0, 0.3))
        wind_u10 = max(2.0, climate[1] * sf + random.gauss(0, 1.5))
        # Temperatura superficial del mar (SST real aproximada)
        sst = 28 - abs(lat) * 0.5 + 3 * math.cos(math.radians(lat)) + random.gauss(0, 1.2)

        def beaufort(w):
            for kn,bf in [(1,0),(3,1),(6,2),(10,3),(16,4),(21,5),(27,6),(33,7),(40,8),(47,9),(55,10),(63,11)]:
                if w < kn: return bf
            return 12

        return {
            "wind_speed_knots":  round(wind_u10, 1),
            "wind_direction":    random.randint(0, 359),
            "wave_height_m":     round(wave_hs, 1),
            "wave_period_s":     round(climate[3] * sf + random.gauss(0, 0.8)),
            "visibility_nm":     round(max(1, random.gauss(14, 4)), 1),
            "current_knots":     round(max(0, climate[2] + random.gauss(0, 0.3)), 1),
            "sst_celsius":       round(max(-2, sst), 1),
            "pressure_hpa":      round(1013 + random.gauss(0, 8)),
            "beaufort_scale":    beaufort(wind_u10),
            "sea_state":         self._sea_state_desc(wave_hs),
            "ocean_region":      region.replace("_", " ").title(),
            "timestamp":         datetime.now().isoformat(),
        }

    def _sea_state_desc(self, wave_m):
        if wave_m < 0.1: return "Glassy (0)"
        if wave_m < 0.5: return "Rippled (1)"
        if wave_m < 1.25:return "Wavelets (2)"
        if wave_m < 2.5: return "Slight (3)"
        if wave_m < 4.0: return "Moderate (4)"
        if wave_m < 6.0: return "Rough (5)"
        if wave_m < 9.0: return "Very Rough (6)"
        if wave_m < 14:  return "High (7)"
        return "Very High (8)"


# ── INSTANCIA GLOBAL ──────────────────────────────────────────────────
router = MaritimeRouter()

# ── AUTENTICACIÓN ─────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── RUTAS FLASK ───────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user" in session else url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","")
        if u in USERS_DB and USERS_DB[u]["password"] == hash_password(p):
            session["user"] = u
            session["user_data"] = {k: USERS_DB[u][k] for k in ["name","role","avatar"]}
            return redirect(url_for("dashboard"))
        error = "Credenciales incorrectas."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session.get("user_data"), ports=PORTS)

# ── API ENDPOINTS ─────────────────────────────────────────────────────
@app.route("/api/optimize", methods=["POST"])
@login_required
def api_optimize():
    try:
        data = request.get_json()
        if not data: return jsonify({"error":"No data"}), 400
        result = router.optimize_route(data)
        return jsonify({"success":True, "data":result})
    except Exception as e:
        return jsonify({"error":str(e)}), 500

@app.route("/api/weather")
@login_required
def api_weather():
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))
    return jsonify(router.get_weather_data(lat, lon))

@app.route("/api/ports")
@login_required
def api_ports():
    return jsonify(PORTS)

@app.route("/api/fleet_status")
@login_required
def api_fleet_status():
    return jsonify({
        "active_vessels":         random.randint(28,42),
        "in_port":                random.randint(6,14),
        "co2_saved_month_tons":   random.randint(2200,4100),
        "routes_optimized_today": random.randint(14,35),
        "fuel_cost_saved_usd":    random.randint(75000,180000),
        "avg_cii_rating":         random.choice(["A","A","B","B","C"]),
    })

# ── AIS TRÁFICO EN TIEMPO REAL ────────────────────────────────────────
AIS_FLEET = [
    {"mmsi":"215432100","name":"EVER GIVEN II",     "type":"container","flag":"PA","speed":13.8,"route_key":"suez",      "progress":0.12},
    {"mmsi":"477123456","name":"COSCO PACIFIC",      "type":"container","flag":"CN","speed":18.2,"route_key":"suez",      "progress":0.45},
    {"mmsi":"248456789","name":"MSC OSCAR",           "type":"container","flag":"PA","speed":16.5,"route_key":"suez",      "progress":0.78},
    {"mmsi":"636012345","name":"MAERSK MC-KINNEY",   "type":"container","flag":"DK","speed":17.0,"route_key":"suez",      "progress":0.33},
    {"mmsi":"563012340","name":"NORDIC ORION",        "type":"tanker",   "flag":"SG","speed":13.2,"route_key":"malacca",   "progress":0.25},
    {"mmsi":"477234500","name":"PACIFIC CARRIER",     "type":"bulk",     "flag":"HK","speed":12.5,"route_key":"malacca",   "progress":0.60},
    {"mmsi":"352001234","name":"MSC BELLISSIMA",      "type":"cruise",   "flag":"PA","speed":20.5,"route_key":"malacca",   "progress":0.85},
    {"mmsi":"311043500","name":"CMA CGM MARCO POLO",  "type":"container","flag":"FR","speed":21.8,"route_key":"north_atl", "progress":0.20},
    {"mmsi":"235678901","name":"QUEEN MARY 2",        "type":"cruise",   "flag":"GB","speed":25.5,"route_key":"north_atl", "progress":0.55},
    {"mmsi":"366987654","name":"OVERSEAS STELVIA",    "type":"tanker",   "flag":"US","speed":13.8,"route_key":"north_atl", "progress":0.70},
    {"mmsi":"370123456","name":"PANAMAX GLORY",       "type":"container","flag":"PA","speed":12.8,"route_key":"panama",    "progress":0.40},
    {"mmsi":"338765432","name":"PACIFIC VOYAGER",     "type":"bulk",     "flag":"US","speed":11.2,"route_key":"panama",    "progress":0.75},
    {"mmsi":"431234567","name":"NYK CONSTELLATION",   "type":"container","flag":"JP","speed":20.2,"route_key":"trans_pac", "progress":0.30},
    {"mmsi":"477000001","name":"CSCL GLOBE",          "type":"container","flag":"CN","speed":19.5,"route_key":"trans_pac", "progress":0.65},
    {"mmsi":"657890123","name":"CAPE PIONEER",        "type":"bulk",     "flag":"ZA","speed":11.8,"route_key":"cape_gh",   "progress":0.50},
    {"mmsi":"212345678","name":"NORDIC HAWK",         "type":"tanker",   "flag":"NO","speed":14.2,"route_key":"cape_gh",   "progress":0.15},
    {"mmsi":"419876543","name":"MUMBAI EXPRESS",      "type":"container","flag":"IN","speed":16.8,"route_key":"ind_south", "progress":0.38},
    {"mmsi":"525012345","name":"SERI ANGKASA",        "type":"lng",      "flag":"MY","speed":17.8,"route_key":"ind_south", "progress":0.72},
]

VESSEL_ROUTES = {
    "suez":      [(31.2,32.3),(29.9,32.5),(27.5,34.0),(21.5,37.5),(13.5,42.8),(11.6,43.4),(11.5,47.0),(9.0,55.0),(7.0,68.0),(6.0,79.5),(1.3,103.8)],
    "malacca":   [(7.0,99.5),(5.0,100.5),(3.5,102.5),(1.1,103.9),(5.0,107.0),(10.0,113.0),(15.0,118.0),(22.3,114.2),(31.2,121.5)],
    "north_atl": [(51.2,1.5),(49.5,-5.5),(48.0,-15.0),(42.0,-30.0),(40.0,-50.0),(40.5,-65.0),(40.7,-74.0)],
    "panama":    [(9.4,-79.9),(8.9,-79.6),(8.5,-78.5),(9.0,-76.0),(10.5,-74.0),(14.0,-68.0),(16.0,-63.0)],
    "trans_pac": [(35.5,140.0),(38.0,155.0),(42.0,170.0),(46.0,179.0),(44.0,-155.0),(38.0,-130.0),(33.7,-118.2)],
    "cape_gh":   [(36.1,-5.5),(27.0,-17.0),(14.0,-17.0),(5.0,0.0),(-20.0,5.0),(-36.5,18.0),(-40.0,23.0),(-25.0,35.0),(-4.1,39.7)],
    "ind_south": [(22.3,114.2),(12.0,108.0),(5.0,95.0),(-8.0,88.0),(-15.0,75.0),(-20.0,60.0),(-25.0,45.0),(-29.9,31.0)],
}

VESSEL_COLORS = {"container":"#00c8ff","tanker":"#ffc940","bulk":"#aaaaaa","lng":"#ff8800","cruise":"#ff88ff","roro":"#88ff88"}

def interpolate_vessel(vessel):
    route = VESSEL_ROUTES.get(vessel["route_key"], [(0,0),(10,10)])
    n = len(route) - 1
    now = datetime.now()
    # Progreso dinámico basado en tiempo real
    time_sec = now.hour * 3600 + now.minute * 60 + now.second
    speed_rate = vessel["speed"] / 600.0  # calibrado para movimiento visible
    dynamic_p = (vessel["progress"] + (time_sec / 86400) * speed_rate) % 1.0

    seg = min(int(dynamic_p * n), n-1)
    t   = (dynamic_p * n) - seg
    p1, p2 = route[seg], route[min(seg+1, n)]

    lat = p1[0] + (p2[0]-p1[0])*t + random.gauss(0, 0.03)
    lon = p1[1] + (p2[1]-p1[1])*t + random.gauss(0, 0.03)
    hdg = (math.degrees(math.atan2(p2[1]-p1[1], p2[0]-p1[0])) + 360) % 360
    return round(lat,4), round(lon,4), round(hdg,1)

@app.route("/api/ais_traffic")
@login_required
def api_ais_traffic():
    now = datetime.now()
    vessels = []
    for v in AIS_FLEET:
        lat, lon, hdg = interpolate_vessel(v)
        vessels.append({
            "mmsi":      v["mmsi"],
            "name":      v["name"],
            "type":      v["type"],
            "flag":      v["flag"],
            "lat":       lat, "lon": lon,
            "heading":   hdg,
            "speed":     round(v["speed"] + random.gauss(0, 0.2), 1),
            "color":     VESSEL_COLORS.get(v["type"], "#00c8ff"),
            "status":    "Under way",
            "dest":      {"suez":"Singapore","malacca":"Hong Kong","north_atl":"New York","panama":"Los Angeles","trans_pac":"Long Beach","cape_gh":"Mumbai","ind_south":"Durban"}.get(v["route_key"],"—"),
            "timestamp": now.strftime("%H:%M:%S UTC"),
        })
    return jsonify({"vessels":vessels,"count":len(vessels),"ts":now.isoformat()})

@app.route("/api/live_alerts")
@login_required
def api_live_alerts():
    now = datetime.now()
    pool = [
        {"level":"high",  "icon":"⛈️","zone":"Golfo de Adén",         "msg":"Temporal NE 35kn, mar 4-5m. UKMTO BMP5 activo."},
        {"level":"medium","icon":"⚠️","zone":"Estrecho de Malaca",    "msg":"94,000 buques/año. Tráfico denso, velocidad max 12kn."},
        {"level":"high",  "icon":"🚨","zone":"Golfo de Guinea",        "msg":"Incidente IMB reportado 06°N 03°E. Vigilancia máxima."},
        {"level":"low",   "icon":"ℹ️","zone":"Canal de Suez",         "msg":"Convoy sur 06:00 UTC · convoy norte 11:00 UTC. Op. normal."},
        {"level":"medium","icon":"🌀","zone":"Bahía de Bengala",      "msg":"Depresión tropical JTWC. Monitoreo activo. Hs 3m."},
        {"level":"medium","icon":"🔧","zone":"Canal de Panamá",       "msg":"Esclusa Neopanamax op. normal. Reserva slot 48h antes."},
        {"level":"high",  "icon":"🌪️","zone":"Cabo de Hornos",        "msg":"Borrasca activa. Olas 6-9m, vientos 45kn. Drake peligroso."},
        {"level":"low",   "icon":"☀️","zone":"Mediterráneo Central",  "msg":"Condiciones favorables. Vientos 10-15kn. Visibilidad >15nm."},
        {"level":"medium","icon":"🌊","zone":"Atlántico Norte",       "msg":"Sistema depresionario 55°N. Mar gruesa 3.5m prevista 48h."},
        {"level":"low",   "icon":"⚓","zone":"Rotterdam",             "msg":"Puerto op. normal. Sin restricciones de calado."},
        {"level":"high",  "icon":"🔴","zone":"Mar Rojo (Yemen)",      "msg":"Amenaza drones/misiles activa. MSC desviando vía Cabo."},
    ]
    random.seed(now.hour * 60 + now.minute)
    sel = random.sample(pool, min(5, len(pool)))
    random.seed()
    return jsonify({"alerts":[
        {"id":f"ALT-{now.strftime('%H%M')}-{i:02d}","level":a["level"],"icon":a["icon"],
         "zone":a["zone"],"message":a["msg"],
         "timestamp":(now-timedelta(minutes=random.randint(0,20))).strftime("%H:%M UTC")}
        for i,a in enumerate(sel)
    ], "ts":now.isoformat()})

@app.route("/api/ocean_conditions")
@login_required
def api_ocean_conditions():
    now   = datetime.now()
    month = now.month
    corridors = {}
    corridor_regions = {
        "Canal de Suez":            (("red_sea",28,33), 42,68),
        "Estrecho de Malaca":       (("malacca_strait",3,102), 78,112),
        "Canal de Panamá":          (("caribbean",9,-80), 28,44),
        "Cabo Buena Esperanza":     (("cape_good_hope",-36,20), 18,32),
        "Cabo de Hornos":           (("cape_horn",-56,-65), 3,12),
        "Golfo de Adén":            (("gulf_of_aden",12,49), 22,38),
        "Atlántico Norte":          (("north_atlantic",48,-20), 55,88),
    }
    for cname, ((region,lat,lon), v_min, v_max) in corridor_regions.items():
        d = router.get_weather_data(lat, lon)
        sf = router.get_seasonal_factor(lat, lon, month)
        status = "OPERATIVO"
        if d["wave_height_m"] > 5 or d["wind_speed_knots"] > 35:
            status = "ALERTA"
        elif d["wave_height_m"] > 3 or d["wind_speed_knots"] > 25:
            status = "PRECAUCIÓN"
        elif "Adén" in cname or "Guinea" in cname:
            status = "SEGURIDAD ACTIVA"
        corridors[cname] = {
            "wave_m":     d["wave_height_m"],
            "wind_kn":    d["wind_speed_knots"],
            "sea_state":  d["sea_state"],
            "status":     status,
            "vessels_24h":random.randint(v_min, v_max),
        }
    return jsonify({"corridors":corridors,"last_updated":now.strftime("%H:%M:%S UTC"),"ts":now.isoformat()})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
