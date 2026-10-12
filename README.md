# SICOGE: Gestión de Cartera Basada en Análisis Geoespacial

Vista de análisis de la cartera de contribuyentes por tipo de deuda, título, juicio y sector, para la Dirección General Financiera de la M.I. Municipalidad de Guayaquil.

**Idea y desarrollo de la georreferenciación:** Jorge Jamil Espinoza Villa, Analista Financiero
**Estado:** en uso

## Qué contiene

SICOGE se documenta como la página `GEORREFERENCIACION` del dashboard de Power BI *Recaudación Municipal: Tablero Ejecutivo*:

- 1 visual HTML Content con el panel de contribuyentes (medida `Dashboard_HTML_Contribuyentes_Pro_Plus`).
- 1 tabla dinámica con tipo de deuda, título, juicio, sector de nomenclatura y contribuyente, con el valor total, el número de contribuyentes y el promedio por contribuyente.

Detalle en [`docs/vista-georreferenciacion.md`](docs/vista-georreferenciacion.md).

## Pendiente por documentar

- [ ] Si el visual HTML dibuja un mapa o solo paneles y tablas.
- [ ] Método de geocodificación y fecha de la última actualización de coordenadas.
- [ ] Origen y frecuencia de actualización de la tabla `GEORREFERENCIACION`.
- [ ] Usuarios con acceso.

## Datos

Este repositorio **no contiene datos de contribuyentes ni coordenadas**, ni el archivo `.pbix`. Solo documentación.
