# Resultados del Monte Carlo (LTspice, corridas reales)

Netlists: `mc_v2_modo1.cir` … `mc_v2_modo3.cir` (generados por `gen_mc.py`); logs `.log`; datos `mc_v2_modoN.csv`.
Modelos: OPAx376 de TI (SBOM406), IRLHM620 VDMOS de la biblioteca de LTspice. 500 corridas por rango.
Tolerancias (gaussiana, 3σ): R_SH 0,1 %, R_ADS 0,1 %, R_DV/R_ST/R_A/R_B/R_FB/R_G 1 %, C 5 %, Vos OPA376 25 µV,
offset ADC 4 µV, ganancia ADC 0,05 %, RDS(on) de Q3 0,55–0,70 Ω (uniforme), corriente de entrada ADC 2 nA/pin.
RX medida = R_SH,nominal · (VX,on − VX,off)/(VREF,on − VREF,off) (ecuación del firmware).

## Rango 0,1 A (RX real = 1000 mΩ)

| Magnitud | Media | Desv. estándar (σ) | Mín. | Máx. |
|---|---|---|---|---|
| Corriente I | 95.06 mA | 0.42 mA (0.44 %) | 93.80 mA | 96.35 mA |
| VSET | 9.517 mV | 0.041 mV | 9.394 mV | 9.633 mV |
| VX/VREF | 10.000112 | 3.45e-03 | 9.989833 | 10.009828 |
| RX medida | 1000.01125 mΩ | 0.34500 mΩ | 998.98328 mΩ | 1000.98281 mΩ |
| Error de RX | +0.0011 % | 0.0345 % (3σ = 0.104 %) | -0.1017 % | +0.0983 % |

Sensibilidad del error de RX (contribución a σ, regresión lineal):

| Parámetro | Coef. (% de RX por % o µV) | Contribución a σ(RX) | % de la varianza |
|---|---|---|---|
| R_SH (shunt 0,1 Ω, 0,1 %) | -1.0000 | 0.03450 % | 100.0 % |
| Vos OPA376 (±25 µV) | +0.0000 | 0.00001 % | 0.0 % |
| R_ADS1 1 k (0,1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_ADS2 1 k (0,1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_ST 1 k (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_ADS3 1 k (0,1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_FB 1 k (1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_B 105 Ω (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_ADS4 1 k (0,1 %) | -0.0000 | 0.00000 % | 0.0 % |
| RDS(on) Q3 | -0.0000 | 0.00000 % | 0.0 % |
| R_DV 33 k (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_A 976 Ω (1 %) | +0.0000 | 0.00000 % | 0.0 % |

## Rango 0,5 A (RX real = 100 mΩ)

| Magnitud | Media | Desv. estándar (σ) | Mín. | Máx. |
|---|---|---|---|---|
| Corriente I | 482.59 mA | 1.97 mA (0.41 %) | 477.29 mA | 490.48 mA |
| VSET | 48.659 mV | 0.198 mV | 48.122 mV | 49.414 mV |
| VX/VREF | 1.000011 | 3.45e-04 | 0.998983 | 1.000982 |
| RX medida | 100.00105 mΩ | 0.03450 mΩ | 99.89826 mΩ | 100.09821 mΩ |
| Error de RX | +0.0011 % | 0.0345 % (3σ = 0.104 %) | -0.1017 % | +0.0982 % |

Sensibilidad del error de RX (contribución a σ, regresión lineal):

| Parámetro | Coef. (% de RX por % o µV) | Contribución a σ(RX) | % de la varianza |
|---|---|---|---|
| R_SH (shunt 0,1 Ω, 0,1 %) | -1.0000 | 0.03450 % | 100.0 % |
| Vos OPA376 (±25 µV) | +0.0000 | 0.00000 % | 0.0 % |
| R_ADS1 1 k (0,1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_FB 1 k (1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_ADS2 1 k (0,1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_ST 1 k (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_ADS3 1 k (0,1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_ADS4 1 k (0,1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_DV 33 k (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_B 105 Ω (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| RDS(on) Q3 | -0.0000 | 0.00000 % | 0.0 % |
| R_A 976 Ω (1 %) | +0.0000 | 0.00000 % | 0.0 % |

## Rango 1 A (RX real = 10 mΩ)

| Magnitud | Media | Desv. estándar (σ) | Mín. | Máx. |
|---|---|---|---|---|
| Corriente I | 961.51 mA | 4.55 mA (0.47 %) | 948.48 mA | 976.83 mA |
| VSET | 97.032 mV | 0.456 mV | 95.680 mV | 98.502 mV |
| VX/VREF | 0.100001 | 3.45e-05 | 0.099898 | 0.100098 |
| RX medida | 10.00010 mΩ | 0.00345 mΩ | 9.98983 mΩ | 10.00982 mΩ |
| Error de RX | +0.0010 % | 0.0345 % (3σ = 0.104 %) | -0.1017 % | +0.0982 % |

Sensibilidad del error de RX (contribución a σ, regresión lineal):

| Parámetro | Coef. (% de RX por % o µV) | Contribución a σ(RX) | % de la varianza |
|---|---|---|---|
| R_SH (shunt 0,1 Ω, 0,1 %) | -1.0000 | 0.03450 % | 100.0 % |
| R_ADS1 1 k (0,1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_ADS2 1 k (0,1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_FB 1 k (1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_ST 1 k (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| Vos OPA376 (±25 µV) | +0.0000 | 0.00000 % | 0.0 % |
| R_ADS3 1 k (0,1 %) | +0.0000 | 0.00000 % | 0.0 % |
| R_DV 33 k (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_ADS4 1 k (0,1 %) | -0.0000 | 0.00000 % | 0.0 % |
| R_B 105 Ω (1 %) | -0.0000 | 0.00000 % | 0.0 % |
| RDS(on) Q3 | -0.0000 | 0.00000 % | 0.0 % |
| R_A 976 Ω (1 %) | +0.0000 | 0.00000 % | 0.0 % |

## Resumen

| Rango | RX real | Error medio | σ | 3σ | Peor caso | σ(I)/I |
|---|---|---|---|---|---|---|
| 0,1 A | 1000 mΩ | +0.0011 % | 0.0345 % | 0.104 % | 0.102 % | 0.44 % |
| 0,5 A | 100 mΩ | +0.0011 % | 0.0345 % | 0.104 % | 0.102 % | 0.41 % |
| 1 A | 10 mΩ | +0.0010 % | 0.0345 % | 0.104 % | 0.102 % | 0.47 % |

## Sensibilidad de la corriente I (no afecta a RX, pero fija el rango)

| Rango | Parámetro | % de la varianza de I |
|---|---|---|
| 0,1 A | R_DV 33 k (1 %) | 50.3 % |
| 0,1 A | R_B 105 Ω (1 %) | 41.9 % |
| 0,1 A | Vos OPA376 (±25 µV) | 4.0 % |
| 0,1 A | RDS(on) Q3 | 2.7 % |
| 0,5 A | R_DV 33 k (1 %) | 63.2 % |
| 0,5 A | R_A 976 Ω (1 %) | 18.3 % |
| 0,5 A | R_ST 1 k (1 %) | 17.5 % |
| 0,5 A | R_SH (shunt 0,1 Ω, 0,1 %) | 0.8 % |
| 1 A | R_ST 1 k (1 %) | 52.8 % |
| 1 A | R_DV 33 k (1 %) | 46.5 % |
| 1 A | R_SH (shunt 0,1 Ω, 0,1 %) | 0.6 % |
| 1 A | Vos OPA376 (±25 µV) | 0.0 % |

## Conclusiones
- **La única resistencia crítica para la exactitud de RX es el shunt R_SH**: explica el 100 % de la varianza del error (coeficiente −1: un shunt 0,1 % alto produce RX 0,1 % bajo).
- **Con el shunt de ±0,1 % (VPG CSM2512S)**, el error de RX tiene σ = 0,0345 % y 3σ = 0,104 % en los tres rangos (peor caso de 500 corridas: 0,102 %).
- **Lo que no afecta a RX:** R_DV, R_ST, R_A, R_B, R_FB, RDS(on) de Q3, el offset del OPA376, el offset y la ganancia del ADC, la corriente de entrada del ADC y el apareamiento de R_ADS. Todos cambian la corriente I (σ ≈ 0,4–0,5 %) o se cancelan en el cociente VX/VREF y con ON/OFF.
- **Tolerancias recomendadas:**
  - R_SH ±0,1 % o mejor con TCR ≤ 15 ppm/°C. Alternativa: shunt de 1 % más una calibración con un patrón usando el campo R_REF que ya tiene la app.
  - Divisor de VSET, R_A, R_B, R_FB y R_G: 1 % / 100 ppm de película gruesa (suficiente).
  - R_ADS: bastaría 1 %, porque su apareamiento no influye (con 2 nA de corriente de entrada el error es < 1 ppm). Se mantienen las de 0,1 % por su bajo ruido de película delgada, aunque podrían cambiarse por 1 % para ahorrar.
- **Limitaciones del modelo:** no incluye la INL ni el ruido del ADS1220, las FEM térmicas, el TCR ni el autocalentamiento. Esos efectos se tratan en `calculos/fase2_calculos.md` (ruido, INL) y los cancela la medición ON/OFF (FEM).


## Formas de onda

`mc_formas_de_onda.png` superpone las curvas I(RX) de las 500 corridas de cada rango, leídas de los `.raw` de LTspice (`graficar_mc.py`). La corrida de 1 A se repitió en `ondas_m3/` y dio `.meas` idénticos (semilla determinista). Ninguna corrida oscila: la dispersión aparece solo en la amplitud de la meseta. Los datos re-muestreados a 641 puntos están en `mc_curvas_I_modo{1,2,3}.csv`. Los `.raw` se borraron por su tamaño (unos 177 MB cada uno); se regeneran con `LTspice -b -ascii mc_v2_modoN.cir`.
