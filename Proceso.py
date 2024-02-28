import simpy
import random
import csv
import statistics

# Definimos intervalo aquí
intervalo = 5

class Proceso:
    def __init__(self, env, id, ram, cpu):
        self.env = env
        self.id = id
        self.ram = ram
        self.cpu = cpu
        self.cantRam = random.randint(1, 10)
        self.cantInstrucciones = random.randint(1, 10)
        self.tiempo_creacion = None
        self.tiempo_finalizacion = None
        self.tiempo_en_sistema = None

    def correr(self):
        yield self.env.timeout(random.expovariate(1.0/ intervalo))
        self.tiempo_creacion = self.env.now
        with self.ram.get(self.cantRam) as req:
            yield req
            yield self.env.process(self.ejecutar())

    def ejecutar(self):
        tiempo_inicio = self.env.now
        while self.cantInstrucciones > 0:
            with self.cpu.request() as req:
                yield req
                yield self.env.timeout(1)
                self.cantInstrucciones -= 3
        self.tiempo_finalizacion = self.env.now
        self.ram.put(self.cantRam)
        self.tiempo_en_sistema = self.tiempo_finalizacion - tiempo_inicio

def main():
    env = simpy.Environment()
    ram = simpy.Container(env, init=100, capacity=100)
    cpu = simpy.Resource(env, capacity=3)
    random.seed(42)
    procesos = []
    cantProcesos = 200

    for i in range(cantProcesos):
        proceso = Proceso(env, i, ram, cpu)
        procesos.append(proceso)
        env.process(proceso.correr())

    env.run()

    guardar_datos(procesos)
    promedio, desviacion_estandar = calcular_promedio_desviacion(procesos)
    print(f"Promedio de tiempo en sistema: {promedio}")
    print(f"Desviación estándar: {desviacion_estandar}")

def guardar_datos(procesos):
    nombre_archivo = "datos.csv"
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=["id", "tiempoCreacion", "tiempoFinalizacion", "tiempoEnSistema"])
        escritor_csv.writeheader()
        for proceso in procesos:
            escritor_csv.writerow({
                "id": proceso.id,
                "tiempoCreacion": proceso.tiempo_creacion,
                "tiempoFinalizacion": proceso.tiempo_finalizacion,
                "tiempoEnSistema": proceso.tiempo_en_sistema
            })
    print(f"Los datos se han almacenado en el archivo CSV: {nombre_archivo}")

def calcular_promedio_desviacion(procesos):
    tiempos_en_sistema = [proceso.tiempo_en_sistema for proceso in procesos if proceso.tiempo_en_sistema is not None]
    if tiempos_en_sistema:
        promedio = statistics.mean(tiempos_en_sistema)
        desviacion_estandar = statistics.stdev(tiempos_en_sistema)
        return promedio, desviacion_estandar
    else:
        return 0, 0

if __name__ == "__main__":
    main()
