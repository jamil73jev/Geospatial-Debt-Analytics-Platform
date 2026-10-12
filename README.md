# SICOGE: Gestión de Cartera Basada en Análisis Geoespacial

Portal de gestión de cartera basada en análisis geoespacial para la Dirección General Financiera de la M.I. Municipalidad de Guayaquil. Permite consultar, analizar y dar seguimiento a las obligaciones pendientes de los contribuyentes con títulos de crédito y patente municipal, ubicados geográficamente.

**Idea y desarrollo de la georreferenciación:** Jorge Jamil Espinoza Villa, Analista Financiero
**Estado:** publicado

## Secciones del portal

1. Consulta Contribuyentes
2. Deudas por Sector
3. Asignación
4. Seguimiento de Asignación
5. Tendencias Históricas
6. Resumen Ejecutivo

## Componentes

| Componente | Descripción |
|---|---|
| Portal web | Sitio institucional de la Dirección General Financiera (WordPress), con las seis secciones |
| Mapa interactivo | Aplicación de ArcGIS Experience Builder alojada en el geoportal de Guayaquil |
| Vista GEORREFERENCIACIÓN | Página del dashboard Recaudación Municipal: Tablero Ejecutivo, con panel HTML de contribuyentes por tipo de deuda, título, juicio y sector (ver `docs/vista-georreferenciacion.md`) |
| Vista de análisis | Página `CARTERA` del dashboard de Power BI "Cartera Municipal Cobranza y Conciliación", con mapa ArcGIS y filtros por contribuyente |

## Origen de los datos

- Cartera de títulos de crédito (impuesto 1,5 por mil y otros).
- Patente municipal.
- Coordenadas de los contribuyentes. [Documentar el método: código predial, dirección o geocodificación, y quién mantiene la capa.]

## Pendiente por documentar

- [ ] Método de geocodificación y fecha de la última actualización de coordenadas.
- [ ] Capas y servicios de ArcGIS usados, con su responsable.
- [ ] Control de acceso: quién puede ver qué campos de cada contribuyente.
- [ ] Frecuencia de actualización de la cartera.

## Documentación

- [`docs/arquitectura.md`](docs/arquitectura.md): componentes y flujo.
- [`docs/vista-georreferenciacion.md`](docs/vista-georreferenciacion.md): página GEORREFERENCIACIÓN de Power BI.
- [`docs/secciones-del-portal.md`](docs/secciones-del-portal.md): las seis secciones.

## Datos

Este repositorio **no contiene datos de contribuyentes ni coordenadas**. Solo documentación y código propio del proyecto.
