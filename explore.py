# ruff: noqa: PLR1711  -- marimo cells end with a bare `return` by design

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="FM Receiver: varicap tuning")


@app.cell
async def _():
    import dataclasses
    import importlib
    import sys

    import marimo as mo
    import numpy as np
    import pandas  # noqa: F401  -- needed by fm_receiver.data; listed so the browser loads it
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    if "pyodide" in sys.modules:
        # GitHub Pages: Python runs in the browser, the package is shipped as a zip next to the page
        import io
        import zipfile

        from pyodide.http import pyfetch

        _package_dir = "/home/pyodide/fm_receiver_pkg"
        _response = await pyfetch(str(mo.notebook_location() / "public" / "fm_receiver.zip"))
        zipfile.ZipFile(io.BytesIO(await _response.bytes())).extractall(_package_dir)
        sys.path.insert(0, _package_dir)

    # importlib instead of `import fm_receiver`, so the browser does not look for it on PyPI
    data = importlib.import_module("fm_receiver.data")
    model = importlib.import_module("fm_receiver.model")
    _units = importlib.import_module("fm_receiver.units")
    MHz, dB, mV, per_MHz = _units.MHz, _units.dB, _units.mV, _units.per_MHz

    return (
        MHz,
        dB,
        data,
        dataclasses,
        go,
        mV,
        make_subplots,
        mo,
        model,
        np,
        per_MHz,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Варикапне налаштування вхідного контуру FM-приймача

    Вхідний контур приймача діапазону **88–108 МГц** перебудовується варикапом —
    ємністю, якою керують напругою. Конспект показує, як параметри контуру
    впливають на напругу налаштування, вибірковість і пригнічення дзеркального каналу.

    Змінюй параметри повзунками — усі графіки, таблиця й висновки перераховуються самі.
    """)
    return


@app.cell
def _(mo):
    mo.accordion(
        {
            "Теорія: еквівалентна схема і формули": mo.md(
                r"""
                Паралельний контур $R_\mathrm{loss} \parallel L \parallel C_\mathrm{par} \parallel C_v(U)$,
                живлення від джерела струму.

                **Налаштування.** Ємність для резонансу на $f_0$ і ємність варикапа:

                $$C(f_0) = \frac{1}{4\pi^2 f_0^2 L}, \qquad C_v = C - C_\mathrm{par}$$

                З характеристики варикапа $C_v(U) = C_{v0}/(1 + U/\varphi)^\gamma$ напруга налаштування:

                $$U(f_0) = \varphi\left[\left(\frac{C_{v0}}{C_v(f_0)}\right)^{1/\gamma} - 1\right]$$

                **Вибірковість.** АЧХ, добротність і смуга:

                $$K_U = \frac{1}{\sqrt{1 + \xi^2}}, \quad \xi = Q\left(\frac{f}{f_0} - \frac{f_0}{f}\right), \quad
                Q = 2\pi f_0 C R_\mathrm{loss}, \quad BW = \frac{f_0}{Q}$$

                **Дзеркальний канал.** $f_\mathrm{im} = f_0 + 2 f_\mathrm{IF}$, пригнічення
                $A = 10 \lg\left(1 + \xi(f_\mathrm{im})^2\right)$ дБ. Станція OK, якщо $A \ge A_\mathrm{th}$.
                $\xi$ рахується точно: наближення $2Q\,\Delta f / f_0$ при $2 f_\mathrm{IF}/f_0 \approx 0.2$
                завищує $\xi$ приблизно на $f_\mathrm{IF}/(f_0 + f_\mathrm{IF}) \approx 10\%$.

                **Допуск напруги.** Щоб частота не пішла більше ніж на $f_\mathrm{tol}$:
                $U_\mathrm{tol} = \dfrac{dU}{df_0} \, f_\mathrm{tol}$.
                """
            )
        }
    )
    return


@app.cell
def _(mo, model):
    _cp, _cvp, _fp = model.DEFAULT_CP, model.DEFAULT_CVP, model.DEFAULT_FP

    L_slider = mo.ui.slider(
        0.08, 0.12, 0.005, value=_cp.L * 1e6, label="L, μH", show_value=True
    )
    R_loss_slider = mo.ui.slider(
        0.5, 10, 0.1, value=_cp.R_loss * 1e-3, label="R_loss, kΩ", show_value=True
    )
    C_par_slider = mo.ui.slider(
        0, 8, 0.5, value=_cp.C_par * 1e12, label="C_par, pF", show_value=True
    )
    C_v0_slider = mo.ui.slider(
        40, 80, 1, value=_cvp.C_v0 * 1e12, label="C_v0, pF", show_value=True
    )
    phi_slider = mo.ui.slider(
        0.5, 1.0, 0.05, value=_cvp.phi, label="φ, V", show_value=True
    )
    gamma_slider = mo.ui.slider(
        0.3, 1.0, 0.05, value=_cvp.gamma, label="γ", show_value=True
    )
    f_IF_slider = mo.ui.slider(
        9, 12, 0.1, value=_fp.f_IF * 1e-6, label="f_IF, MHz", show_value=True
    )
    A_th_slider = mo.ui.slider(
        10, 40, 1, value=_fp.A_threshold, label="A_th, dB", show_value=True
    )
    f_tol_slider = mo.ui.slider(
        10, 200, 10, value=_fp.f_tol * 1e-3, label="f_tol, kHz", show_value=True
    )

    mo.vstack(
        [
            mo.md("## Параметри"),
            mo.hstack(
                [
                    mo.vstack(
                        [mo.md("**Контур**"), L_slider, R_loss_slider, C_par_slider]
                    ),
                    mo.vstack(
                        [mo.md("**Варикап**"), C_v0_slider, phi_slider, gamma_slider]
                    ),
                    mo.vstack(
                        [mo.md("**Приймач**"), f_IF_slider, A_th_slider, f_tol_slider]
                    ),
                ],
                justify="space-around",
            ),
        ]
    )
    return (
        A_th_slider,
        C_par_slider,
        C_v0_slider,
        L_slider,
        R_loss_slider,
        f_IF_slider,
        f_tol_slider,
        gamma_slider,
        phi_slider,
    )


@app.cell
def _(
    A_th_slider,
    C_par_slider,
    C_v0_slider,
    L_slider,
    R_loss_slider,
    dataclasses,
    f_IF_slider,
    f_tol_slider,
    gamma_slider,
    model,
    np,
    phi_slider,
):
    cp = dataclasses.replace(
        model.DEFAULT_CP,
        L=L_slider.value * 1e-6,
        R_loss=R_loss_slider.value * 1e3,
        C_par=C_par_slider.value * 1e-12,
    )
    cvp = dataclasses.replace(
        model.DEFAULT_CVP,
        C_v0=C_v0_slider.value * 1e-12,
        phi=phi_slider.value,
        gamma=gamma_slider.value,
    )
    fp = dataclasses.replace(
        model.DEFAULT_FP,
        f_IF=f_IF_slider.value * 1e6,
        A_threshold=A_th_slider.value,
        f_tol=f_tol_slider.value * 1e3,
    )
    f_0 = model.freq_set(fp)
    stations = np.array(fp.f_stations)
    return cp, cvp, f_0, fp, stations


@app.cell
def _(MHz, cp, cvp, f_0, go, mo, model, stations):
    _fig = go.Figure()
    _fig.add_scatter(x=MHz(f_0), y=model.U_v(f_0, cp, cvp), name="U(f₀)")
    _fig.add_scatter(
        x=MHz(stations),
        y=model.U_v(stations, cp, cvp),
        mode="markers+text",
        text=[f"{MHz(f):g}" for f in stations],
        textposition="top left",
        name="stations",
    )
    _fig.update_layout(
        xaxis_title="f₀, MHz",
        yaxis_title="U, V",
        template="plotly_white",
        height=380,
        margin={"t": 30},
    )

    mo.vstack(
        [
            mo.md(
                "## Налаштування\n"
                "Напруга на варикапі, потрібна для налаштування на частоту $f_0$. "
                "Крива опукла: до верхнього краю діапазону напруга росте швидше."
            ),
            _fig,
        ]
    )
    return


@app.cell
def _(mo):
    f_0_view_slider = mo.ui.slider(
        88,
        108,
        0.1,
        value=100,
        label="Частота налаштування f₀, MHz",
        show_value=True,
        full_width=True,
    )
    return (f_0_view_slider,)


@app.cell
def _(MHz, cp, dB, f_0_view_slider, fp, go, mo, model, np):
    _f_0 = f_0_view_slider.value * 1e6
    _f = np.linspace(80e6, 135e6, 1101)
    _f_im = model.f_im(_f_0, fp)
    _K_im = dB(model.K_U(_f_im, _f_0, cp))

    _fig = go.Figure()
    _fig.add_scatter(x=MHz(_f), y=dB(model.K_U(_f, _f_0, cp)), name="K_U(f)")
    _fig.add_scatter(
        x=[MHz(_f_im)],
        y=[_K_im],
        mode="markers+text",
        text=[f"f_im = {MHz(_f_im):.1f} MHz<br>A = {-_K_im:.1f} dB"],
        textposition="bottom center",
        name="image channel",
    )
    _fig.add_hline(y=-fp.A_threshold, line_dash="dash", line_color="grey")
    _fig.update_layout(
        xaxis_title="f, MHz",
        yaxis_title="K_U, dB",
        yaxis_range=[-45, 3],
        template="plotly_white",
        height=380,
        margin={"t": 30},
    )

    mo.vstack(
        [
            mo.md(
                "## АЧХ і дзеркальний канал\n"
                "АЧХ контуру, налаштованого на $f_0$. Маркер показує, наскільки контур "
                "послаблює сигнал на частоті дзеркального каналу; пунктир — поріг $-A_\\mathrm{th}$."
            ),
            f_0_view_slider,
            _fig,
        ]
    )
    return


@app.cell
def _(MHz, cp, f_0, fp, make_subplots, mo, model, stations):
    _fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=("Q", "BW, MHz", "A, dB"),
        horizontal_spacing=0.08,
    )
    _fig.add_scatter(x=MHz(f_0), y=model.Q(f_0, cp), row=1, col=1, showlegend=False)
    _fig.add_scatter(
        x=MHz(f_0), y=MHz(model.BW(f_0, cp)), row=1, col=2, showlegend=False
    )
    _fig.add_scatter(x=MHz(f_0), y=model.A(f_0, cp, fp), row=1, col=3, showlegend=False)
    _fig.add_scatter(
        x=MHz(stations),
        y=model.A(stations, cp, fp),
        mode="markers",
        row=1,
        col=3,
        showlegend=False,
    )
    _fig.add_hline(y=fp.A_threshold, line_dash="dash", line_color="grey", row=1, col=3)
    _fig.update_xaxes(title_text="f₀, MHz")
    _fig.update_layout(template="plotly_white", height=340, margin={"t": 40})

    mo.vstack(
        [
            mo.md(
                "## Вибірковість по діапазону\n"
                "Добротність падає з частотою (при сталому $R_\\mathrm{loss}$), тому смуга "
                "розширюється, а пригнічення дзеркального каналу погіршується до верхнього краю."
            ),
            _fig,
        ]
    )
    return


@app.cell
def _(MHz, cp, cvp, f_0, fp, mV, make_subplots, mo, model, per_MHz):
    _fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "dU/df₀, V/MHz",
            f"U_tol, mV (f_tol = {fp.f_tol * 1e-3:g} kHz)",
        ),
    )
    _fig.add_scatter(
        x=MHz(f_0),
        y=per_MHz(model.dU_df_0(f_0, cp, cvp)),
        row=1,
        col=1,
        showlegend=False,
    )
    _fig.add_scatter(
        x=MHz(f_0), y=mV(model.U_tol(f_0, cp, fp, cvp)), row=1, col=2, showlegend=False
    )
    _fig.update_xaxes(title_text="f₀, MHz")
    _fig.update_layout(template="plotly_white", height=320, margin={"t": 40})

    mo.vstack(
        [
            mo.md(
                "## Вимоги до джерела напруги\n"
                "Чим крутіша $U(f_0)$, тим більша похибка напруги допустима при тому самому $f_\\mathrm{tol}$."
            ),
            _fig,
        ]
    )
    return


@app.cell
def _(cp, cvp, data, fp, mo):
    _, stations_table = data.f_stations_data(fp=fp, cp=cp, cvp=cvp)

    mo.vstack(
        [
            mo.md("## Станції"),
            mo.ui.table(stations_table.reset_index(), selection=None, pagination=False),
        ]
    )
    return (stations_table,)


@app.cell
def _(fp, mo, stations_table):
    _A = stations_table["A, dB"]
    _weak = stations_table[stations_table["status"] == "WEAK"]
    _worst = _A.idxmin()

    if _weak.empty:
        _verdict = mo.callout(
            mo.md(
                f"**Усі {len(stations_table)} станцій OK.** Найменший запас — "
                f"{_A.min() - fp.A_threshold:.1f} дБ на {_worst:g} МГц "
                f"(A = {_A.min():.1f} дБ при порозі {fp.A_threshold:g} дБ)."
            ),
            kind="success",
        )
    else:
        _list = ", ".join(f"{f:g}" for f in _weak.index)
        _verdict = mo.callout(
            mo.md(
                f"**WEAK IMAGE REJECTION: {len(_weak)} з {len(stations_table)} станцій** "
                f"({_list} МГц). Найгірша — {_worst:g} МГц, A = {_A.min():.1f} дБ "
                f"при порозі {fp.A_threshold:g} дБ."
            ),
            kind="danger",
        )

    mo.vstack([mo.md("## Висновок"), _verdict])
    return


if __name__ == "__main__":
    app.run()
