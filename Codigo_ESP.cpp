// 1. PINES ANALÓGICOS DEL XIAO ESP32-C3
const int pinVref = A0;    // Pin conectado al selector manual (Vref)
const int pinVsense = A1;  // Pin que lee la salida de tu amplificador operacional
const int pinBateria = A2; // Pin que lee el voltaje de la batería

void setup() {
  Serial.begin(115200);
  
  // El ADC del XIAO ESP32-C3 tiene una resolución de 12 bits (0 a 4095)
  analogReadResolution(12);
}

void loop() {
  // ---------------------------------------------------------
  // 1. LEER EL SELECTOR MANUAL (Modo de inyección de corriente)
  // ---------------------------------------------------------
  int lecturaVref = analogRead(pinVref);
  float voltajeVref = (lecturaVref / 4095.0) * 3.3; // Convertir lectura a voltios
  
  float corrienteInyectada = 0.0;
  String unidad = "";

  // EJEMPLO: Ajusta estos voltajes según lo que diseñaron físicamente
  if (voltajeVref >= 2.5) {
    // MODO 1: Rango Alto (Ej. 1 Amperio de inyección)
    corrienteInyectada = 1.0; 
    unidad = "mΩ"; 
  } 
  else if (voltajeVref >= 1.0 && voltajeVref < 2.5) {
    // MODO 2: Rango Medio (Ej. 100 mA de inyección)
    corrienteInyectada = 0.1; 
    unidad = "mΩ";
  } 
  else {
    // MODO 3: Rango Bajo (Ej. 10 mA de inyección)
    corrienteInyectada = 0.01; 
    unidad = "µΩ"; 
  }

  // ---------------------------------------------------------
  // 2. LEER LA CAÍDA DE TENSIÓN Y CALCULAR RESISTENCIA
  // ---------------------------------------------------------
  int lecturaVsense = analogRead(pinVsense);
  float voltajeSense = (lecturaVsense / 4095.0) * 3.3; 
  
  // LEY DE OHM (R = V / I)
  float resistencia = 0.0;
  if (corrienteInyectada > 0) {
    // IMPORTANTE: Si usas un amplificador con ganancia (Ej. ganancia de 100), 
    // debes dividir voltajeSense entre esa ganancia antes de calcular.
    // Ejemplo real: resistencia = (voltajeSense / 100.0) / corrienteInyectada;
    resistencia = voltajeSense / corrienteInyectada;
  }

  // ---------------------------------------------------------
  // 3. LEER BATERÍA Y TIEMPO DE CARGA
  // ---------------------------------------------------------
  int lecturaBat = analogRead(pinBateria);
  float voltajeBat = (lecturaBat / 4095.0) * 3.3 * 2; // Asume divisor de tensión 1:1 para Lipo 4.2V
  
  int porcentajeBat = map(voltajeBat * 100, 320, 420, 0, 100); 
  if(porcentajeBat > 100) porcentajeBat = 100;
  if(porcentajeBat < 0) porcentajeBat = 0;

  int tiempoCarga = 0; // Aquí puedes poner la lógica que detecta si el USB está conectado

  // ---------------------------------------------------------
  // 4. EMPAQUETAR Y ENVIAR LOS DATOS A LA APP INVENTOR
  // ---------------------------------------------------------
  // Formatear la resistencia a 6 decimales y pegarle la unidad dinámica
  String stringResistencia = String(resistencia, 6) + " " + unidad;
  
  // Construir la cadena: "15.123456 mΩ|75|45"
  String datos = stringResistencia + "|" + String(porcentajeBat) + "|" + String(tiempoCarga);
  
  // Por ahora lo imprime en el Monitor Serie para que lo pruebes físicamente
  Serial.println(datos); 
  
  delay(500); // Enviar datos cada medio segundo
}