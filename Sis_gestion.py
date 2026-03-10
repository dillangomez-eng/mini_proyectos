class sistema_gestion:
  def __init__(self):
    self.inventario = {}  
    
  def agregar_producto(self):
    while True:
      nombre_producto = input("nombre_producto (o 'salir'): ")
      if nombre_producto.lower() == "salir":
        break
      if nombre_producto in self.inventario:
        sumar = int(input("cantidad: "))
        if sumar < 0:
          print("La cantidad no puede ser negativa")
          continue
        cantidad = self.inventario[nombre_producto][1] + sumar
        precio = self.inventario[nombre_producto][0]
        self.inventario[nombre_producto] = (precio, cantidad)
      else:
        precio = int(input("precio: "))
        if precio < 0:
          print("El precio no puede ser negativo")
          continue
        cantidad = int(input("cantidad: "))
        if cantidad < 0:
          print("La cantidad no puede ser negativa")
          continue
        self.inventario[nombre_producto] = (precio, cantidad)
      
   
  def vender_producto(self):
    while True:
      nombre_producto = input("nombre_producto (o 'salir'): ")
      if nombre_producto.lower() == "salir":
          break
      if nombre_producto in self.inventario:
        restar = int(input("cantidad: "))
        if restar < 0:
          print("La cantidad no puede ser negativa")
          continue
        cantidad = self.inventario[nombre_producto][1] - restar
        if cantidad < 0:
          print("No hay suficiente cantidad en el inventario")
          continue
        self.inventario[nombre_producto] = (self.inventario[nombre_producto][0], cantidad)
      else:
        print("Producto no encontrado")
  def mostrar_inventario(self):
    total = 0
    for nombre_producto, valor in self.inventario.items():
          subtotal = valor[0] * valor[1]
          total += subtotal
          print(f"{nombre_producto}:  Precio=${valor[0]}, Cantidad={valor[1]}, Subtotal=${subtotal}")
    
    print(f"\nValor total del inventario: ${total}")
    return total
  
sistema = sistema_gestion()

while True:
  print("1. Agregar producto")
  print("2. Vender producto")
  print("3. Mostrar inventario")
  print("4. Salir")
  opcion = input("Seleccione una opción: ")
  
  if opcion == "1":
    sistema.agregar_producto()
  elif opcion == "2":
    sistema.vender_producto()
  elif opcion == "3":
     sistema.mostrar_inventario()
  elif opcion == "4":
    break
  else:
    print("Opción no válida")