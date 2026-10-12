# Vista GEORREFERENCIACIÓN (Power BI)

Página del dashboard **Recaudación Municipal: Tablero Ejecutivo** (`Recaudación Municipal Tablero Ejecutivo.pbix`, octubre 2026) que corresponde a SICOGE. El archivo `.pbix` no se sube a este repositorio.

| Dato | Valor |
|---|---|
| Página | `GEORREFERENCIACION` |
| Visuales | 1 visual HTML Content, 1 tabla dinámica |
| Tabla del modelo | `GEORREFERENCIACION` |
| Contiene datos personales | Sí (nombre del contribuyente) |
| Fuente de datos | Base de datos municipal en un data warehouse |

## Visual HTML Content

Se alimenta de una sola medida DAX de la tabla del modelo, `Dashboard_HTML_Contribuyentes_Pro_Plus`, que genera el HTML del panel de contribuyentes.

## Tabla dinámica

| Tipo | Campo |
|---|---|
| Filas | `TipoDeuda`, `AnioTitulo`, `NumeroTitulo`, `NumeroJuicio`, `AnioJuicio`, `SectorNomenclatura`, `NombreContribuyente` |
| Valores | suma de `ValorTotal`, `Numero de contribuyentes`, `Promedio por Contribuyente` |
| Segmentación | medidas `SO_Cartera_Base_Segmentacion`, `SO_Obligaciones_Base_Segmentacion`, `SO_Segmento_Contribuyente` |

La vista relaciona la deuda de cada contribuyente (tipo, título y juicio) con su sector de nomenclatura.

## Por confirmar

- Si el visual HTML dibuja un mapa o solo paneles y tablas.
- Vista o tabla de origen de `GEORREFERENCIACION` en el data warehouse y frecuencia de actualización.
- Relación exacta con el mapa de ArcGIS y con la página `CARTERA` del dashboard de cartera.
