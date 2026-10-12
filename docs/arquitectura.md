# Arquitectura de SICOGE

**Gestión de Cartera Basada en Análisis Geoespacial** reúne tres componentes. Lo que aún no está confirmado se marca como *por confirmar*.

```
Cartera (títulos de crédito y patente municipal)
        │  + coordenadas de los contribuyentes (geocodificación: por confirmar)
        ▼
Capas de ArcGIS (propietario y servicio: por confirmar)
        ├──► Mapa interactivo (ArcGIS Experience Builder, geoportal de Guayaquil)
        │          ▲ incrustado en
        │    Portal web de la Dirección General Financiera (WordPress, 6 secciones)
        └──► Página CARTERA del dashboard de Power BI "Cartera Municipal: Cobranza y Conciliación"
```

## Componentes

| Componente | Tecnología | Función |
|---|---|---|
| Portal web | WordPress, sitio institucional | Reúne las seis secciones de consulta y análisis |
| Mapa interactivo | ArcGIS Experience Builder | Ubica y consulta contribuyentes sobre el mapa |
| Vista de análisis | Power BI con visual Esri (ArcGIS) | Cartera con filtros por contribuyente y mapa |

## Origen del proyecto

La idea de georreferenciar a los contribuyentes con títulos de crédito y patente municipal, y su desarrollo, son de Jorge Jamil Espinoza Villa, Analista Financiero de la Dirección General Financiera.

## Por confirmar

- Método de geocodificación (código predial, dirección u otro) y fecha de la última actualización.
- Capas y servicios de ArcGIS, y quién los administra.
- Quién puede ver cada campo del contribuyente y si el portal exige inicio de sesión.
- Frecuencia de actualización de la cartera.
