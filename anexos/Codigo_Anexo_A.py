"""Reproduce las 10 filas exploratorias de imagen-clima del Anexo A.
Entradas: dos ZIP originales Copernicus, CSV de cuadriculas, CSV de 9 con clima
salida: CSV.
"""
from pathlib import Path
import hashlib, io, zipfile
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import box, mapping
from shapely.ops import transform
from pyproj import Transformer
ROOT=Path('/mnt/data')
base=pd.read_csv(ROOT/'Centinela_malla_2km_10_observaciones_preliminares.csv')
prev=pd.read_csv(ROOT/'ANEXO_A_nueve_cuadriculas_imagen_clima_preliminar.csv')
rows=[]
for _,r in base.iterrows():
    folder='Browser_images (4).zip' if r['id']=='META_PILOTO_05' else 'Browser_images (3).zip'
    with zipfile.ZipFile(ROOT/folder) as z:
        arrays={};meta=None
        for name in z.namelist():
            for band in ('B02','B03','B04','B08','B11'):
                if f'L2A_{band}_(Raw)' in name:
                    with rasterio.open(io.BytesIO(z.read(name))) as src:
                        arrays[band]=src.read(1).astype(np.float64)
                        if meta is None:meta=(src.crs,src.transform,src.shape,src.bounds)
        assert len(arrays)==5, (folder,arrays.keys())
        crs,affine,shape,bounds=meta
        assert all(a.shape==shape for a in arrays.values())
        geom=transform(Transformer.from_crs('EPSG:32619',crs,always_xy=True).transform,box(r.utm_x_min,r.utm_y_min,r.utm_x_max,r.utm_y_max))
        within=geometry_mask([mapping(geom)],out_shape=shape,transform=affine,invert=True)
        good=within.copy()
        for a in arrays.values():good &= np.isfinite(a)&(a>0)
        with np.errstate(divide='ignore',invalid='ignore'):
            ndvi=(arrays['B08']-arrays['B04'])/(arrays['B08']+arrays['B04'])
            ndmi=(arrays['B08']-arrays['B11'])/(arrays['B08']+arrays['B11'])
        good &= np.isfinite(ndvi)&np.isfinite(ndmi)
        n=int(good.sum()); total=int(within.sum())
        assert n>0, r['id']
        climate=prev.loc[prev.id==r['id']].iloc[0]
        rows.append(dict(id=r['id'],fecha_referencia=r['fecha_referencia'],fecha_imagen='2024-01-10',zip_origen=folder,clave=f"({r['id']}, {r['fecha_referencia']})",latitud_centro=float(r.latitud_centro),longitud_centro=float(r.longitud_centro),pixeles_en_recorte=total,pixeles_espectrales_validos=n,ndvi_medio_preliminar=round(float(np.mean(ndvi[good])),4),ndmi_medio_preliminar=round(float(np.mean(ndmi[good])),4),temperatura_media_7d=round(float(climate.temperatura_media_7d),6),humedad_media_7d=round(float(climate.humedad_media_7d),6),precipitacion_7d=round(float(climate.precipitacion_7d),4),detecciones_futuras_7d=int(r.detecciones_futuras_16_22_ene),etiqueta_preliminar=int(r.etiqueta_deteccion_futura),revision_nubes='PENDIENTE: falta SCL',revision_meta='PENDIENTE: poligono administrativo',revision_negativos='PENDIENTE: cobertura sensor VIIRS'))
df=pd.DataFrame(rows)
assert len(df)==10 and df.id.nunique()==10 and df.ndvi_medio_preliminar.notna().all()
csv=ROOT/'ANEXO_A_10_observaciones_multimodales_preliminares.csv'
df.to_csv(csv,index=False,encoding='utf-8-sig')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
md=['# Anexo A — Prueba de acoplamiento de 10 registros reales (preliminar)','', '**Proyecto:** Centinela de Incendios Forestales  ','**Integrantes:** Isabella Jiménez Cortés, Juan David Bernal y David Felipe Tautiva  ','**Fecha de referencia:** 15/01/2024','', '## Clave y correspondencia temporal','', 'Clave por muestra: `(id_cuadricula, fecha_referencia)`. Imagen: Sentinel-2 L2A del **10/01/2024**; clima: NASA POWER **09–15/01/2024**; etiqueta exploratoria FIRMS VIIRS S-NPP: detecciones **16–22/01/2024**. Cuadrículas UTM EPSG:32619 de 2 × 2 km.','', '## Tabla solicitada por el profesor','', '| N.º | Clave (entidad, ventana) | Dato de imagen: NDVI medio | Dato de serie: T2M media (°C) | NDMI medio | Detecciones posteriores (etiqueta) |','|---:|---|---:|---:|---:|---|']
for i,r in df.iterrows():md.append(f"| {i+1} | `{r['id']}, 2024-01-15` | {r.ndvi_medio_preliminar:.4f} | {r.temperatura_media_7d:.3f} | {r.ndmi_medio_preliminar:.4f} | {r.detecciones_futuras_7d} ({r.etiqueta_preliminar}) |")
md+=['','Los diez valores NDVI/NDMI provienen de bandas espectrales reales de las descargas de Copernicus; los valores de temperatura provienen de las consultas NASA POWER realizadas en Google Colab y guardadas en la tabla de acoplamiento previa. Los valores meteorológicos se repiten en ubicaciones cercanas por la resolución espacial de POWER.','', '## Consulta, código y trazabilidad','', '- Imágenes: `Browser_images (3).zip` (cuadrículas 01–04 y 06–10), `Browser_images (4).zip` (cuadrícula 05). Bandas **B02, B03, B04, B08 y B11**; nombres de los productos indican la fecha 2024-01-10.','- Clima: NASA POWER API `https://power.larc.nasa.gov/api/temporal/daily/point` con `T2M,RH2M,PRECTOTCORR`, `community=AG`, `start=20240109`, `end=20240115`, `format=JSON`, coordenadas de los centros de cada cuadrícula.','- FIRMS: VIIRS S-NPP 2024, filtrado a presuntos fuegos de vegetación; recuento espacial de los eventos registrados del 16 al 22 de enero. Etiquetas procedentes del archivo piloto de cuadrículas y **no auditadas nuevamente en esta versión**.','- Script de reproducción del cálculo espectral y de la unión tabular: `construir_anexo_A_completo.py`. Tabla de salida: `ANEXO_A_10_observaciones_multimodales_preliminares.csv`.','', '### Huellas SHA-256 de los insumos de imagen','']
for name in ('Browser_images (3).zip','Browser_images (4).zip'):
 md.append(f'- `{name}`: `{sha(ROOT/name)}`')
md+=['','## Alcance y validaciones pendientes','', '1. **Nubes/sombras:** no se descargó ni aplicó la máscara SCL, por lo que NDVI/NDMI son resúmenes **preliminares**, no valores validados ambientalmente.','2. **Espacio:** se intersectaron las cuadrículas de 2 × 2 km con los GeoTIFF georreferenciados. Falta comprobar los polígonos oficiales del departamento del Meta y verificar que cada escena corresponda al producto y fecha esperados.','3. **Etiquetas:** un cero significa ausencia de detección **registrada** en la ventana, no ausencia demostrada de incendio. Es necesario evaluar cobertura de VIIRS y filtros de confianza.','4. **Muestra:** estos diez casos sirven para comprobar acoplamiento técnico, **no** para entrenar o evaluar un modelo de Deep Learning.','5. **Reproducibilidad:** el script usa los archivos originales descargados y la tabla previa de clima/etiquetas; para una auditoría independiente completa se debe conservar también el notebook de consulta a NASA POWER y el algoritmo de etiquetado FIRMS.','']
(ROOT/'ANEXO_A_Centinela_Incendios_10_registros.md').write_text('\n'.join(md),encoding='utf-8')
print(df[['id','ndvi_medio_preliminar','ndmi_medio_preliminar','temperatura_media_7d','etiqueta_preliminar']].to_string(index=False))
print('Created',csv)
