import numpy as np
import matplotlib.pyplot as plt
import simpy
import os
import random

# SIMULACIÓN DE REACTOR QUÍMICO

class Reactor:
    def __init__(self, temperatura_inicial, tasa_entrada_media, tasa_entrada_desviacion, eficiencia, capacidad_enfriamiento):
        self.temperatura = temperatura_inicial  # Temperatura inicial del reactor
        self.tasa_entrada_media = tasa_entrada_media  # Media de la tasa de entrada de reactivos
        self.tasa_entrada_desviacion = tasa_entrada_desviacion  # Desviación estándar de la tasa de entrada
        self.eficiencia = eficiencia  # Eficiencia de la reacción a 150°C
        self.capacidad_enfriamiento = capacidad_enfriamiento  # Capacidad de enfriamiento del sistema
        self.producto_generado = 0  # Cantidad total de producto generado
        self.temperaturas = []  # Lista para almacenar la temperatura en cada paso de tiempo
        self.tasas_entrada = []  # Lista para almacenar la tasa de entrada en cada paso de tiempo
        self.eficiencias = []  # Lista para almacenar la eficiencia en cada paso de tiempo
        self.producto_acumulado = []  # Lista para almacenar el producto acumulado en cada paso de tiempo
        self.temperatura_objetivo = 150  # Temperatura objetivo en °C
        self.rango_temperatura_optima = (145, 155)  # Rango de temperatura óptima

    def calcular_calor_generado(self, tasa_entrada):
        # Mejora: Cálculo más realista del calor generado
        calor_especifico = 4.2  # kJ/kg·°C (aproximación para soluciones acuosas)
        calor_reaccion = 250  # kJ/kg (valor hipotético para la reacción)
        return tasa_entrada * calor_reaccion

    def calcular_eficiencia_actual(self):
        # Mejora: Función de eficiencia más realista con degradación gradual
        if self.rango_temperatura_optima[0] <= self.temperatura <= self.rango_temperatura_optima[1]:
            return self.eficiencia
        else:
            # Degradación exponencial de la eficiencia fuera del rango óptimo
            desviacion = min(
                abs(self.temperatura - self.rango_temperatura_optima[0]),
                abs(self.temperatura - self.rango_temperatura_optima[1])
            )
            factor = np.exp(-0.02 * desviacion)
            return self.eficiencia * max(0.2, factor)

    def simular_paso(self, dt):
        # Validación de entrada
        if dt <= 0:
            raise ValueError("El paso de tiempo debe ser positivo")
        
        # Simular la tasa de entrada de reactivos (distribución normal)
        tasa_entrada = max(0, np.random.normal(self.tasa_entrada_media, self.tasa_entrada_desviacion))
        self.tasas_entrada.append(tasa_entrada)

        # Calcular el calor generado por la reacción (modelo más realista)
        calor_generado = self.calcular_calor_generado(tasa_entrada)

        # Calcular el calor disipado por el sistema de enfriamiento
        calor_disipado = self.capacidad_enfriamiento * (self.temperatura - self.temperatura_objetivo)

        # Constante de capacidad térmica del reactor (kJ/°C)
        capacidad_termica = 5000

        # Ecuación diferencial de balance térmico mejorada
        dT_dt = (calor_generado - calor_disipado) / capacidad_termica
        self.temperatura = max(0, self.temperatura + dT_dt * dt)  # Impedir temperatura negativa

        # Almacenar la temperatura actual
        self.temperaturas.append(self.temperatura)

        # Calcular la eficiencia actual
        eficiencia_actual = self.calcular_eficiencia_actual()
        self.eficiencias.append(eficiencia_actual * 100)  # Almacenar en porcentaje

        # Calcular la producción del producto final
        produccion = tasa_entrada * eficiencia_actual * dt
        self.producto_generado += produccion
        self.producto_acumulado.append(self.producto_generado)

def simulacion_reactor(tiempo_simulacion, temperatura_inicial, tasa_entrada_media, tasa_entrada_desviacion, eficiencia, capacidad_enfriamiento):
    # Validación de entrada
    if tiempo_simulacion <= 0:
        raise ValueError("El tiempo de simulación debe ser positivo")
    if temperatura_inicial < 0:
        raise ValueError("La temperatura inicial no puede ser negativa")
    if tasa_entrada_media <= 0:
        raise ValueError("La tasa de entrada media debe ser positiva")
    if tasa_entrada_desviacion < 0:
        raise ValueError("La desviación estándar no puede ser negativa")
    if eficiencia <= 0 or eficiencia > 1:
        raise ValueError("La eficiencia debe estar entre 0 y 1")
    if capacidad_enfriamiento <= 0:
        raise ValueError("La capacidad de enfriamiento debe ser positiva")

    # Crear el reactor
    reactor = Reactor(temperatura_inicial, tasa_entrada_media, tasa_entrada_desviacion, eficiencia, capacidad_enfriamiento)

    # Configurar el paso de tiempo (en minutos)
    dt = 0.1  # Paso de tiempo en minutos
    tiempo_total = tiempo_simulacion * 60  # Convertir horas a minutos

    # Simular el proceso
    tiempo = np.arange(0, tiempo_total, dt)
    for t in tiempo:
        reactor.simular_paso(dt)

    # Métricas
    producto_total = reactor.producto_generado
    temperatura_promedio = np.mean(reactor.temperaturas)
    variabilidad_temperatura = np.std(reactor.temperaturas)
    eficiencia_global = (producto_total / (reactor.tasa_entrada_media * tiempo_total)) * 100
    tiempo_fuera_rango = np.sum([1 for temp in reactor.temperaturas if temp < 145 or temp > 155]) * dt
    porcentaje_tiempo_fuera_rango = (tiempo_fuera_rango / tiempo_total) * 100

    # Resultados
    print("\n--- Resultados de la Simulación ---")
    print(f"Cantidad total de producto generado: {producto_total:.2f} litros")
    print(f"Temperatura promedio del reactor: {temperatura_promedio:.2f} °C")
    print(f"Variabilidad de la temperatura: {variabilidad_temperatura:.2f} °C")
    print(f"Eficiencia global del proceso: {eficiencia_global:.2f} %")
    print(f"Tiempo fuera del rango óptimo: {tiempo_fuera_rango:.2f} minutos ({porcentaje_tiempo_fuera_rango:.2f}%)")

    # Conclusiones y recomendaciones
    print("\n--- Conclusiones y Recomendaciones ---")
    if variabilidad_temperatura > 5:
        print("Conclusión: La temperatura del reactor presenta alta variabilidad.")
        if tasa_entrada_desviacion > 0.5:
            print("Recomendación: Reducir la variabilidad en la tasa de entrada de reactivos.")
        else:
            print("Recomendación: Aumentar la capacidad de enfriamiento del sistema.")
    else:
        print("Conclusión: La temperatura del reactor es estable.")

    if eficiencia_global < 80:
        print("Conclusión: La eficiencia global del proceso es baja.")
        if porcentaje_tiempo_fuera_rango > 20:
            print("Recomendación: Mejorar el control de temperatura para mantenerla dentro del rango óptimo.")
        else:
            print("Recomendación: Revisar otros factores que afectan la eficiencia del proceso.")
    else:
        print("Conclusión: La eficiencia del proceso es adecuada.")

    # Visualización mejorada
    plt.figure(figsize=(12, 10))
    
    # Gráfico de temperatura
    plt.subplot(3, 1, 1)
    plt.plot(tiempo, reactor.temperaturas, label="Temperatura (°C)", color="red")
    plt.axhline(y=150, color="black", linestyle="--", label="Temperatura objetivo (150°C)")
    plt.axhspan(145, 155, alpha=0.2, color="green", label="Rango óptimo (145-155°C)")
    plt.xlabel("Tiempo (minutos)")
    plt.ylabel("Temperatura (°C)")
    plt.legend()
    plt.title("Temperatura del Reactor en el Tiempo")
    plt.grid(True, linestyle="--", alpha=0.7)
    
    # Gráfico de tasa de entrada
    plt.subplot(3, 1, 2)
    plt.plot(tiempo, reactor.tasas_entrada, label="Tasa de entrada (L/min)", color="blue")
    plt.axhline(y=tasa_entrada_media, color="darkblue", linestyle="--", label=f"Tasa media ({tasa_entrada_media} L/min)")
    plt.xlabel("Tiempo (minutos)")
    plt.ylabel("Tasa de entrada (L/min)")
    plt.legend()
    plt.title("Tasa de Entrada de Reactivos en el Tiempo")
    plt.grid(True, linestyle="--", alpha=0.7)
    
    # Gráfico de eficiencia y producto acumulado
    plt.subplot(3, 1, 3)
    plt.plot(tiempo, reactor.eficiencias, label="Eficiencia (%)", color="green")
    plt.xlabel("Tiempo (minutos)")
    plt.ylabel("Eficiencia (%)")
    plt.legend(loc="upper left")
    plt.title("Eficiencia y Producción Acumulada")
    plt.grid(True, linestyle="--", alpha=0.7)
    
    # Agregar eje secundario para la producción acumulada
    ax2 = plt.twinx()
    ax2.plot(tiempo, reactor.producto_acumulado, label="Producto acumulado (L)", color="purple", linestyle="--")
    ax2.set_ylabel("Producto acumulado (L)")
    ax2.legend(loc="upper right")
    
    plt.tight_layout()
    plt.show()

def ejecutar_simulacion_reactor():
    limpiar_pantalla()
    print("=== Simulación de Reactor de Mezcla Continua ===")
    print("El reactor opera idealmente a 150°C con una eficiencia del 90%.")
    print("La temperatura afecta directamente la eficiencia del proceso.")
    print("La tasa de entrada de reactivos sigue una distribución normal.")
    print("=" * 50)
    
    try:
        tiempo_simulacion = float(input("Duración de la simulación (en horas): "))
        temperatura_inicial = float(input("Temperatura inicial del reactor (°C): "))
        tasa_entrada_media = float(input("Tasa de entrada media de reactivos (L/min): "))
        tasa_entrada_desviacion = float(input("Desviación estándar de la tasa de entrada (L/min): "))
        eficiencia = float(input("Eficiencia de la reacción a 150°C (%): ")) / 100
        capacidad_enfriamiento = float(input("Capacidad de enfriamiento del sistema (W/°C): "))

        # Ejecutar la simulación
        simulacion_reactor(tiempo_simulacion, temperatura_inicial, tasa_entrada_media, tasa_entrada_desviacion, eficiencia, capacidad_enfriamiento)
    
    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nError inesperado: {e}")
    
    input("\nPresione Enter para volver al menú principal...")

# SIMULACIÓN DE TIENDA DE COMESTIBLES

class TiendaComestibles:
    def __init__(self, env, num_cajas, stock_inicial, umbral_reabastecimiento, lote_reabastecimiento, tiempo_reabastecimiento):
        self.env = env
        self.caja = simpy.Resource(env, num_cajas)
        self.stock = stock_inicial
        self.umbral_reabastecimiento = umbral_reabastecimiento
        self.lote_reabastecimiento = lote_reabastecimiento
        self.tiempo_reabastecimiento = tiempo_reabastecimiento
        self.clientes_atendidos = 0
        self.clientes_sin_stock = 0
        self.tiempos_espera = []
        self.tiempos_total = []
        self.veces_sin_stock = 0
        self.reabastecimientos = 0

    def atender_cliente(self, cliente):
        llegada = self.env.now
        print(f"Cliente {cliente} llega a la tienda a las {llegada:.2f} minutos")

        with self.caja.request() as request:
            yield request
            espera = self.env.now - llegada
            self.tiempos_espera.append(espera)
            print(f"Cliente {cliente} comienza a ser atendido a las {self.env.now:.2f} minutos. Tiempo de espera: {espera:.2f} minutos")

            # Verificar stock
            if self.stock > 0:
                self.stock -= 1
                tiempo_servicio = np.random.exponential(5)
                yield self.env.timeout(tiempo_servicio)
                self.clientes_atendidos += 1
                tiempo_total = self.env.now - llegada
                self.tiempos_total.append(tiempo_total)
                print(f"Cliente {cliente} termina de ser atendido a las {self.env.now:.2f} minutos. Tiempo total en la tienda: {tiempo_total:.2f} minutos")
            else:
                self.clientes_sin_stock += 1
                self.veces_sin_stock += 1
                print(f"Cliente {cliente} no pudo ser atendido por falta de stock a las {self.env.now:.2f} minutos")

            # Reabastecer si es necesario
            if self.stock < self.umbral_reabastecimiento:
                self.env.process(self.reabastecer())

    def reabastecer(self):
        print(f"Reabasteciendo inventario a las {self.env.now:.2f} minutos. Stock actual: {self.stock}")
        yield self.env.timeout(self.tiempo_reabastecimiento)
        self.stock += self.lote_reabastecimiento
        self.reabastecimientos += 1
        print(f"Inventario reabastecido a las {self.env.now:.2f} minutos. Stock actual: {self.stock}")

def generar_clientes(env, tienda, tasa_llegada):
    cliente = 0
    while True:
        yield env.timeout(np.random.exponential(60 / tasa_llegada))
        cliente += 1
        env.process(tienda.atender_cliente(cliente))

def simulacion_tienda(tiempo_simulacion, tasa_llegada, num_cajas, stock_inicial, umbral_reabastecimiento, lote_reabastecimiento, tiempo_reabastecimiento):
    env = simpy.Environment()
    tienda = TiendaComestibles(env, num_cajas, stock_inicial, umbral_reabastecimiento, lote_reabastecimiento, tiempo_reabastecimiento)
    env.process(generar_clientes(env, tienda, tasa_llegada))
    env.run(until=tiempo_simulacion)

    # Métricas
    tiempo_espera_promedio = np.mean(tienda.tiempos_espera) if tienda.tiempos_espera else 0
    tiempo_total_promedio = np.mean(tienda.tiempos_total) if tienda.tiempos_total else 0
    clientes_sin_stock = tienda.clientes_sin_stock
    porcentaje_sin_stock = (clientes_sin_stock / (tienda.clientes_atendidos + clientes_sin_stock)) * 100 if (tienda.clientes_atendidos + clientes_sin_stock) > 0 else 0

    # Cálculo de métricas adicionales
    utilizacion_cajas = len(tienda.tiempos_espera) / tiempo_simulacion * 100 if tiempo_simulacion > 0 else 0
    stock_por_hora = tienda.stock / (tiempo_simulacion / 60) if tiempo_simulacion > 0 else 0

    print("\n--- Resultados de la Simulación ---")
    print(f"Tiempo de espera promedio: {tiempo_espera_promedio:.2f} minutos")
    print(f"Tiempo total promedio en la tienda: {tiempo_total_promedio:.2f} minutos")
    print(f"Número de clientes que no pudieron ser atendidos por falta de stock: {clientes_sin_stock} ({porcentaje_sin_stock:.2f}%)")
    print(f"Clientes atendidos: {tienda.clientes_atendidos}")
    print(f"Número de reabastecimientos realizados: {tienda.reabastecimientos}")
    print(f"Veces que se quedó sin stock: {tienda.veces_sin_stock}")
    print(f"Utilización de cajas: {utilizacion_cajas:.2f}%")
    print(f"Stock restante por hora de operación: {stock_por_hora:.2f} unidades/hora")

    # Conclusiones y recomendaciones
    print("\n--- Conclusiones y Recomendaciones ---")
    if tiempo_espera_promedio > 10:
        print("Conclusión: El tiempo de espera promedio es alto (más de 10 minutos).")
        print("Recomendación: Se recomienda aumentar el número de cajas o mejorar la eficiencia del servicio.")
    else:
        print("Conclusión: El tiempo de espera promedio es aceptable (menos de 10 minutos).")
        
    if clientes_sin_stock > 0:
        print("Conclusión: Hay clientes que no pudieron ser atendidos por falta de stock.")
        print("Recomendación: Se recomienda ajustar el umbral de reabastecimiento o aumentar el tamaño del lote de reabastecimiento.")
        
        if tienda.reabastecimientos > 10 and tiempo_simulacion <= 480:  # Más de 10 reabastecimientos en 8 horas o menos
            print("Recomendación adicional: El número de reabastecimientos es alto. Considere aumentar el tamaño del lote de reabastecimiento.")
        
        if tienda.veces_sin_stock > 5:
            print("Recomendación adicional: Se quedó sin stock frecuentemente. Considere reducir el tiempo de reabastecimiento o aumentar el umbral de reabastecimiento.")
    else:
        print("Conclusión: La gestión de inventario es adecuada, no hubo problemas de stock.")
        
    if utilizacion_cajas < 50:
        print("Conclusión: La utilización de cajas es baja.")
        print("Recomendación: Considere reducir el número de cajas para optimizar recursos.")
    elif utilizacion_cajas > 90:
        print("Conclusión: La utilización de cajas es muy alta.")
        print("Recomendación: Considere aumentar el número de cajas para reducir tiempos de espera.")

def ejecutar_simulacion_tienda():
    limpiar_pantalla()
    print("=" * 50)
    print("     SIMULACIÓN DE TIENDA DE COMESTIBLES")
    print("=" * 50)
    print("Parámetros de la simulación:")
    print("- Los clientes llegan con una tasa promedio configurable")
    print("- El tiempo de servicio sigue una distribución exponencial con media de 5 minutos")
    print("- El inventario se reabastece cuando cae por debajo del umbral configurado")
    print("=" * 50)
    
    try:
        tiempo_simulacion = float(input("Duración de la simulación (en horas): ")) * 60  # Convertir a minutos
        tasa_llegada = float(input("Tasa de llegada de clientes (clientes por hora, recomendado 10): "))
        num_cajas = int(input("Número de cajas de pago (recomendado 1): "))
        stock_inicial = int(input("Stock inicial de productos (recomendado 50): "))
        umbral_reabastecimiento = int(input("Umbral de reabastecimiento (recomendado 10): "))
        lote_reabastecimiento = int(input("Tamaño del lote de reabastecimiento (recomendado 50): "))
        tiempo_reabastecimiento = float(input("Tiempo de reabastecimiento (en minutos, recomendado 15): "))
        
        # Validación de entradas
        if tiempo_simulacion <= 0:
            raise ValueError("El tiempo de simulación debe ser positivo")
        if tasa_llegada <= 0:
            raise ValueError("La tasa de llegada debe ser positiva")
        if num_cajas <= 0:
            raise ValueError("El número de cajas debe ser positivo")
        if stock_inicial < 0:
            raise ValueError("El stock inicial no puede ser negativo")
        if umbral_reabastecimiento < 0:
            raise ValueError("El umbral de reabastecimiento no puede ser negativo")
        if lote_reabastecimiento <= 0:
            raise ValueError("El tamaño del lote debe ser positivo")
        if tiempo_reabastecimiento <= 0:
            raise ValueError("El tiempo de reabastecimiento debe ser positivo")
        
        print("\nEjecutando simulación...\n")
        simulacion_tienda(tiempo_simulacion, tasa_llegada, num_cajas, stock_inicial, umbral_reabastecimiento, lote_reabastecimiento, tiempo_reabastecimiento)
        
    except ValueError as e:
        print(f"\nError: Por favor ingrese valores numéricos válidos. {e}")
    except Exception as e:
        print(f"\nError inesperado: {e}")
    
    input("\nPresione Enter para volver al menú principal...")

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_principal():
    while True:
        limpiar_pantalla()
        print("=" * 50)
        print("     SISTEMA DE SIMULACIÓN DE PROBLEMAS")
        print("=" * 50)
        print("1. Simulación de Tienda de Comestibles")
        print("2. Simulación de Reactor de Mezcla Continua")
        print("3. Salir")
        print("=" * 50)
        
        opcion = input("Seleccione una opción (1-3): ")
        
        if opcion == "1":
            ejecutar_simulacion_tienda()
        elif opcion == "2":
            ejecutar_simulacion_reactor()
        elif opcion == "3":
            print("Gracias por usar el sistema de simulación. ¡Hasta pronto!")
            break
        else:
            input("Opción no válida. Presione Enter para continuar...")

# Asegurar que todas las librerías necesarias estén instaladas
def verificar_dependencias():
    try:
        import numpy
        import matplotlib.pyplot
        import simpy
    except ImportError as e:
        print(f"Error: Falta la librería {e.name}.")
        print("Por favor, instale las dependencias necesarias con:")
        print("pip install numpy matplotlib simpy")
        input("Presione Enter para salir...")
        exit(1)

# Ejecutar el programa principal
if __name__ == "__main__":
    verificar_dependencias()
    menu_principal()