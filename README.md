
# Proyecto Centinela de Incendios Forestales

**Universidad Santo Tomás — Maestría en Ciencia de Datos**  
**Asignatura:** Profundización I: Redes Neuronales — Deep Learning  
**Entrega:** Paso 0 — Propuesta de Datos

## 0. Encabezado
| Campo | Información |
|---|---|
| Título | Centinela de Incendios Forestales: Sistema de Alerta Temprana mediante Deep Learning |
| Integrantes | Isabella Jiménez Cortés, Juan David Bernal y David Felipe Tautiva |
| Fecha | 2026-10-31 |
| Versión | v1 — Propuesta para aprobación |

## 1. Problema, cliente y objetivo binario

**Evento de riesgo y cliente:** Se propone anticipar la aparición de focos de calor compatibles con incendios de vegetación en el departamento del Meta, como apoyo a las autoridades ambientales y organismos territoriales de gestión del riesgo.
**Impacto para el cliente:** La identificación anticipada de zonas con mayor probabilidad de registrar actividad térmica permitiría priorizar el monitoreo y orientar acciones preventivas.
**Objetivo binario:** Estimar si una cuadrícula geográfica de 2 × 2 km registrará al menos una detección VIIRS S-NPP clasificada como presunto fuego de vegetación durante los siete días posteriores a la fecha de referencia.

| Etiqueta | Definición |
|---|---|
| 1 — Riesgo | Se registra al menos una detección compatible con fuego de vegetación en los siguientes siete días. |
| 0 — Sin detección registrada | No se registra ninguna detección de esa categoría durante el mismo periodo. |

El umbral de al menos una detección se justifica por la necesidad de identificar tempranamente posibles eventos. Es importante tener en cuenta que una detección satelital no equivale necesariamente a un incendio forestal confirmado y que su ausencia no garantiza que no haya ocurrido un incendio.

## 2. Las dos modalidades del sistema completo

| Modalidad | Instrumento | Información y señal aportada |
|---|---|---|
| **Rama de imagen** | Sentinel-2 MSI L2A — Copernicus | Imágenes multiespectrales que describen la cobertura vegetal, la distribución espacial de la superficie y los contrastes espectrales asociados con el estado de la vegetación. |
| **Rama temporal** | NASA POWER — productos meteorológicos | Series diarias de temperatura (T2M), humedad relativa (RH2M) y precipitación (PRECTOTCORR), que permiten estudiar las condiciones climáticas anteriores al evento. |

**Pregunta de control: ¿la imagen contiene algo que un número no contenga?**
Sí. Las imágenes conservan información sobre patrones, heterogeneidad y distribución espacial de la vegetación que no puede reconstruirse únicamente con los indicadores climáticos agregados. Ambas modalidades proceden de sistemas de observación distintos y aportan información complementaria.

## 3. Fuentes (con enlaces y licencia)

| Modalidad | Fuente (productor primario) | Enlace o DOI | Licencia y versión | Dónde se verificó la licencia | ¿Datos de personas? |
|---|---|---|---|---|---|
| Imagen | Comisión Europea / ESA — Copernicus Sentinel-2 MSI L2A | [Copernicus Data Space](https://dataspace.copernicus.eu/) | Aviso legal sobre el uso de datos Copernicus Sentinel; acceso libre, completo y abierto, conforme al Reglamento (UE) 2021/696 | [Condiciones oficiales](https://dataspace.copernicus.eu/terms-and-conditions) | No |
| Temporal | NASA — POWER | [NASA POWER](https://power.larc.nasa.gov/) | Política de datos científicos abiertos de NASA; verificar condiciones específicas del producto | [Portal oficial NASA POWER](https://power.larc.nasa.gov/) | No |
| Etiqueta complementaria | NASA — FIRMS, VIIRS S-NPP | [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/download/) | Política de acceso y uso de datos científicos de NASA; verificar atribución específica de FIRMS/VIIRS | [Portal oficial NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) | No |

## 4. Por qué NO es un reto resuelto

El proyecto requiere construir un conjunto de datos propio mediante el acoplamiento espacial y temporal de imágenes Sentinel-2, registros meteorológicos NASA POWER y detecciones térmicas NASA FIRMS. Los archivos se obtienen directamente de los productores oficiales y no de conjuntos de datos preprocesados de Kaggle.
Los datos necesitan análisis exploratorio y procesamiento: identificación de nubes y sombras, diferencias de resolución espacial, revisión de valores faltantes, posible desbalance de clases, validación de detecciones térmicas y control de fuga temporal.

## 5. Plan de la Fase 1, clave de alineación y prueba de acoplamiento
### Modalidad seleccionada para la Fase 1

Para la primera fase se utilizarán las series temporales climáticas de NASA POWER, transformadas en características tabulares para entrenar una red neuronal multicapa (MLP) en PyTorch. Se considerarán variables como temperatura media, humedad relativa media y precipitación acumulada durante los siete días anteriores a la fecha de referencia.
En la Fase 2 se incorporarán las imágenes multiespectrales Sentinel-2 mediante una CNN y las secuencias climáticas mediante una LSTM o GRU, permitiendo integrar información espacial y temporal.

### Clave de alineación
**Tipo de clave:** Por muestra, mediante correspondencia espacial y temporal.
**Clave propuesta:** `(id_cuadricula, fecha_referencia)`.

| Componente | Criterio de alineación |
|---|---|
| Unidad espacial | Cuadrículas de 2 × 2 km en el departamento del Meta |
| Fecha de referencia | Día en el que se genera la predicción |
| Imagen Sentinel-2 | Imagen adquirida antes de la fecha de referencia |
| Serie NASA POWER | Registros climáticos de los siete días anteriores, incluida la fecha de referencia |
| Etiqueta NASA FIRMS | Presencia (1) o ausencia de detecciones registradas (0) en los siete días posteriores |

La integración se realizará mediante coordenadas geográficas y fechas, utilizando únicamente información disponible antes del periodo de predicción para evitar fuga de información.

### Prueba de acoplamiento de datos reales
Se desarrolló una prueba piloto con información de enero de 2024:

| Elemento | Evidencia obtenida |
|---|---|
| NASA FIRMS | Diez cuadrículas piloto con etiquetas binarias preliminares |
| NASA POWER | Diez consultas con información climática completa del 9 al 15 de enero de 2024 |
| Sentinel-2 | Una cuadrícula con imagen multiespectral del 10 de enero de 2024 |
| Integración | Una observación multimodal preliminar |
| Validación pendiente | Completar las diez uniones reales entre imágenes, series climáticas y etiquetas |

**Estado:** Las tres fuentes demostraron disponibilidad y compatibilidad inicial. La prueba de diez registros multimodales se encuentra parcialmente completada y deberá documentarse en el Anexo A, con identificadores, fechas, coordenadas y evidencias de correspondencia.
La muestra piloto se utilizará únicamente para verificar la viabilidad de la integración. Para el entrenamiento posterior se ampliará el número de observaciones y periodos, aplicando una separación cronológica entre entrenamiento, validación y prueba.



## 6. Línea base comprometida

| Referencia | Compromiso |
|---|---|
| Clase mayoritaria | Reportar en el conjunto de prueba su exactitud y el recall de la clase de riesgo. |
| Modalidad aplanada | Serie temporal climática resumida en características tabulares. |
| Escalar crudo | Evaluar la precipitación acumulada de los siete días previos como predictor único, con umbral elegido en validación. |
| Modelo principal | Comparar las referencias anteriores con el desempeño de un MLP. |

Se conservarán la partición temporal, la semilla y los resultados de las líneas base para comparar posteriormente con la arquitectura multimodal de la Fase 2.

## 7. Riesgos éticos y protección de datos

| Riesgo | Daño para el cliente | Mitigación |
|---|---|---|
| Sesgo de muestreo o representatividad | Generalización deficiente a otras temporadas o regiones del país. | Ampliar el periodo histórico, evaluar por regiones y controlar el desbalance. |
| Falsa alarma | Priorización innecesaria de recursos de vigilancia y prevención. | Evaluar precisión, ajustar umbrales y comunicar la incertidumbre. |
| Alarma omitida | Una zona con actividad térmica podría no recibir seguimiento oportuno. | Evaluar sensibilidad, falsos negativos y desempeño por territorio. |

**Protección de datos:** Las fuentes seleccionadas contienen información satelital y meteorológica, no registros de personas identificables. Se aplicará el checklist de protección de datos personales conforme a la Ley 1581 de 2012, documentado por separado para cada fuente en el Anexo C.
El sistema tendrá un alcance académico experimental y no sustituirá las alertas ni las decisiones de las autoridades competentes.

## 8. Cita APA 7 de cada fuente

European Commission. (s. f.). *Copernicus Data Space Ecosystem* [Plataforma de datos satelitales]. https://dataspace.copernicus.eu/

National Aeronautics and Space Administration. (s. f.). *NASA POWER: Prediction Of Worldwide Energy Resources* [Base de datos meteorológicos]. https://power.larc.nasa.gov/

National Aeronautics and Space Administration. (s. f.). *Fire Information for Resource Management System (FIRMS)* [Base de datos de detecciones térmicas]. https://firms.modaps.eosdis.nasa.gov/
