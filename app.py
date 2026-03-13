"""
NavRoute AI - Sistema de Optimización de Rutas Navales con IA
Backend Flask principal
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import hashlib
import os
import json
import random
import math
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "navroute_ai_2024_secret_key_segura")

# ─────────────────────────────────────────────
# BASE DE DATOS DE USUARIOS (en producción usar PostgreSQL/MongoDB)
# Contraseñas hasheadas con SHA-256 + salt
# ─────────────────────────────────────────────
SALT = "naval_ai_2024_secure_salt"

def hash_password(password):
    return hashlib.sha256((password + SALT).encode()).hexdigest()

USERS_DB = {
    "admin": {
        "password": hash_password("admin123"),
        "name": "Capitán Admin",
        "role": "admin",
        "avatar": "CA"
    },
    "demo": {
        "password": hash_password("demo2024"),
        "name": "Demo User",
        "role": "user",
        "avatar": "DU"
    }
}

# ─────────────────────────────────────────────
# PUERTOS GLOBALES CLAVE
# ─────────────────────────────────────────────
PORTS = {
    "rotterdam":    {"name": "Rotterdam",    "lat": 51.9,   "lon": 4.5,    "country": "Netherlands", "traffic": "high"},
    "shanghai":     {"name": "Shanghai",     "lat": 31.2,   "lon": 121.5,  "country": "China",       "traffic": "very_high"},
    "singapore":    {"name": "Singapore",    "lat": 1.3,    "lon": 103.8,  "country": "Singapore",   "traffic": "very_high"},
    "los_angeles":  {"name": "Los Ángeles",  "lat": 33.7,   "lon": -118.2, "country": "USA",         "traffic": "high"},
    "dubai":        {"name": "Dubai",        "lat": 25.0,   "lon": 55.1,   "country": "UAE",         "traffic": "high"},
    "hamburg":      {"name": "Hamburgo",     "lat": 53.5,   "lon": 10.0,   "country": "Germany",     "traffic": "high"},
    "busan":        {"name": "Busan",        "lat": 35.1,   "lon": 129.0,  "country": "South Korea", "traffic": "high"},
    "new_york":     {"name": "Nueva York",   "lat": 40.7,   "lon": -74.0,  "country": "USA",         "traffic": "high"},
    "santos":       {"name": "Santos",       "lat": -23.9,  "lon": -46.3,  "country": "Brazil",      "traffic": "medium"},
    "cape_town":    {"name": "Ciudad del Cabo","lat":-33.9,  "lon": 18.4,   "country": "South Africa","traffic": "medium"},
    "tokyo":        {"name": "Tokyo",        "lat": 35.6,   "lon": 139.7,  "country": "Japan",       "traffic": "high"},
    "mumbai":       {"name": "Mumbai",       "lat": 18.9,   "lon": 72.8,   "country": "India",       "traffic": "high"},
    "cartagena":    {"name": "Cartagena",    "lat": 10.4,   "lon": -75.5,  "country": "Colombia",    "traffic": "medium"},
    "antwerp":      {"name": "Amberes",      "lat": 51.2,   "lon": 4.4,    "country": "Belgium",     "traffic": "high"},
    "barcelona":    {"name": "Barcelona",    "lat": 41.4,   "lon": 2.2,    "country": "Spain",       "traffic": "medium"},
    "algeciras":    {"name": "Algeciras",    "lat": 36.1,   "lon": -5.5,   "country": "Spain",       "traffic": "high"},
    "valencia":     {"name": "Valencia",     "lat": 39.4,   "lon": -0.3,   "country": "Spain",       "traffic": "medium"},
    "piraeus":      {"name": "El Pireo",     "lat": 37.9,   "lon": 23.6,   "country": "Greece",      "traffic": "high"},
    "istanbul":     {"name": "Estambul",     "lat": 41.0,   "lon": 29.0,   "country": "Turkey",      "traffic": "high"},
    "jeddah":       {"name": "Yeda",         "lat": 21.5,   "lon": 39.2,   "country": "Saudi Arabia","traffic": "high"},
    "colombo":      {"name": "Colombo",      "lat": 6.9,    "lon": 79.8,   "country": "Sri Lanka",   "traffic": "medium"},
    "port_klang":   {"name": "Port Klang",   "lat": 3.0,    "lon": 101.4,  "country": "Malaysia",    "traffic": "high"},
    "hong_kong":    {"name": "Hong Kong",    "lat": 22.3,   "lon": 114.2,  "country": "China",       "traffic": "very_high"},
    "guangzhou":    {"name": "Guangzhou",    "lat": 23.1,   "lon": 113.3,  "country": "China",       "traffic": "very_high"},
    "shenzhen":     {"name": "Shenzhen",     "lat": 22.5,   "lon": 113.9,  "country": "China",       "traffic": "very_high"},
    "tanjung_pelepas":{"name":"Tanjung Pelepas","lat":1.4,  "lon": 103.5,  "country": "Malaysia",    "traffic": "high"},
    "taipei":       {"name": "Taipei/Kaohsiung","lat":22.6, "lon": 120.3,  "country": "Taiwan",      "traffic": "high"},
    "osaka":        {"name": "Osaka",        "lat": 34.7,   "lon": 135.4,  "country": "Japan",       "traffic": "high"},
    "seattle":      {"name": "Seattle",      "lat": 47.6,   "lon": -122.3, "country": "USA",         "traffic": "medium"},
    "long_beach":   {"name": "Long Beach",   "lat": 33.8,   "lon": -118.2, "country": "USA",         "traffic": "high"},
    "miami":        {"name": "Miami",        "lat": 25.8,   "lon": -80.2,  "country": "USA",         "traffic": "medium"},
    "savannah":     {"name": "Savannah",     "lat": 32.1,   "lon": -81.1,  "country": "USA",         "traffic": "medium"},
    "montreal":     {"name": "Montreal",     "lat": 45.5,   "lon": -73.6,  "country": "Canada",      "traffic": "medium"},
    "colon":        {"name": "Colón",        "lat": 9.4,    "lon": -79.9,  "country": "Panama",      "traffic": "high"},
    "manzanillo":   {"name": "Manzanillo",   "lat": 19.1,   "lon": -104.3, "country": "Mexico",      "traffic": "medium"},
    "valparaiso":   {"name": "Valparaíso",   "lat": -33.0,  "lon": -71.6,  "country": "Chile",       "traffic": "medium"},
    "buenos_aires": {"name": "Buenos Aires", "lat": -34.6,  "lon": -58.4,  "country": "Argentina",   "traffic": "medium"},
    "durban":       {"name": "Durban",       "lat": -29.9,  "lon": 31.0,   "country": "South Africa","traffic": "medium"},
    "mombasa":      {"name": "Mombasa",      "lat": -4.1,   "lon": 39.7,   "country": "Kenya",       "traffic": "medium"},
    "lagos":        {"name": "Lagos",        "lat": 6.5,    "lon": 3.4,    "country": "Nigeria",     "traffic": "medium"},
    "dakar":        {"name": "Dakar",        "lat": 14.7,   "lon": -17.4,  "country": "Senegal",     "traffic": "medium"},
    "sydney":       {"name": "Sydney",       "lat": -33.9,  "lon": 151.2,  "country": "Australia",   "traffic": "medium"},
    "melbourne":    {"name": "Melbourne",    "lat": -37.8,  "lon": 144.9,  "country": "Australia",   "traffic": "medium"},
    "auckland":     {"name": "Auckland",     "lat": -36.8,  "lon": 174.8,  "country": "New Zealand", "traffic": "low"},
    "vancouver":    {"name": "Vancouver",    "lat": 49.3,   "lon": -123.1, "country": "Canada",      "traffic": "medium"},
}

# ─────────────────────────────────────────────
# MOTOR DE IA PARA OPTIMIZACIÓN DE RUTAS
# Simula un modelo ML con lógica geoespacial real
# ─────────────────────────────────────────────
class NavRouteAI:
    
    def __init__(self):
        self.weather_zones = self._init_weather_zones()
        self.piracy_zones = self._init_piracy_zones()
    
    def _init_weather_zones(self):
        """Zonas meteorológicas con riesgo histórico"""
        return [
            {"name": "Cabo de Hornos",    "lat": -56, "lon": -67, "radius": 8,  "risk": 0.9,  "type": "storm"},
            {"name": "Golfo de Bengala",  "lat": 15,  "lon": 88,  "radius": 10, "risk": 0.6,  "type": "cyclone"},
            {"name": "Mar del Norte",     "lat": 57,  "lon": 3,   "radius": 6,  "risk": 0.7,  "type": "gale"},
            {"name": "Pacífico Norte",    "lat": 42,  "lon": -160,"radius": 15, "risk": 0.5,  "type": "storm"},
            {"name": "Golfo de México",   "lat": 25,  "lon": -90, "radius": 8,  "risk": 0.4,  "type": "hurricane"},
            {"name": "Mar Arábigo",       "lat": 18,  "lon": 65,  "radius": 7,  "risk": 0.3,  "type": "cyclone"},
        ]
    
    def _init_piracy_zones(self):
        """Zonas de riesgo de piratería (datos históricos IMO)"""
        return [
            {"name": "Golfo de Adén",     "lat": 12,  "lon": 48,  "radius": 5,  "risk": 0.8},
            {"name": "Estrecho de Malaca","lat": 3,   "lon": 103, "radius": 4,  "risk": 0.5},
            {"name": "Golfo de Guinea",   "lat": 3,   "lon": 5,   "radius": 8,  "risk": 0.7},
        ]
    
    def haversine(self, lat1, lon1, lat2, lon2):
        """Distancia real entre dos puntos geográficos en km"""
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.asin(math.sqrt(a))
    
    def _zone_risk(self, lat, lon, zones):
        """Calcula riesgo acumulado de zonas cercanas"""
        total_risk = 0
        for z in zones:
            dist = self.haversine(lat, lon, z["lat"], z["lon"])
            if dist < z["radius"] * 111:  # convertir grados a km aprox
                proximity = 1 - (dist / (z["radius"] * 111))
                total_risk += z["risk"] * proximity
        return min(total_risk, 1.0)
    
    def _generate_waypoints(self, lat1, lon1, lat2, lon2, n_points=12):
        """Genera waypoints con interpolación esférica (Great Circle)"""
        waypoints = []
        for i in range(n_points + 1):
            t = i / n_points
            # Interpolación Great Circle simplificada
            lat = lat1 + t * (lat2 - lat1)
            lon = lon1 + t * (lon2 - lon1)
            # Curvatura natural de rutas marítimas
            if 0.1 < t < 0.9:
                lat += random.gauss(0, 0.3)
                lon += random.gauss(0, 0.5)
            waypoints.append({"lat": round(lat, 3), "lon": round(lon, 3)})
        return waypoints
    
    def _avoid_land(self, waypoints):
        """Ajusta waypoints para evitar masas terrestres conocidas"""
        adjusted = []
        for wp in waypoints:
            lat, lon = wp["lat"], wp["lon"]
            # Evitar Australia (simplificado)
            if -35 < lat < -10 and 114 < lon < 153:
                lon = 110 if lon < 130 else 155
            # Evitar América del Sur costa
            if -55 < lat < 10 and -80 < lon < -40:
                if lon > -70:
                    lon = -78
            adjusted.append({"lat": round(lat, 3), "lon": round(lon, 3)})
        return adjusted
    
    def optimize_route(self, params):
        """
        Motor principal de optimización de ruta naval
        
        Parámetros de entrada:
        - origin_lat, origin_lon: Coordenadas de origen
        - dest_lat, dest_lon: Coordenadas de destino  
        - fuel_tons: Combustible disponible en toneladas
        - ship_type: Tipo de buque
        - priority: 'fuel' | 'speed' | 'safety'
        - weather_avoidance: bool
        - piracy_avoidance: bool
        """
        
        o_lat = float(params.get("origin_lat", 0))
        o_lon = float(params.get("origin_lon", 0))
        d_lat = float(params.get("dest_lat", 0))
        d_lon = float(params.get("dest_lon", 0))
        fuel_tons = float(params.get("fuel_tons", 500))
        ship_type = params.get("ship_type", "container")
        priority = params.get("priority", "fuel")
        weather_avoid = params.get("weather_avoidance", True)
        piracy_avoid = params.get("piracy_avoidance", True)
        
        # Distancia base (Great Circle)
        base_dist = self.haversine(o_lat, o_lon, d_lat, d_lon)
        
        # Factor de ajuste por tipo de buque
        ship_factors = {
            "container":  {"speed": 22, "consumption": 150, "name": "Portacontenedores"},
            "tanker":     {"speed": 16, "consumption": 80,  "name": "Buque Tanque"},
            "bulk":       {"speed": 14, "consumption": 60,  "name": "Granelero"},
            "lng":        {"speed": 19, "consumption": 120, "name": "Buque LNG"},
            "roro":       {"speed": 20, "consumption": 100, "name": "RoRo"},
            "cruise":     {"speed": 23, "consumption": 200, "name": "Crucero"},
        }
        sf = ship_factors.get(ship_type, ship_factors["container"])
        
        # Generar 3 rutas candidatas con diferentes estrategias
        routes = []
        
        strategies = [
            {"name": "Ruta Óptima IA", "color": "#00d4ff", "style": "optimal",
             "dist_mult": 1.05, "fuel_mult": 0.85, "safety_mult": 0.90},
            {"name": "Ruta Directa",   "color": "#ffd700", "style": "direct",
             "dist_mult": 1.00, "fuel_mult": 1.00, "safety_mult": 0.75},
            {"name": "Ruta Segura",    "color": "#00ff9d", "style": "safe",
             "dist_mult": 1.15, "fuel_mult": 1.05, "safety_mult": 0.98},
        ]
        
        for s in strategies:
            actual_dist = base_dist * s["dist_mult"]
            actual_speed = sf["speed"] * (0.9 if priority == "fuel" else 1.0)
            
            travel_hours = actual_dist / (actual_speed * 1.852)  # knots to km/h
            
            # Consumo de combustible (toneladas)
            fuel_consumed = (sf["consumption"] * travel_hours / 24) * s["fuel_mult"]
            
            # Score de IA (0-100)
            ai_score = self._calculate_ai_score(
                actual_dist, fuel_consumed, s["safety_mult"], 
                fuel_tons, priority
            )
            
            # Generar waypoints para esta ruta
            waypoints = self._generate_waypoints(o_lat, o_lon, d_lat, d_lon, 14)
            waypoints = self._avoid_land(waypoints)
            
            # Calcular riesgo meteorológico a lo largo de la ruta
            weather_risk = max(
                self._zone_risk(wp["lat"], wp["lon"], self.weather_zones) 
                for wp in waypoints[2:-2]
            )
            piracy_risk = max(
                self._zone_risk(wp["lat"], wp["lon"], self.piracy_zones) 
                for wp in waypoints[2:-2]
            )
            
            # Generar alertas contextuales
            alerts = self._generate_alerts(waypoints, weather_risk, piracy_risk, fuel_consumed, fuel_tons)
            
            # ETA
            departure = datetime.now()
            arrival = departure + timedelta(hours=travel_hours)
            
            routes.append({
                "id": s["style"],
                "name": s["name"],
                "color": s["color"],
                "waypoints": waypoints,
                "stats": {
                    "distance_km": round(actual_dist),
                    "distance_nm": round(actual_dist / 1.852),
                    "travel_hours": round(travel_hours, 1),
                    "travel_days": round(travel_hours / 24, 1),
                    "fuel_consumed_tons": round(fuel_consumed, 1),
                    "fuel_remaining_tons": round(fuel_tons - fuel_consumed, 1),
                    "fuel_efficiency": round((actual_dist / 1.852) / fuel_consumed, 2),
                    "avg_speed_knots": round(actual_speed, 1),
                    "co2_tons": round(fuel_consumed * 3.1, 1),
                    "weather_risk_pct": round(weather_risk * 100, 1),
                    "piracy_risk_pct": round(piracy_risk * 100, 1),
                    "safety_score": round(s["safety_mult"] * 100, 1),
                    "ai_score": ai_score,
                    "departure": departure.strftime("%Y-%m-%d %H:%M UTC"),
                    "arrival_eta": arrival.strftime("%Y-%m-%d %H:%M UTC"),
                    "ship_type": sf["name"],
                },
                "alerts": alerts,
                "is_recommended": s["style"] == "optimal"
            })
        
        # Metadata del análisis IA
        analysis = {
            "model": "NavRoute-AI v2.4",
            "optimization_time_ms": random.randint(280, 850),
            "weather_data_points": random.randint(1200, 2800),
            "ais_vessels_analyzed": random.randint(340, 980),
            "fuel_saving_vs_direct": round(
                (routes[1]["stats"]["fuel_consumed_tons"] - routes[0]["stats"]["fuel_consumed_tons"])
                / routes[1]["stats"]["fuel_consumed_tons"] * 100, 1
            ),
            "co2_saved_vs_direct_tons": round(
                routes[1]["stats"]["co2_tons"] - routes[0]["stats"]["co2_tons"], 1
            ),
            "priority_mode": priority,
            "weather_avoidance": weather_avoid,
            "piracy_avoidance": piracy_avoid,
        }
        
        return {"routes": routes, "analysis": analysis}
    
    def _calculate_ai_score(self, dist, fuel, safety, fuel_avail, priority):
        """Score compuesto de IA para ranking de rutas (0-100)"""
        fuel_score = max(0, min(100, (1 - fuel/fuel_avail) * 100)) if fuel_avail > 0 else 0
        dist_score = max(0, 100 - (dist / 200))
        safety_score = safety * 100
        
        weights = {"fuel": (0.5, 0.2, 0.3), "speed": (0.2, 0.5, 0.3), "safety": (0.2, 0.1, 0.7)}
        w = weights.get(priority, weights["fuel"])
        
        score = w[0]*fuel_score + w[1]*dist_score + w[2]*safety_score
        return min(99, max(60, round(score)))
    
    def _generate_alerts(self, waypoints, weather_risk, piracy_risk, fuel_used, fuel_avail):
        """Genera alertas contextuales inteligentes"""
        alerts = []
        
        if weather_risk > 0.6:
            alerts.append({
                "type": "weather", "level": "high",
                "icon": "⛈️",
                "message": f"Zona de alta actividad meteorológica detectada. Oleaje estimado 4-6m.",
            })
        elif weather_risk > 0.3:
            alerts.append({
                "type": "weather", "level": "medium",
                "icon": "🌊",
                "message": "Vientos moderados previstos en parte del trayecto (Fuerza 5-6 Beaufort).",
            })
        
        if piracy_risk > 0.5:
            alerts.append({
                "type": "security", "level": "high",
                "icon": "🚨",
                "message": "Zona de alta actividad de piratería reportada. Recomendado protocolo BMP5.",
            })
        elif piracy_risk > 0.2:
            alerts.append({
                "type": "security", "level": "medium",
                "icon": "⚠️",
                "message": "Zona con historial de incidentes marítimos menores. Mantener vigilancia.",
            })
        
        fuel_ratio = fuel_used / fuel_avail if fuel_avail > 0 else 1
        if fuel_ratio > 0.9:
            alerts.append({
                "type": "fuel", "level": "critical",
                "icon": "⛽",
                "message": f"Combustible insuficiente. Recomendada escala de reabastecimiento.",
            })
        elif fuel_ratio > 0.75:
            alerts.append({
                "type": "fuel", "level": "medium",
                "icon": "⛽",
                "message": "Consumo elevado. Reducir velocidad a Slow Steaming puede ahorrar 15-20%.",
            })
        
        if not alerts:
            alerts.append({
                "type": "ok", "level": "low",
                "icon": "✅",
                "message": "Condiciones favorables. Ruta limpia sin alertas significativas.",
            })
        
        return alerts
    
    def get_weather_data(self, lat, lon):
        """Simula datos meteorológicos en tiempo real (en producción: OpenWeatherMap API)"""
        # Variación estacional simplificada
        month = datetime.now().month
        season_factor = 1 + 0.3 * math.sin(2 * math.pi * month / 12)
        
        return {
            "wind_speed_knots": round(random.uniform(5, 25) * season_factor, 1),
            "wind_direction": random.randint(0, 359),
            "wave_height_m": round(random.uniform(0.5, 5) * season_factor, 1),
            "wave_period_s": random.randint(6, 18),
            "visibility_nm": round(random.uniform(5, 20), 1),
            "current_knots": round(random.uniform(0, 3), 1),
            "temperature_c": round(15 + 15 * math.cos(math.radians(lat)) + random.gauss(0, 3), 1),
            "pressure_hpa": random.randint(995, 1025),
            "timestamp": datetime.now().isoformat(),
        }

# Instancia global del motor IA
ai_engine = NavRouteAI()

# ─────────────────────────────────────────────
# DECORADOR DE AUTENTICACIÓN
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ─────────────────────────────────────────────
# RUTAS DE LA APLICACIÓN
# ─────────────────────────────────────────────

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if username in USERS_DB:
            if USERS_DB[username]["password"] == hash_password(password):
                session["user"] = username
                session["user_data"] = {
                    "name": USERS_DB[username]["name"],
                    "role": USERS_DB[username]["role"],
                    "avatar": USERS_DB[username]["avatar"]
                }
                return redirect(url_for("dashboard"))
        error = "Credenciales incorrectas. Verifique usuario y contraseña."
    
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", 
                         user=session.get("user_data"),
                         ports=PORTS)

# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────

@app.route("/api/optimize", methods=["POST"])
@login_required
def api_optimize():
    """Endpoint principal de optimización de rutas"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        result = ai_engine.optimize_route(data)
        return jsonify({"success": True, "data": result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/weather", methods=["GET"])
@login_required
def api_weather():
    """Datos meteorológicos para un punto geográfico"""
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))
    data = ai_engine.get_weather_data(lat, lon)
    return jsonify(data)

@app.route("/api/ports", methods=["GET"])
@login_required
def api_ports():
    """Lista de puertos globales"""
    return jsonify(PORTS)

@app.route("/api/fleet_status", methods=["GET"])
@login_required
def api_fleet_status():
    """Estado simulado de flota (para dashboard KPIs)"""
    return jsonify({
        "active_vessels": random.randint(24, 38),
        "in_port": random.randint(5, 12),
        "avg_fuel_efficiency": round(random.uniform(0.42, 0.58), 2),
        "co2_saved_month_tons": random.randint(1200, 2800),
        "routes_optimized_today": random.randint(8, 24),
        "safety_incidents_month": random.randint(0, 2),
        "fuel_cost_saved_usd": random.randint(45000, 120000),
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
