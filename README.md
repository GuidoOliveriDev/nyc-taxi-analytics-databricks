# NYC Taxi Analytics — Databricks Lakehouse Demo

Proyecto end-to-end de análisis de viajes de taxi en NYC usando 
Databricks Free Edition y arquitectura medallion (Bronze / Silver / Gold).

## 📊 Dashboard

![Dashboard](dashboard/dashboard_overview.png)

## 🛠️ Stack

- **Databricks Free Edition** (Serverless compute)
- **Delta Lake** (formato de tabla con ACID + time travel)
- **Databricks SQL**
- **AI/BI Dashboards** (visualización nativa)

## 🏗️ Arquitectura Medallion

**Bronze** (`trips_bronze`)  
Ingesta cruda desde `samples.nyctaxi.trips`, sin transformaciones. 
Source of truth, permite reprocesar las capas superiores si cambia la lógica.

**Silver** (`trips_silver`)  
Datos limpios y enriquecidos: filtrado de outliers (fares negativos, 
distancias en cero, viajes con timestamp inválido) y columnas derivadas 
(duración del viaje en minutos, hora y fecha del pickup).

**Gold** (`daily_metrics`, `hourly_patterns`)  
Agregaciones de negocio listas para consumo en dashboards: métricas 
diarias y patrones horarios.

## ❓ Preguntas de negocio respondidas

1. ¿Cómo evoluciona el revenue diario a lo largo del período?
2. ¿Cuáles son las horas más rentables por día de la semana?
3. ¿Qué zonas (por ZIP code) generan más demanda y revenue?
4. ¿Cuáles son las rutas origen-destino más frecuentes?

## 📁 Estructura del repo
