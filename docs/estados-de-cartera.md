# Estados de cartera

Estados que usa el informe de necesidades de notificación para clasificar la cartera según su etapa. Fuente: el informe y su presentación (corte del 16 de septiembre de 2026), en [`informes/`](../informes/).

```mermaid
flowchart LR
    subgraph PREV["Etapa previa a la notificación"]
        TIN["TIN<br/>Ingreso razón de no recepción<br/>de título de crédito"]
        P["P<br/>Sorteado<br/>para juicio coactivo"]
    end
    subgraph NOTIF["En notificación"]
        GAT["GAT<br/>Generación automática<br/>de título de crédito"]
        T["T<br/>Autos impreso"]
    end
    TIN --> GAT
    P --> T
    GAT --> OUT["Notificación del título de crédito"]
    T --> OUT2["Notificación del auto de pago"]
```

| Estado | Significado | Tipo de cartera | Etapa |
|---|---|---|---|
| `TIN` | Ingreso razón de no recepción de título de crédito | Títulos de crédito | Previa |
| `GAT` | Generación automática de título de crédito | Títulos de crédito | En notificación |
| `P` | Sorteado | Coactiva | Previa |
| `T` | Autos impreso | Coactiva | En notificación |

La cartera es un flujo: lo que hoy está en una etapa previa pasa después a notificación, por eso el informe dimensiona la capacidad de notificación sobre ambas etapas.
