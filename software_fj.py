import abc, datetime

# 1. Función para guardar eventos y errores en un archivo de texto (Log)
def log(nivel, msg):
    with open("registro_errores.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] [{nivel}] {msg}\n")
        
 # 2. Excepciones personalizadas
class SoftwareFJError(Exception): pass
class ValidacionError(SoftwareFJError): pass
class NoDisponibleError(SoftwareFJError): pass

# 3. Clase abstracta general y Cliente con encapsulamiento
class Entidad(abc.ABC):
    def __init__(self, id_ent): self._id = id_ent
    @abc.abstractmethod
    def detalles(self): pass
    
class Cliente(Entidad):
    def __init__(self, id_c, nombre, correo):
        super().__init__(id_c)
        if len(nombre.strip()) < 3: raise ValidacionError("Nombre muy corto.")
        if "@" not in correo: raise ValidacionError("Correo inválido.")
        self.__nombre, self.__correo = nombre, correo  # Datos encapsulados (privados)

    def get_nombre(self): return self.__nombre
    def detalles(self): return f"Cliente: {self.__nombre} ({self.__correo})"
    
    # 4. Clase abstracta Servicio y 3 servicios especializados (Herencia y Polimorfismo)
class Servicio(abc.ABC):
    def __init__(self, id_s, nombre, costo):
        if costo <= 0: raise ValidacionError("El costo debe ser mayor a 0.")
        self.id_s, self.nombre, self.costo, self.disponible = id_s, nombre, costo, True
        
    @abc.abstractmethod 
    def calcular_costo(self, duracion, iva=0.19, extra=0.0): pass  # Sobrecarga con parámetros opcionales
    @abc.abstractmethod
    def describir(self): pass

class ReservaSala(Servicio):
    def calcular_costo(self, duracion, iva=0.19, descuento=0.0):
        if duracion <= 0: raise ValidacionError("Horas inválidas.")
        sub = self.costo * duracion
        return sub + (sub * iva) - (sub * descuento)
    def describir(self): return f"Sala: {self.nombre}"
    
class AlquilerEquipo(Servicio):
    def calcular_costo(self, duracion, iva=0.19, seguro=0.05):
        if duracion <= 0: raise ValidacionError("Días inválidos.")
        sub = self.costo * duracion
        return sub + (sub * iva) + (sub * seguro)
    def describir(self): return f"Equipo: {self.nombre}"

class Asesoria(Servicio):
    def calcular_costo(self, duracion, iva=0.19, urgencia=0):
        if duracion <= 0: raise ValidacionError("Horas inválidas.")
        return (self.costo * duracion) * (1 + iva) + urgencia
    def describir(self): return f"Asesoría: {self.nombre}"
    
    # 5. Clase Reserva con try/except/else/finally y encadenamiento de excepciones
class Reserva:
    def __init__(self, cliente, servicio, duracion):
        self.cliente, self.servicio, self.duracion, self.estado = cliente, servicio, duracion, "Pendiente"

    def procesar(self):
        try:
            if not self.servicio.disponible:
                raise NoDisponibleError(f"'{self.servicio.nombre}' no está disponible.")
            total = self.servicio.calcular_costo(self.duracion)
        except ValidacionError as e:
            self.estado = "Fallida"
            log("ERROR", f"Validación en reserva: {e}")
            raise SoftwareFJError("Error de datos al procesar reserva.") from e  # Encadenamiento
        except NoDisponibleError as e:
            self.estado = "Rechazada"
            log("WARN", str(e))
            print(f"Alerta: {e}")
        else:
            self.estado, self.servicio.disponible = "Confirmada", False
            log("INFO", f"Reserva OK: {self.cliente.get_nombre()} - {self.servicio.nombre} (${total:,.0f})")
            print(f"Confirmada: {self.servicio.describir()} | Total: ${total:,.0f}")
        finally:
            print(f"-> Estado final: {self.estado}")

    def cancelar(self):
        if self.estado == "Confirmada":
            self.estado, self.servicio.disponible = "Cancelada", True
            log("INFO", f"Cancelada: {self.servicio.nombre}")
            print(f"Reserva cancelada: {self.servicio.nombre} libre.")
            
            # 6. Simulación de 10 operaciones (sin base de datos, usando listas)
clientes, servicios, reservas = [], [], []
print("=== SIMULACIÓN SOFTWARE FJ ===")

# Op 1 a 3: Clientes (1 válido, 2 inválidos)
for datos in [("1", "Empresa Alpha", "info@alpha.com"), ("2", "Al", "a@b.com"), ("3", "Gamma", "sinarroba.com")]:
    try:
        c = Cliente(*datos)
        clientes.append(c)
        print(f"OK -> {c.detalles()}")
        log("INFO", f"Cliente creado: {c.get_nombre()}")
    except ValidacionError as e:
        print(f"Error controlado (Cliente): {e}")
        log("ERROR", f"Cliente fallido: {e}")
        
# Op 4 y 5: Servicios (3 válidos, 1 inválido)
s1, s2, s3 = ReservaSala("S1", "Sala VIP", 50000), AlquilerEquipo("E1", "Proyector", 25000), Asesoria("A1", "Cloud", 150000)
servicios.extend([s1, s2, s3])    
try:
    ReservaSala("S9", "Sala Mala", -5000)
except ValidacionError as e:
    print(f"Error controlado (Servicio): {e}")
    log("ERROR", f"Servicio fallido: {e}")
    
# Op 6 a 9: Reservas (Exitosa, Fallida por ocupación, Cancelación, Fallida encadenada)
r1 = Reserva(clientes[0], s1, 3); reservas.append(r1); r1.procesar()   # Op 6: Exitosa
r2 = Reserva(clientes[0], s1, 2); reservas.append(r2); r2.procesar()   # Op 7: Falla (ocupada)
r1.cancelar()

try:
    r3 = Reserva(clientes[0], s2, -4); reservas.append(r3); r3.procesar()  # Op 9: Falla encadenada
except SoftwareFJError as e:
    print(f"Excepción encadenada: {e} | Causa: {e.__cause__}")
    
 # Op 10: Método sobrecargado (sin IVA y con urgencia)
cotizacion = s3.calcular_costo(duracion=4, iva=0.0, urgencia=50000)
print(f"Cotización especial Asesoría: ${cotizacion:,.0f}")
log("INFO", f"Cotización especial: ${cotizacion:,.0f}")
print("=== FIN DE SIMULACIÓN (Revisa registro_errores.log) ===")
       
                
    
  