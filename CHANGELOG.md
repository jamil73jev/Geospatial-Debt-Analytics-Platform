# Historial de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Las versiones siguen `MAYOR.MENOR.PARCHE`.

## [1.2.0] - 2026-10-13

### Agregado
- `AVISO.md`: aviso de uso y propiedad intelectual de este repositorio.
- Explicación de dónde nace la ubicación geográfica: el catastro del predio.
- Significado de AGA (áreas de gestión administrativa), PHV y PHH, y fecha de la última actualización de coordenadas (5 de octubre de 2026).

## [1.1.0] - 2026-10-13

### Agregado
- Medida DAX `Dashboard_HTML_Contribuyentes_Pro_Plus` en `dax/` y su explicación en `docs/medida-html-georreferenciacion.md`.
- Vista previa HTML con datos ficticios (`docs/vista-previa/`), capturas en `docs/img/` y el generador `herramientas/generar_vista_previa.py`.
- Segmentos de Pareto, calidad de la ubicación y rangos de antigüedad, tomados de la consulta de cartera consolidada.
- Confirmación de que los campos de la tabla dinámica de GEORREFERENCIACIÓN existen en esa consulta.

## [1.0.0] - 2026-10-13

Primera versión presentada de forma profesional.

### Agregado
- Documentación de la vista GEORREFERENCIACIÓN de Power BI: campos, medidas y tabla dinámica.
- Estados de cartera (TIN, GAT, P y T) con diagrama.
- Flujo de datos de la cartera al operativo y ejemplo con datos ficticios.
- Informe de necesidades de notificación y su presentación (`informes/`).
- Verificación automática de datos sensibles y enlaces, plantilla de cambios y responsable del código.

### Cambiado
- SICOGE queda documentado solo como la vista GEORREFERENCIACIÓN.
