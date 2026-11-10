# Propuesta de cambios mínimos al firmware (v1 → v2). PENDIENTE DE APROBACIÓN

La base es `Codigo_ESP.txt` de la v1. Se mantienen el mismo diagrama de bloques, la misma trama BLE (`Resistencia|Batería%|TiempoCarga|VoltajeBat|Modo`), los mismos UUID y la misma lógica del loop.
Hay **4 cambios**; todo lo demás queda igual línea por línea.

## 1. Pines nuevos (tras `pinPulse`)
```cpp
const int pinRangeA = 3;   // GPIO3: conecta R_A (rango 0,5 A)
const int pinRangeB = 8;   // GPIO8: conecta R_B (rango 0,1 A); pull-up de 10 k (strapping)
const int pinSCLK = 4, pinMISO = 5, pinMOSI = 6, pinCS = 2;   // ADS1220 (DOUT/DRDY en MISO)
const float R_SHUNT = 0.100;  // patrón único v2 (mismo valor en los 3 modos)
```

## 2. Selección electrónica de rango (reemplaza al interruptor SP3T)
```cpp
void setRange(uint8_t modo) {        // 1 = 0,1 A · 2 = 0,5 A · 3 = 1 A
  digitalWrite(pinRangeA, modo == 2 ? HIGH : LOW);
  digitalWrite(pinRangeB, modo == 1 ? HIGH : LOW);
}
```
- En `setup()`: `pinMode(pinRangeA, OUTPUT); pinMode(pinRangeB, OUTPUT); setRange(1);`. Arranca en el rango de menor corriente.
- En `onWrite()`, después de leer `current_mode` y `active_r_ref`, agregar:
```cpp
          setRange(current_mode);
          // La app de la v1 envía R_REF nominal 1,0 / 0,2 / 0,1 según el modo; en la v2 el patrón es siempre 0,100 Ω.
          // Se acepta el valor de la app solo como calibración fina del shunt (±10 %); si no, se usa R_SHUNT.
          if (active_r_ref < 0.09 || active_r_ref > 0.11) active_r_ref = R_SHUNT;
```
  Con esto **la app no necesita cambios**.

## 3. Aviso de "punta abierta" (fuentes de 10 µA de detección del ADS1220)
```cpp
#include <SPI.h>
void adsWrite(uint8_t reg, uint8_t val) {
  digitalWrite(pinCS, LOW); SPI.transfer(0x40 | (reg << 2)); SPI.transfer(val); digitalWrite(pinCS, HIGH);
}
long adsReadOnce() {                         // conversión única (20 SPS) y lectura de 24 bits
  digitalWrite(pinCS, LOW); SPI.transfer(0x08); digitalWrite(pinCS, HIGH);   // START/SYNC
  delay(60);
  digitalWrite(pinCS, LOW); SPI.transfer(0x10);                               // RDATA
  long v = ((long)SPI.transfer(0) << 16) | ((long)SPI.transfer(0) << 8) | SPI.transfer(0);
  digitalWrite(pinCS, HIGH);
  if (v & 0x800000) v -= 0x1000000;
  return v;
}
bool puntaAbierta() {
  adsWrite(0, 0x05);   // MUX = AIN0-AIN1 (sensado S+/S-), ganancia 4, PGA bypass
  adsWrite(1, 0x01);   // 20 SPS, single-shot, BCS = 1 (fuentes de 10 µA activas)
  adsWrite(2, 0x00);   // referencia interna 2,048 V
  adsWrite(3, 0x02);   // DOUT/DRDY combinado
  long code = adsReadOnce();
  adsWrite(1, 0x00);   // apaga las fuentes de detección
  return code > 0x7F0000 || code < -0x7F0000;   // sensado abierto -> lectura a fondo de escala
}
```
- En `setup()`: `pinMode(pinCS, OUTPUT); digitalWrite(pinCS, HIGH); SPI.begin(pinSCLK, pinMISO, pinMOSI, pinCS); SPI.setDataMode(SPI_MODE1);`.
- En `loop()`, antes de generar el pulso:
```cpp
    if (current_mode != 255 && puntaAbierta()) {
      resistencia = 0; unidad = ""; strForzado = "PUNTA ABIERTA";   // la app muestra este texto tal cual
    }
```
  Para esto se declara `String strForzado = "";` y se usa `strResistencia = (strForzado.length() ? strForzado : ...)`.
- **Fundamento:** con el sensado conectado, 10 µA × (RX + R_ADS) produce unos pocos mV, muy por debajo del fondo de escala (±512 mV con G = 4). Con una punta S abierta, la entrada va al riel y la lectura se satura. Así lo describe TI en SBAS501D, sección 8.3.10 *Sensor Detection*.

## 4. Nota
El firmware de la v1 no medía realmente: devolvía valores fijos (854,321 mΩ, etc.). Esta propuesta **no cambia eso**, por la regla de "firmware mínimo". La lectura real (VX y VREF con ON/OFF y el cociente) está descrita en el informe y se implementaría con las mismas funciones `adsWrite`/`adsReadOnce` cambiando el MUX (AIN0-AIN1 y AIN2-AIN3).
