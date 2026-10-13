#!/usr/bin/env python3
"""Genera una vista previa HTML de la medida DAX del dashboard de georreferenciación.

La medida (`dax/dashboard-html-contribuyentes-pro-plus_v202610.dax`) devuelve un
texto HTML que Power BI muestra con un visual de contenido HTML. Fuera de Power BI
ese texto no se puede ver porque el DAX necesita el modelo de datos.

Este script toma el HTML de la medida (estilos y estructura reales), reemplaza
cada cálculo DAX por valores FICTICIOS y deja un archivo que se abre en cualquier
navegador. No lee datos reales ni se conecta a ninguna base.

Uso:
    python3 herramientas/generar_vista_previa.py [salida.html]

Sin argumentos escribe `docs/vista-previa/georreferenciacion.html`.
"""
from __future__ import annotations

import random
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DAX = RAIZ / "dax" / "dashboard-html-contribuyentes-pro-plus_v202610.dax"
SALIDA_POR_DEFECTO = RAIZ / "docs" / "vista-previa" / "georreferenciacion.html"

SEGMENTOS = ("c", "h", "m", "l")  # crítico, alto, medio, bajo
COMBINACIONES = [
    "c", "h", "m", "l", "ch", "cm", "cl", "hm", "hl", "ml",
    "chm", "chl", "cml", "hml", "all",
]
MONTO_PROMEDIO = {"c": 21000, "h": 7200, "m": 2100, "l": 420}
OBLIG_PROMEDIO = {"c": 14, "h": 8, "m": 5, "l": 2}

PARROQUIAS = [
    "PARROQUIA EJEMPLO 01", "PARROQUIA EJEMPLO 02", "PARROQUIA EJEMPLO 03",
    "PARROQUIA EJEMPLO 04", "PARROQUIA EJEMPLO 05", "PARROQUIA EJEMPLO 06",
    "PARROQUIA EJEMPLO 07", "PARROQUIA EJEMPLO 08", "PARROQUIA EJEMPLO 09",
    "PARROQUIA EJEMPLO 10", "PARROQUIA EJEMPLO 11", "PARROQUIA EJEMPLO 12",
]
SECTORES = [f"SEC-{i:03d} · SECTOR DE EJEMPLO" for i in range(1, 17)]
RUBROS = [
    "RUBRO DE EJEMPLO A", "RUBRO DE EJEMPLO B", "RUBRO DE EJEMPLO C",
    "RUBRO DE EJEMPLO D", "RUBRO DE EJEMPLO E", "RUBRO DE EJEMPLO F",
]
BRECHAS = [
    ("01", "SIN UBICACIÓN"), ("02", "SIN COORDENADAS"),
    ("03", "SIN PARROQUIA"), ("04", "SIN SECTOR"),
]


# --------------------------------------------------------------------------
# Formato (configuración regional es: miles con punto, decimales con coma)
# --------------------------------------------------------------------------
def _miles(valor: float, decimales: int) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def formatear(valor, formato: str) -> str:
    if formato == "#,##0":
        return _miles(valor, 0)
    if formato == "0.00":
        return _miles(valor, 2).replace(".", "")
    if formato == "$ #,##0.00":
        return "$ " + _miles(valor, 2)
    if formato == "0.0%":
        return _miles(valor * 100, 1) + "%"
    if formato == "0.00%":
        return _miles(valor * 100, 2) + "%"
    raise ValueError(f"Formato no soportado: {formato}")


# --------------------------------------------------------------------------
# Datos ficticios
# --------------------------------------------------------------------------
def repartir(total: int, n: int, rnd: random.Random, ceros: int = 0) -> list[int]:
    """Reparte un entero en n partes aleatorias que suman exactamente total.

    `ceros` deja esa cantidad de partes en cero (zonas sin ese segmento).
    """
    pesos = [rnd.random() + 0.15 for _ in range(n)]
    for indice in rnd.sample(range(n), ceros):
        pesos[indice] = 0.0
    suma = sum(pesos)
    partes = [int(total * p / suma) for p in pesos]
    partes[0] += total - sum(partes)
    return partes


def generar_modelo(semilla: int = 20261012) -> dict:
    rnd = random.Random(semilla)
    fases = {}
    for fase, factor in (("TIT", 1.0), ("COA", 1.35)):
        # Contribuyentes por segmento en el universo con ubicación completa
        totales = {
            "c": int(rnd.randint(60, 90) * factor),
            "h": int(rnd.randint(260, 340) * factor),
            "m": int(rnd.randint(900, 1200) * factor),
            "l": int(rnd.randint(3200, 4200) * factor),
        }
        ceros = {"c": 3, "h": 0, "m": 0, "l": 0}  # algunas zonas sin críticos
        parroquias = {s: repartir(totales[s], len(PARROQUIAS), rnd, ceros[s]) for s in SEGMENTOS}
        sectores = {s: repartir(totales[s], len(SECTORES), rnd, 2 * ceros[s]) for s in SEGMENTOS}

        def monto(cant: int, seg: str) -> float:
            return round(cant * MONTO_PROMEDIO[seg] * rnd.uniform(0.85, 1.15), 2)

        filas_parr = []
        for i, nombre in enumerate(PARROQUIAS):
            cant = {s: parroquias[s][i] for s in SEGMENTOS}
            filas_parr.append({"nombre": nombre, "cant": cant,
                               "monto": {s: monto(cant[s], s) for s in SEGMENTOS}})
        filas_sect = []
        for i, nombre in enumerate(SECTORES):
            cant = {s: sectores[s][i] for s in SEGMENTOS}
            filas_sect.append({"nombre": nombre, "cant": cant,
                               "monto": {s: monto(cant[s], s) for s in SEGMENTOS}})
        # Brechas de ubicación (exclusivas): 01 sin ubicación … 04 sin sector
        brechas = []
        for codigo, etiqueta in BRECHAS:
            escala = {"01": 0.30, "02": 0.12, "03": 0.08, "04": 0.10}[codigo]
            cant = {s: int(totales[s] * escala * rnd.uniform(0.7, 1.3)) for s in SEGMENTOS}
            brechas.append({"codigo": codigo, "etiqueta": etiqueta, "cant": cant,
                            "monto": {s: monto(cant[s], s) for s in SEGMENTOS}})
        fases[fase] = {"parr": filas_parr, "sect": filas_sect, "brechas": brechas}
    return {"fases": fases, "rnd": rnd}


def sumar_filas(a: list[dict], b: list[dict]) -> list[dict]:
    salida = []
    for fa, fb in zip(a, b):
        base = {k: v for k, v in fa.items() if k not in ("cant", "monto")}
        base["cant"] = {s: fa["cant"][s] + fb["cant"][s] for s in SEGMENTOS}
        base["monto"] = {s: round(fa["monto"][s] + fb["monto"][s], 2) for s in SEGMENTOS}
        salida.append(base)
    return salida


# --------------------------------------------------------------------------
# HTML de las filas (replica las plantillas DAX)
# --------------------------------------------------------------------------
def clave_a_segmentos(clave: str) -> set[str]:
    return set("chml") if clave == "all" else set(clave)


def celdas_dinamicas(cant: dict, monto: dict) -> str:
    def attrs(fn) -> str:
        return "\n".join(f"                    data-{k}='{fn(k)}'" for k in COMBINACIONES)

    def suma(valores: dict, clave: str) -> float:
        return sum(valores[s] for s in clave_a_segmentos(clave))

    def promedio(clave: str) -> float:
        n = suma(cant, clave)
        return suma(monto, clave) / n if n else 0

    return (
        "                <td class='seg-num total seg-dynamic'\n"
        + attrs(lambda k: formatear(suma(cant, k), "#,##0")) + "></td>\n"
        "                <td class='seg-money seg-dynamic'\n"
        + attrs(lambda k: formatear(suma(monto, k), "$ #,##0.00")) + "></td>\n"
        "                <td class='seg-average seg-dynamic'\n"
        + attrs(lambda k: formatear(promedio(k), "$ #,##0.00")) + "></td>\n"
    )


def clase_riesgo(cant: dict, base: str) -> str:
    nombres = {"c": "critical", "h": "high", "m": "medium", "l": "low"}
    return base + "".join(f" has-{nombres[s]}" for s in SEGMENTOS if cant[s] > 0)


def fila_territorial(fila: dict) -> str:
    c = fila["cant"]
    return (
        f"<tr class='{clase_riesgo(c, 'seg-risk-row')}'>\n"
        f"                <td class='seg-parr-name'>{fila['nombre']}</td>\n"
        f"                <td class='seg-num critical'>{formatear(c['c'], '#,##0')}</td>\n"
        f"                <td class='seg-num high'>{formatear(c['h'], '#,##0')}</td>\n"
        f"                <td class='seg-num medium'>{formatear(c['m'], '#,##0')}</td>\n"
        f"                <td class='seg-num low'>{formatear(c['l'], '#,##0')}</td>\n"
        + celdas_dinamicas(c, fila["monto"]) + "            </tr>"
    )


def fila_brecha_hija(b: dict) -> str:
    c = b["cant"]
    return (
        f"<tr class='{clase_riesgo(c, 'seg-review-child seg-risk-row')}'>\n"
        "                <td class='seg-parr-name'>\n"
        "                    <span class='seg-child-line'>└─</span>\n"
        f"                    <span class='seg-status-code'>{b['codigo']}</span>{b['etiqueta']}</td>\n"
        f"                <td class='seg-num critical'>{formatear(c['c'], '#,##0')}</td>\n"
        f"                <td class='seg-num high'>{formatear(c['h'], '#,##0')}</td>\n"
        f"                <td class='seg-num medium'>{formatear(c['m'], '#,##0')}</td>\n"
        f"                <td class='seg-num low'>{formatear(c['l'], '#,##0')}</td>\n"
        + celdas_dinamicas(c, b["monto"]) + "            </tr>"
    )


def fila_brecha_padre(brechas: list[dict]) -> str:
    cant = {s: sum(b["cant"][s] for b in brechas) for s in SEGMENTOS}
    monto = {s: sum(b["monto"][s] for b in brechas) for s in SEGMENTOS}
    return (
        f"<tr class='{clase_riesgo(cant, 'seg-review-parent seg-risk-row')}'>\n"
        "                <td class='seg-parr-name'>\n"
        "                    <span class='seg-review-icon'>&#9662;</span>\n"
        "                    REVISAR UBICACIÓN\n"
        "                    <span class='seg-review-sub'>Sin ubicación, coordenadas, parroquia o sector · GENERAL</span>\n"
        "                </td>\n"
        f"                <td class='seg-num critical'>{formatear(cant['c'], '#,##0')}</td>\n"
        f"                <td class='seg-num high'>{formatear(cant['h'], '#,##0')}</td>\n"
        f"                <td class='seg-num medium'>{formatear(cant['m'], '#,##0')}</td>\n"
        f"                <td class='seg-num low'>{formatear(cant['l'], '#,##0')}</td>\n"
        + celdas_dinamicas(cant, monto) + "            </tr>"
    )


def orden_territorial(filas: list[dict]) -> list[dict]:
    """Mismo criterio de la medida: promedio, cartera y presencias."""
    def promedio(f):
        n = sum(f["cant"].values())
        return sum(f["monto"].values()) / n if n else 0
    return sorted(filas, key=lambda f: (-promedio(f), -sum(f["monto"].values())))


def html_territorial(filas: list[dict], brechas: list[dict]) -> str:
    cuerpo = "\n".join(fila_territorial(f) for f in orden_territorial(filas))
    return cuerpo + "\n" + fila_brecha_padre(brechas) + "\n" + "\n".join(
        fila_brecha_hija(b) for b in brechas)


def html_estados(estados: list[tuple[str, float, int, int]], total: float) -> str:
    filas = []
    for nombre, monto, cont, oblig in sorted(estados, key=lambda e: -e[1]):
        filas.append(
            "<div class='phase-state-row'>\n"
            "  <div class='phase-state-main'>\n"
            f"    <span class='phase-state-name'>{nombre}</span>\n"
            f"    <span class='phase-state-pct'>{formatear(monto / total, '0.0%')}</span>\n"
            "  </div>\n"
            "  <div class='phase-state-metrics'>\n"
            f"    <div><span>Cartera</span><b>{formatear(monto, '$ #,##0.00')}</b></div>\n"
            f"    <div><span>Contrib.</span><b>{formatear(cont, '#,##0')}</b></div>\n"
            f"    <div><span>Oblig.</span><b>{formatear(oblig, '#,##0')}</b></div>\n"
            f"    <div><span>Promedio</span><b>{formatear(monto / cont, '$ #,##0.00')}</b></div>\n"
            "  </div>\n"
            "</div>")
    return "\n".join(filas)


# --------------------------------------------------------------------------
# Variables de la medida
# --------------------------------------------------------------------------
def catalogo_estados(texto_dax: str, fase: str) -> list[str]:
    patron = re.compile(r'\(\s*"%s"\s*,\s*"([^"]+)"\s*\)' % fase)
    return patron.findall(texto_dax)


def construir_contexto(texto_dax: str) -> dict:
    modelo = generar_modelo()
    rnd: random.Random = modelo["rnd"]
    tit, coa = modelo["fases"]["TIT"], modelo["fases"]["COA"]
    gen = {
        "parr": sumar_filas(tit["parr"], coa["parr"]),
        "sect": sumar_filas(tit["sect"], coa["sect"]),
        "brechas": sumar_filas(tit["brechas"], coa["brechas"]),
    }

    def totales(fase: dict) -> tuple[int, float, int]:
        filas = fase["parr"] + fase["brechas"]
        cont = sum(sum(f["cant"].values()) for f in filas)
        monto = sum(sum(f["monto"].values()) for f in filas)
        oblig = sum(f["cant"][s] * OBLIG_PROMEDIO[s] for f in filas for s in SEGMENTOS)
        return cont, round(monto, 2), oblig

    cont_t, cart_t, obl_t = totales(tit)
    cont_c, cart_c, obl_c = totales(coa)
    contribuyentes = cont_t + cont_c
    cartera = cart_t + cart_c
    obligaciones = obl_t + obl_c

    seg = {s: sum(f["cant"][s] for f in gen["parr"] + gen["brechas"]) for s in SEGMENTOS}
    seg_monto = {s: sum(f["monto"][s] for f in gen["parr"] + gen["brechas"]) for s in SEGMENTOS}

    # Calidad de ubicación (excluyentes): 05 completa = tablas territoriales
    def monto_filas(filas):
        return round(sum(sum(f["monto"].values()) for f in filas), 2)

    def cont_filas(filas):
        return sum(sum(f["cant"].values()) for f in filas)

    def obl_filas(filas):
        return sum(f["cant"][s] * OBLIG_PROMEDIO[s] for f in filas for s in SEGMENTOS)

    b = {x["codigo"]: x for x in gen["brechas"]}
    completa = gen["parr"]
    c05, m05, o05 = cont_filas(completa), monto_filas(completa), obl_filas(completa)
    c01, m01, o01 = (cont_filas([b["01"]]), monto_filas([b["01"]]), obl_filas([b["01"]]))
    dep = [b["02"], b["03"], b["04"]]
    m_dep = monto_filas(dep)
    notificable = m05 + m_dep

    def pct(x, total=cartera):
        return x / total if total else 0

    def ancho(p):
        return f"{p * 100:.1f}"

    # Top territorial
    def top_territorial(filas):
        validas = [f for f in filas if sum(f["cant"].values()) > 0]
        prom = lambda f: sum(f["monto"].values()) / sum(f["cant"].values())
        por_prom = max(validas, key=prom)
        por_cartera = max(validas, key=lambda f: sum(f["monto"].values()))
        top5 = sorted(validas, key=lambda f: -sum(f["monto"].values()))[:5]
        monto_top5 = sum(sum(f["monto"].values()) for f in top5)
        total_inf = sum(sum(f["monto"].values()) for f in validas)
        con_prio = sum(1 for f in validas if f["cant"]["c"] + f["cant"]["h"] > 0)
        con_crit = sum(1 for f in validas if f["cant"]["c"] > 0)
        return {
            "n": len(validas), "prio": con_prio, "crit": con_crit,
            "nombre_prom": por_prom["nombre"], "prom": prom(por_prom),
            "nombre_cart": por_cartera["nombre"],
            "monto_cart": sum(por_cartera["monto"].values()),
            "top5": monto_top5, "pct_top5": monto_top5 / total_inf,
        }

    tp, ts = top_territorial(gen["parr"]), top_territorial(gen["sect"])

    # Estados por fase (catálogo real de estados; montos ficticios)
    def estados_fase(codigo: str, total: float, cuantos: int):
        nombres = catalogo_estados(texto_dax, codigo)[:cuantos]
        pesos = [rnd.random() + 0.2 for _ in nombres]
        suma = sum(pesos)
        salida = []
        for nombre, peso in zip(nombres, pesos):
            monto = round(total * peso / suma, 2)
            cont = max(1, int(monto / rnd.uniform(1800, 2600)))
            salida.append((nombre, monto, cont, int(cont * rnd.uniform(2.2, 3.6))))
        return salida

    est_t = estados_fase("TIT", cart_t, 4)
    est_c = estados_fase("COA", cart_c, 6)

    # Rubros bloqueados (suman la cartera sin ubicación)
    pesos = [rnd.random() + 0.2 for _ in RUBROS]
    suma_p = sum(pesos)
    filas_rubro = []
    resto_c, resto_o = c01, o01
    for i, (rubro, peso) in enumerate(zip(RUBROS, pesos)):
        monto = round(m01 * peso / suma_p, 2)
        cont = c01 * peso / suma_p
        filas_rubro.append((rubro, monto, int(cont) or 1, int(cont * o01 / c01) or 1))
    filas_rubro.sort(key=lambda r: -r[1])
    html_rubros = "\n".join(
        "<tr>\n"
        f"  <td class='nogeo-rubro' title='{r}'>{r}</td>\n"
        f"  <td class='num'>{formatear(o, '#,##0')}</td>\n"
        f"  <td class='num'>{formatear(cn, '#,##0')}</td>\n"
        f"  <td class='money strong'>{formatear(m, '$ #,##0.00')}</td>\n"
        f"  <td class='center'>{formatear(m / m01, '0.00%')}</td>\n"
        "</tr>" for r, m, cn, o in filas_rubro)

    pct_dir = m05 / notificable
    pct_mej = m_dep / notificable
    p_ya, p_dep, p_inv = pct(m05), pct(m_dep), pct(m01)
    decision = (
        "REDUCIR LA CARTERA BLOQUEADA POR FALTA DE UBICACIÓN" if p_inv >= 0.25 else
        "NOTIFICAR Y DEPURAR EN PARALELO" if p_dep >= p_ya else
        "ESCALAR LA NOTIFICACIÓN SOBRE LA CARTERA YA UBICABLE")

    f = formatear
    p_notif = pct(notificable)
    mayor = "COACTIVA" if cart_c >= cart_t else "TÍTULOS"
    msg_notif = (
        f"{f(p_notif, '0.0%')} de la cartera es ubicable y puede incorporarse al proceso de "
        f"notificación. Dentro de ese universo, {f(pct_dir, '0.0%')} está listo sin corrección "
        f"territorial y {f(pct_mej, '0.0%')} puede notificarse mientras se mejoran coordenadas, "
        "parroquia o sector.")
    msg_ejec_notif = (
        f"{f(p_notif, '0.0%')} de la cartera puede entrar al proceso de notificación con la "
        f"información disponible. {f(p_ya, '0.0%')} está lista sin corrección territorial; "
        f"{f(p_dep, '0.0%')} puede notificarse pero requiere mejorar coordenadas, parroquia o "
        f"sector; y solo {f(p_inv, '0.0%')} está bloqueada por ausencia de ubicación.")
    msg_fases = (
        f"{mayor} concentra la mayor exposición con {f(max(cart_c, cart_t), '$ #,##0.00')} "
        f"({f(max(cart_c, cart_t) / cartera, '0.0%')} de la cartera). Operativamente, la deuda nace "
        "en Títulos y, si no se logra recuperar, migra a Coactiva. La diferencia entre ambas "
        f"fases es {f(abs(cart_c - cart_t), '$ #,##0.00')}.")

    def msg_territorio(t, singular, plural, articulo_top, informada):
        return (
            f"Se identifican {f(t['n'], '#,##0')} {plural} con cartera dentro del filtro actual; "
            f"{f(t['prio'], '#,##0')} presentan al menos un contribuyente Crítico o Alto y "
            f"{f(t['crit'], '#,##0')} contienen presencia crítica. {articulo_top} con mayor "
            f"prioridad territorial por rendimiento promedio es {t['nombre_prom']} con "
            f"{f(t['prom'], '$ #,##0.00')} de cartera promedio por contribuyente. "
            f"Las cinco {plural} de mayor cartera concentran {f(t['pct_top5'], '0.0%')} de la "
            f"cartera con {singular} informad{informada}.")

    msg_parr = msg_territorio(tp, "parroquia", "parroquias", "La parroquia", "a")
    msg_sect = msg_territorio(ts, "sector", "sectores", "El sector", "o")

    ctx = {
        # Filtros activos
        "_FechaCorteTexto": "12/10/2026 (ficticia)", "_FiltroFase": "Todas",
        "_FiltroAnio": "Todos", "_FiltroRubro": "Todos", "_FiltroAGA": "Todos",
        "_FiltroParroquia": "Todas", "_FiltroSector": "Todos",
        "_FiltroEstado": "Todos", "_FiltroEdad": "Todas",
        # KPI generales
        "_Contribuyentes": contribuyentes, "_Cartera": cartera,
        "_DeudaPromedio": cartera / contribuyentes, "_Obligaciones": obligaciones,
        "_ObligPromedio": obligaciones / contribuyentes,
        "_MayorExposicion": 86450.75,
        "_PctContribNotificablesHoy": (contribuyentes - c01) / contribuyentes,
        # Fases
        "_PctCarteraTitulosTotal": cart_t / cartera, "_PctCarteraCoactivaTotal": cart_c / cartera,
        "_CarteraTitulosTotal": cart_t, "_CarteraCoactivaTotal": cart_c,
        "_ContribuyentesTitulosTotal": cont_t, "_ContribuyentesCoactivaTotal": cont_c,
        "_ObligacionesTitulosTotal": obl_t, "_ObligacionesCoactivaTotal": obl_c,
        "_PromedioTitulosPorContribuyente": cart_t / cont_t,
        "_PromedioCoactivaPorContribuyente": cart_c / cont_c,
        "_HtmlEstadosTitulos": html_estados(est_t, cart_t),
        "_HtmlEstadosCoactiva": html_estados(est_c, cart_c),
        "_WTitulosFase": ancho(cart_t / cartera), "_WCoactivaFase": ancho(cart_c / cartera),
        "_MensajeEjecutivoFases": msg_fases,
        # Segmentación operativa
        "_Criticos": seg["c"], "_Altos": seg["h"], "_Medios": seg["m"], "_Bajos": seg["l"],
        "_PctCriticos": seg["c"] / contribuyentes, "_PctAltos": seg["h"] / contribuyentes,
        "_PctMedios": seg["m"] / contribuyentes, "_PctBajos": seg["l"] / contribuyentes,
        "_MontoCriticos": seg_monto["c"], "_MontoAltos": seg_monto["h"],
        "_MontoMedios": seg_monto["m"], "_MontoBajos": seg_monto["l"],
        "_PctCarteraCriticos": seg_monto["c"] / cartera, "_PctCarteraAltos": seg_monto["h"] / cartera,
        "_PctCarteraMedios": seg_monto["m"] / cartera, "_PctCarteraBajos": seg_monto["l"] / cartera,
        # Parroquia
        "_CantidadParroquiasAnalizadas": tp["n"], "_ParroquiasConPrioridad": tp["prio"],
        "_TopParroquiaPrioridadNombre": tp["nombre_prom"], "_TopParroquiaPrioridadPromedio": tp["prom"],
        "_TopParroquiaCarteraNombre": tp["nombre_cart"], "_TopParroquiaCarteraMonto": tp["monto_cart"],
        "_PctCarteraTop5Parroquias": tp["pct_top5"], "_CarteraTop5Parroquias": tp["top5"],
        "_MensajeEjecutivoParroquia": msg_parr,
        "_HtmlSegmentacionParroquia": "", "_HtmlSegmentacionParroquia_TIT": "",
        "_HtmlSegmentacionParroquia_COA": "",
        # Sector
        "_CantidadSectoresAnalizados": ts["n"], "_SectoresConPrioridad": ts["prio"],
        "_TopSectorPrioridadNombre": ts["nombre_prom"], "_TopSectorPrioridadPromedio": ts["prom"],
        "_TopSectorCarteraNombre": ts["nombre_cart"], "_TopSectorCarteraMonto": ts["monto_cart"],
        "_PctCarteraTop5Sectores": ts["pct_top5"], "_CarteraTop5Sectores": ts["top5"],
        "_MensajeEjecutivoSector": msg_sect,
        "_HtmlSegmentacionSector": "", "_HtmlSegmentacionSector_TIT": "",
        "_HtmlSegmentacionSector_COA": "",
        "_CantidadParroquiasAnalizadas_TIT": len(PARROQUIAS),
        "_CantidadParroquiasAnalizadas_COA": len(PARROQUIAS),
        "_CantidadSectoresAnalizados_TIT": len(SECTORES),
        "_CantidadSectoresAnalizados_COA": len(SECTORES),
        # Brechas: el contenido va completo dentro de la concatenación de cada tabla
        "_HtmlBrechas_GENERAL": "", "_HtmlBrechas_TIT": "", "_HtmlBrechas_COA": "",
        # Notificación
        "_CarteraNotificableHoy": notificable, "_PctCarteraNotificableHoy": p_notif,
        "_ObligNotificablesHoy": o05 + obl_filas(dep), "_ContribNotificablesHoy": c05 + cont_filas(dep),
        "_CarteraNoNotificableHoy": m01, "_PctCarteraNoNotificableHoy": pct(m01),
        "_ObligNoNotificablesHoy": o01, "_ContribNoNotificablesHoy": c01,
        "_WNotificable": ancho(p_notif), "_WNoNotificable": ancho(pct(m01)),
        "_MensajeNotificacionEjecutivo": msg_notif,
        "_CarteraUbicacionCompleta": m05, "_PctDirectoDentroNotificable": pct_dir,
        "_CarteraNotificableIncompleta": m_dep, "_PctMejoraDentroNotificable": pct_mej,
        "_WDirectoDentroNotificable": ancho(pct_dir), "_WMejoraDentroNotificable": ancho(pct_mej),
        "_PctAccionNotificarYa": p_ya, "_PctAccionNotificarDepurar": p_dep,
        "_PctAccionInvestigar": p_inv, "_WAccionNotificarYa": ancho(p_ya),
        "_WAccionNotificarDepurar": ancho(p_dep), "_WAccionInvestigar": ancho(p_inv),
        "_ObligUbicacionCompleta": o05, "_ContUbicacionCompleta": c05,
        "_ObligNotificarDepurar": obl_filas(dep),
        "_CarteraSinCoordenadas": monto_filas([b["02"]]), "_ObligSinCoordenadas": obl_filas([b["02"]]),
        "_ContSinCoordenadas": cont_filas([b["02"]]),
        "_CarteraSinParroquia": monto_filas([b["03"]]), "_ObligSinParroquia": obl_filas([b["03"]]),
        "_ContSinParroquia": cont_filas([b["03"]]),
        "_CarteraSinSector": monto_filas([b["04"]]), "_ObligSinSector": obl_filas([b["04"]]),
        "_ContSinSector": cont_filas([b["04"]]),
        "_DecisionEjecutivaNotificacion": decision, "_MensajeEjecutivoNotificacion": msg_ejec_notif,
        "_CantidadRubrosNoNotificables": len(RUBROS), "_HtmlRubrosNoNotificables": html_rubros,
    }
    # Cuerpos de las tablas territoriales (filas + REVISAR UBICACIÓN)
    ctx["_HtmlSegmentacionParroquia"] = html_territorial(gen["parr"], gen["brechas"])
    ctx["_HtmlSegmentacionParroquia_TIT"] = html_territorial(tit["parr"], tit["brechas"])
    ctx["_HtmlSegmentacionParroquia_COA"] = html_territorial(coa["parr"], coa["brechas"])
    ctx["_HtmlSegmentacionSector"] = html_territorial(gen["sect"], gen["brechas"])
    ctx["_HtmlSegmentacionSector_TIT"] = html_territorial(tit["sect"], tit["brechas"])
    ctx["_HtmlSegmentacionSector_COA"] = html_territorial(coa["sect"], coa["brechas"])
    return ctx


# --------------------------------------------------------------------------
# Intérprete mínimo de la concatenación DAX final
# --------------------------------------------------------------------------
def extraer_plantilla(texto_dax: str) -> str:
    """Devuelve el texto desde la comilla que abre el HTML final hasta el final."""
    m = re.search(r'^RETURN\s*\n"\s*\n<style>', texto_dax, re.M)
    if not m:
        raise SystemExit("No se encontró el RETURN final con el HTML (<style>).")
    inicio = texto_dax.index('"', m.start())
    return texto_dax[inicio:]


def leer_cadena(t: str, i: int) -> tuple[str, int]:
    """Lee un literal DAX que empieza en t[i] == '"'. Devuelve (texto, posición siguiente)."""
    assert t[i] == '"'
    i += 1
    partes = []
    while True:
        j = t.index('"', i)
        partes.append(t[i:j])
        if j + 1 < len(t) and t[j + 1] == '"':  # comilla escapada ""
            partes.append('"')
            i = j + 2
            continue
        return "".join(partes), j + 1


def leer_expresion(t: str, i: int) -> tuple[str, int]:
    """Lee una expresión hasta el próximo '&' de nivel 0 o el final."""
    profundidad, j = 0, i
    while j < len(t):
        ch = t[j]
        if ch == '"':
            _, j = leer_cadena(t, j)
            continue
        if ch == "(":
            profundidad += 1
        elif ch == ")":
            profundidad -= 1
        elif ch == "&" and profundidad == 0:
            break
        j += 1
    return t[i:j].strip(), j


def evaluar(expr: str, ctx: dict) -> str:
    expr = re.sub(r"\s+", " ", expr)
    m = re.fullmatch(r'FORMAT\s*\(\s*(_\w+)\s*,\s*"([^"]+)"\s*\)', expr)
    if m:
        nombre, formato = m.groups()
        if nombre not in ctx:
            raise KeyError(nombre)
        return formatear(ctx[nombre], formato)
    m = re.fullmatch(r"_\w+", expr)
    if m:
        if expr not in ctx:
            raise KeyError(expr)
        return str(ctx[expr])
    raise ValueError(f"Expresión no soportada: {expr[:80]}")


def renderizar(plantilla: str, ctx: dict) -> str:
    salida, i, n = [], 0, len(plantilla)
    while i < n:
        while i < n and plantilla[i].isspace():
            i += 1
        if i >= n:
            break
        if plantilla[i] == '"':
            texto, i = leer_cadena(plantilla, i)
            salida.append(texto)
        else:
            expr, i = leer_expresion(plantilla, i)
            if expr:
                salida.append(evaluar(expr, ctx))
        while i < n and plantilla[i].isspace():
            i += 1
        if i < n and plantilla[i] == "&":
            i += 1
    return "".join(salida)


MARCO = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vista previa · Dashboard de georreferenciación (datos ficticios)</title>
<style>
 .preview-banner{{position:sticky;top:0;z-index:10;background:#b3261e;color:#fff;
   font:600 12px/1.4 system-ui,Segoe UI,Arial,sans-serif;padding:6px 12px;text-align:center}}
 html,body{{background:#f2f5f8}}
</style>
</head>
<body>
<div class="preview-banner">VISTA PREVIA · DATOS FICTICIOS · Generada con herramientas/generar_vista_previa.py a partir de la medida DAX real</div>
{cuerpo}
</body>
</html>
"""


def main() -> None:
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else SALIDA_POR_DEFECTO
    texto = DAX.read_text(encoding="utf-8")
    ctx = construir_contexto(texto)
    try:
        html = renderizar(extraer_plantilla(texto), ctx)
    except KeyError as error:
        raise SystemExit(f"Falta el valor ficticio de la variable {error} en el contexto.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(MARCO.format(cuerpo=html), encoding="utf-8", newline="\n")
    print(f"Vista previa escrita en {destino} ({len(html):,} caracteres)")


if __name__ == "__main__":
    main()
