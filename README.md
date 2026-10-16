# FM Receiver — варикапне налаштування вхідного контуру

Розрахунок вхідного контуру FM-приймача діапазону **88–108 МГц**, який перебудовується варикапом:
напруга налаштування, вибірковість, пригнічення дзеркального каналу і вимоги до точності джерела напруги.
Усі результати — графіки, таблиці, анімація і звіт Word — генеруються з однієї програмної моделі.

Розрахунково-графічна робота, КПІ ім. Ігоря Сікорського, РТФ, група РЕ-41.

## Що вийде

| Результат | Де |
|---|---|
| Звіт Word (13 с.: модель, 11 рисунків, таблиці, висновки) | `report.docx` |
| Інтерактивний конспект з повзунками параметрів | `explore.py` (marimo) |
| Графіки PNG, 300 dpi | `results/figures/` |
| Таблиці CSV (станції, сітка частот, вихідні дані) | `results/data/` |
| Анімація перебудови АЧХ 88 → 108 МГц | `results/animations/K_U_sweep.gif` |

## Швидкий старт

Потрібен лише [uv](https://docs.astral.sh/uv/) — він сам встановить Python 3.14, бібліотеки й Quarto.

```bash
# 1. встановити uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
curl -LsSf https://astral.sh/uv/install.sh | sh                # Linux / macOS

# 2. отримати код
git clone https://github.com/Artem-Kravchenko1/rf-receiver.git
cd rf-receiver

# 3. зібрати все: тести → графіки, дані, GIF → звіт
uv run fm-build
```

Перший запуск завантажує залежності (кілька сотень МБ, разом із Quarto), далі збірка триває ~40 с.

## Окремі команди

| Команда | Що робить |
|---|---|
| `uv run fm-build` | усе разом (параметри: `--skip-tests`, `--no-report`, `--results <тека>`) |
| `uv run marimo edit explore.py` | конспект: теорія, повзунки, живі графіки, таблиця станцій |
| `uv run marimo run explore.py` | той самий конспект як застосунок без коду |
| `uv run pytest` | тести (модель, SymPy, графіки, дані, конспект) |
| `uv run python -m fm_receiver.export` | лише графіки, дані й GIF |
| `uv run quarto render report.qmd` | лише звіт |

## Модель

Паралельний контур $R_\mathrm{loss} \parallel L \parallel C_\mathrm{par} \parallel C_v(U)$, живлення від джерела струму.

- налаштування: $C(f_0) = 1/(4\pi^2 f_0^2 L)$, $C_v = C - C_\mathrm{par}$,
  $U(f_0) = \varphi\left[(C_{v0}/C_v)^{1/\gamma} - 1\right]$
- вибірковість: $K_U = 1/\sqrt{1+\xi^2}$, $\xi = Q(f/f_0 - f_0/f)$, $Q = 2\pi f_0 C R_\mathrm{loss}$, $BW = f_0/Q$
- дзеркальний канал: $f_\mathrm{im} = f_0 + 2 f_\mathrm{IF}$, $A = 10\lg(1 + \xi(f_\mathrm{im})^2)$ дБ, станція OK при $A \ge 20$ дБ
- допуск напруги: $U_\mathrm{tol} = (dU/df_0)\, f_\mathrm{tol}$

Вихідні дані: $L$ = 0.1 мкГн, $R_\mathrm{loss}$ = 3 кОм, $C_\mathrm{par}$ = 3 пФ, $C_{v0}$ = 60 пФ, $\varphi$ = 0.7 В,
$\gamma$ = 0.5, $f_\mathrm{IF}$ = 10.7 МГц, $f_\mathrm{tol}$ = 50 кГц; станції 88.4, 91.4, 96, 100, 103.6, 107 МГц.

**Результат:** напруга налаштування 2.16…6.49 В, $Q$ = 54…44, усі станції задовольняють критерій
(найменший запас 4.3 дБ на 107 МГц), допустима похибка джерела напруги 7…15 мВ.

## Структура

```
src/fm_receiver/
    model.py            формули (єдине джерело), параметри — frozen dataclass
    symulate_model.py   SymPy: виведення й перевірка формул
    units.py            перетворення одиниць
    plot_style/         стиль Matplotlib (.mplstyle) і оформлення осей
    plots.py            11 графіків (Matplotlib)
    data.py             таблиці (pandas): СІ + читабельні одиниці
    animation.py        GIF перебудови АЧХ
    export.py           збереження графіків, даних, GIF у results/
    build.py            команда fm-build
explore.py              конспект (marimo + Plotly)
report.qmd              звіт (Quarto → docx); template.docx — стилі, _quarto.yml — налаштування
tools/                  генерація шаблону й обробка docx після збірки
tests/                  pytest
docs/                   скани рукописних виведень
```

## Стек

Python 3.14 · uv · NumPy · SymPy · pandas · Matplotlib · Plotly · marimo · pytest · Ruff · Quarto
