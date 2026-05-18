# Pokemon PSA-like Grader & Market Estimator

Aplicacion web y API para estimar de forma orientativa la condicion visual de cartas Pokemon y calcular un precio aproximado ajustado segun su estado.

> Este proyecto no certifica notas PSA reales. El objetivo es construir un estimador visual tipo PSA para fines educativos y de productivizacion de modelos de Machine Learning.

## Estado actual

Hito 1 completado parcialmente:

- Estructura base del proyecto.
- Backend con FastAPI.
- Configuracion mediante variables de entorno.
- Conexion con Pokemon TCG API.
- Endpoint de salud `/health`.
- Endpoint de busqueda por ID `/api/v1/card/{card_id}`.
- Endpoint de busqueda por nombre `/api/v1/search?name=...`.

## Alcance del MVP

El usuario podra:

1. Buscar una carta Pokemon por nombre o ID.
2. Consultar informacion basica y precio de mercado.
3. Subir una imagen de una carta.
4. Recibir una estimacion de condicion visual.
5. Obtener una puntuacion PSA-like y un precio ajustado.

En la primera version, la imagen no se usara para identificar automaticamente la carta. El usuario seleccionara o buscara la carta, y la imagen servira para estimar su condicion.

## Clases del modelo

El baseline visual trabajara inicialmente con tres clases:

| Label | Descripcion | Rango PSA-like orientativo |
|---|---|---|
| `mint` | Carta aparentemente en muy buen estado | 8-10 |
| `played` | Carta usada con desgaste visible | 4-7 |
| `damaged` | Carta con danos claros o desgaste fuerte | 1-3 |

## Estrategia de datos

La Pokemon TCG API se usa para obtener:

- ID oficial de cartas.
- Nombre.
- Set.
- Rareza.
- Imagen oficial.
- Precios de mercado cuando esten disponibles.

Como no contamos con un dataset real etiquetado de cartas dañadas, el primer modelo se entrenara con un dataset sintetico: imagenes oficiales limpias a las que se aplicaran degradaciones artificiales como ruido, manchas, scratches, perdida de color o bordes desgastados.

Esta estrategia permite construir un baseline visual, aunque se documenta como limitacion porque el modelo aprende danos sinteticos y no necesariamente danos reales.

## Estructura del proyecto

```text
pokemon-psa-grader/
├── app/
│   ├── api/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── memoria_inicial.ipynb
├── frontend/
├── models/
├── notebooks/
├── tests/
├── Memoria.ipynb
├── README.md
├── requirements.txt
└── requirements-dev.txt