# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks notebook source
# MAGIC
# MAGIC # 05 — Eager (pandas) vs Lazy (Spark)
# MAGIC Notebook demostrativo, independiente de las capas medallion.
# MAGIC Objetivo: mostrar concretamente, con tiempos y `.explain()`, por qué
# MAGIC **Spark es lazy** (arma un plan y no ejecuta hasta que hay una *acción*)
# MAGIC y **pandas es eager** (ejecuta cada línea al instante, todo en memoria).
# MAGIC
# MAGIC Lee desde `workspace.taxi_demo.trips_silver`. No modifica ninguna tabla.

# COMMAND ----------

import time
from pyspark.sql import functions as F

# Apunto a la tabla Silver ya existente del proyecto 
df_spark = spark.table("workspace.taxi_demo.trips_silver")

df_spark.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Spark es lazy
# MAGIC Definir transformaciones (`filter`, `withColumn`, `select`) no ejecuta nada.
# MAGIC Spark solo construye un plan de ejecución y lo guarda.

# COMMAND ----------

# Encadeno varias transformaciones y mido cuánto tarda definirlas
t0 = time.time()

viajes_largos = (
    df_spark
    .filter(F.col("trip_distance") > 5)
    .withColumn("fare_por_milla", F.col("fare_amount") / F.col("trip_distance"))
    .select("trip_distance", "fare_amount", "fare_por_milla")
)

t1 = time.time()
print(f"Definir las transformaciones tardó: {t1 - t0:.4f} s")
print(">>> Spark no ejecutó nada todavía. Solo armó un plan en memoria.")

# COMMAND ----------

# Prueba definitiva de que es lazy: el plan existe pero todavía no corrió.
# .explain() muestra el plan físico que Spark ejecutaría si hubiera una acción.
# En el output, busca la línea "Physical Plan" para ver lo que ejecutaría Spark.
viajes_largos.explain()

# COMMAND ----------

# Recién una acción dispara la ejecución del plan.
# Acciones típicas: count(), show(), collect(), toPandas(), write.
t0 = time.time()
total = viajes_largos.count()          # esto ejecuta el plan
t1 = time.time()

print(f"count() = {total:,} filas")
print(f"La acción tardó: {t1 - t0:.4f} s  <-- recién acá Spark trabajó de verdad")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Pandas es eager
# MAGIC Cada línea se ejecuta apenas la corrés. No hay plan diferido, no hay "acciones".

# COMMAND ----------

import pandas as pd

# traigo una muestra chica a pandas. Ojo: toPandas() también es una acción de Spark
# (por eso esta línea tarda: ejecuta el plan y materializa los datos en memoria).
pdf = viajes_largos.limit(1000).toPandas()
print(type(pdf))   # pandas.core.frame.DataFrame -> ya vive en memoria, local

# COMMAND ----------

# En pandas, cada operación se ejecuta ya. No hay que pedir ninguna acción.
t0 = time.time()

pdf["fare_por_milla_redondeado"] = pdf["fare_por_milla"].round(2)
resultado = (
    pdf
    .groupby(pd.cut(pdf["trip_distance"], bins=[5, 10, 20, 50]), observed=True)["fare_amount"]
    .mean()
)

t1 = time.time()
print(resultado)
print(f">>> pandas ejecutó cada línea al instante (eager). Tardó: {t1 - t0:.4f} s")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusión
# MAGIC
# MAGIC | | Spark (DataFrame API) | Pandas |
# MAGIC |---|---|---|
# MAGIC | Evaluación | **Lazy**: arma un plan, no ejecuta | **Eager**: ejecuta cada línea |
# MAGIC | Dispara ejecución | una *acción* (`count`, `show`, `collect`, `toPandas`, `write`) | cualquier línea |
# MAGIC | Dónde vive la data | distribuida en el cluster | en memoria local |
# MAGIC | Escala | TB / billones de filas | lo que entra en RAM |
# MAGIC
# MAGIC **Por qué importa:** la pereza de Spark le permite optimizar todo el plan
# MAGIC antes de correrlo (predicate pushdown, column pruning, etc.) y escalar a
# MAGIC datasets que no entran en una sola máquina. 
# MAGIC Pandas es perfecto para datos chicos y análisis interactivo, pero todo tiene que entrar en memoria.