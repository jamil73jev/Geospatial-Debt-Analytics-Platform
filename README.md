# SICOGE: Gestión de Cartera Basada en Análisis Geoespacial

Vista de análisis de la cartera de contribuyentes por tipo de deuda, título, juicio y sector, para la Dirección General Financiera de la M.I. Municipalidad de Guayaquil.

| | |
|---|---|
| **Idea y desarrollo de la georreferenciación** | Jorge Jamil Espinoza Villa, Analista Financiero |
| **Área** | Dirección General Financiera, M.I. Municipalidad de Guayaquil |
| **Estado** | En uso |
| **Plataforma** | Power BI (visual HTML Content) |
| **Uso** | Interno. Repositorio privado |

## Qué contiene

SICOGE se documenta como la página `GEORREFERENCIACION` del dashboard de Power BI *Recaudación Municipal: Tablero Ejecutivo*.

| Componente | Descripción |
|---|---|
| Panel de contribuyentes | Visual HTML Content alimentado por la medida `Dashboard_HTML_Contribuyentes_Pro_Plus` |
| Tabla de detalle | Tabla dinámica por tipo de deuda, título, juicio, sector de nomenclatura y contribuyente, con valor total, número de contribuyentes y promedio por contribuyente |

## Documentación

| Documento | Contenido |
|---|---|
| [Vista GEORREFERENCIACIÓN](docs/vista-georreferenciacion.md) | Campos, medidas y pendientes de la página |

## Pendiente por documentar

- [ ] Si el visual HTML dibuja un mapa o solo paneles y tablas.
- [ ] Método de geocodificación y fecha de la última actualización de coordenadas.
- [ ] Origen y frecuencia de actualización de la tabla `GEORREFERENCIACION`.
- [ ] Usuarios con acceso.

## Datos y seguridad

Este repositorio **no contiene datos de contribuyentes ni coordenadas**, ni el archivo `.pbix`. Solo documentación.
