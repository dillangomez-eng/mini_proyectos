class CuentaBancaria:
    def __init__(self, numero_cuenta, titular, saldo):
        self.numero_cuenta = numero_cuenta
        self.titular = titular
        self.saldo = saldo  
        
    def depositar(self, monto):
        if monto <= 0:
            print("El monto a depositar debe ser mayor que cero.")
        else:
            self.saldo += monto
            print(f"Depósito de {monto} realizado. Nuevo saldo: {self.saldo}")
        
    def retirar(self, monto):
        if monto > self.saldo:
            print("Fondos insuficientes para retirar.")  
        elif monto <= 0:
            print("El monto a retirar debe ser mayor que cero.")    
        else:
            self.saldo -= monto
            print(f"Retiro de {monto} realizado. Nuevo saldo: {self.saldo}")
            
    def transferir(self, monto, cuenta_destino):
        if monto > self.saldo:
            print("Fondos insuficientes para transferir.")  
        elif monto <= 0:
            print("El monto a transferir debe ser mayor que cero.")    
        else:
            self.saldo -= monto
            cuenta_destino.saldo += monto
            print(f"Transferencia de {monto} realizada a la cuenta {cuenta_destino.numero_cuenta}. Nuevo saldo: {self.saldo}")
    
    def mostrar_informacion(self):
        print(f"Cuenta: {self.numero_cuenta} | Titular: {self.titular} | Saldo: ${self.saldo}")
    
class Banco:
    def __init__(self):
        self.cuentas = {}
    
    def crear_cuenta(self, numero_cuenta, titular, saldo_inicial=0):
        if saldo_inicial < 0:
            print("Error: El saldo inicial no puede ser negativo")
            return False
        
        if numero_cuenta in self.cuentas:
            print(f"Error: La cuenta {numero_cuenta} ya existe")
            return False
        
        self.cuentas[numero_cuenta] = CuentaBancaria(numero_cuenta, titular, saldo_inicial)
        print(f"Cuenta {numero_cuenta} creada correctamente")
        return True
    
    def obtener_cuenta(self, numero_cuenta):
        if numero_cuenta not in self.cuentas:
            print(f"Error: La cuenta {numero_cuenta} no existe")
            return None
        return self.cuentas[numero_cuenta]
    
    def mostrar_cuentas(self):
        if not self.cuentas:
            print("No hay cuentas registradas")
            return
    
        for numero, cuenta in self.cuentas.items():
            print(f"Cuenta: {numero} | Titular: {cuenta.titular} | Saldo: ${cuenta.saldo}")
            
class Menu:
    def __init__(self, banco):
        self.banco = banco
    
    def mostrar_menu(self):
        while True:
            print("\n--- Menú del Banco ---")
            print("1. Crear cuenta")
            print("2. Depositar")
            print("3. Retirar")
            print("4. Transferir")
            print("5. Mostrar cuentas")
            print("6. Salir")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                numero_cuenta = input("Número de cuenta: ")
                titular = input("Titular: ")
                saldo_inicial = float(input("Saldo inicial: "))
                self.banco.crear_cuenta(numero_cuenta, titular, saldo_inicial)
                
            elif opcion == "2":
                numero_cuenta = input("Número de cuenta: ")
                monto = float(input("Monto a depositar: "))
                cuenta = self.banco.obtener_cuenta(numero_cuenta)
                if cuenta:
                    cuenta.depositar(monto)
                    
            elif opcion == "3":
                numero_cuenta = input("Número de cuenta: ")
                monto = float(input("Monto a retirar: "))
                cuenta = self.banco.obtener_cuenta(numero_cuenta)
                if cuenta:
                    cuenta.retirar(monto)
                    
            elif opcion == "4":
                numero_origen = input("Número de cuenta origen: ")
                numero_destino = input("Número de cuenta destino: ")
                monto = float(input("Monto a transferir: "))
                
                cuenta_origen = self.banco.obtener_cuenta(numero_origen)
                cuenta_destino = self.banco.obtener_cuenta(numero_destino)
                
                if cuenta_origen and cuenta_destino:
                    cuenta_origen.transferir(monto, cuenta_destino)
                    
            elif opcion == "5":
                self.banco.mostrar_cuentas()
                
            elif opcion == "6":
                print("Saliendo del programa...")
                break
            else:
                print("Opción no válida. Por favor, intente nuevamente.")
                
if __name__ == "__main__":
    banco = Banco()
    menu_banco = Menu(banco)
    menu_banco.mostrar_menu()