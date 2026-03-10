class libro:
    def __init__(self, titulo, autor, isbn, disponible=True):
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.disponible = disponible

    def marcar_como_prestado(self):
        if self.disponible:
            self.disponible = False
            print(f"El libro '{self.titulo}' ha sido marcado como prestado.")
        else:
            print(f"El libro '{self.titulo}' ya está prestado.")
            
    def marcar_como_disponible(self):
        if not self.disponible:
            self.disponible = True
            print(f"El libro '{self.titulo}' ha sido marcado como disponible.")
        else:
            print(f"El libro '{self.titulo}' ya está disponible.")
            
    def mostrar_informacion(self):
        estado = "Disponible" if self.disponible else "Prestado"
        print(f"Título: {self.titulo} | Autor: {self.autor} | ISBN: {self.isbn} | Estado: {estado}")
        
class usuario:
    def __init__(self, nombre, id_usuario):
        self.nombre = nombre
        self.id_usuario = id_usuario
        self.libros_prestados = []
        
    def prestar_libro(self, libro):
        if len(self.libros_prestados) >= 3:
            print(f"{self.nombre} no puede prestar más de 3 libros.")
            return
        if libro.disponible:
            libro.marcar_como_prestado()
            self.libros_prestados.append(libro)
            print(f"{self.nombre} ha prestado el libro '{libro.titulo}'.")
        else:
            print(f"El libro '{libro.titulo}' no está disponible para préstamo.")
            
    def devolver_libro(self, libro):
        if libro in self.libros_prestados:
            libro.marcar_como_disponible()
            self.libros_prestados.remove(libro)
            print(f"{self.nombre} ha devuelto el libro '{libro.titulo}'.")
        else:
            print(f"{self.nombre} no tiene el libro '{libro.titulo}' prestado.")
            
    def mostrar_informacion(self):
        print(f"Usuario: {self.nombre} | ID: {self.id_usuario} | Libros prestados: {[libro.titulo for libro in self.libros_prestados]}")
        
class biblioteca:
    def __init__(self):
        self.libros = []
        self.usuarios = []
        self.prestamos = {}  # Diccionario para rastrear libro: usuario
        self.historial = []  # Lista para historial de préstamos y devoluciones
        
    def agregar_libro(self, libro):
        self.libros.append(libro)
        print(f"El libro '{libro.titulo}' ha sido agregado a la biblioteca.")
        
    def registrar_usuario(self, usuario):
        self.usuarios.append(usuario)
        print(f"El usuario '{usuario.nombre}' ha sido registrado en la biblioteca.")
        
    def prestar_libro(self, usuario, libro):
        if libro.disponible and usuario in self.usuarios and libro in self.libros:
            usuario.prestar_libro(libro)
            self.prestamos[libro] = usuario
            self.historial.append(f"{usuario.nombre} prestó '{libro.titulo}'")
        else:
            print("No se puede prestar el libro (no disponible, usuario no registrado o libro no en biblioteca).")
            
    def devolver_libro(self, usuario, libro):
        if libro in self.prestamos and self.prestamos[libro] == usuario:
            usuario.devolver_libro(libro)
            del self.prestamos[libro]
            self.historial.append(f"{usuario.nombre} devolvió '{libro.titulo}'")
        else:
            print("No se puede devolver el libro (no prestado por este usuario).")
            
    def mostrar_libros_disponibles(self):
        print("Libros disponibles en la biblioteca:")
        for libro in self.libros:
            if libro.disponible:
                libro.mostrar_informacion()
                
    def mostrar_usuarios_registrados(self):
        print("Usuarios registrados en la biblioteca:")
        for usuario in self.usuarios:
            usuario.mostrar_informacion()
            
    def mostrar_prestamos_actuales(self):
        print("Préstamos actuales:")
        for libro, usuario in self.prestamos.items():
            print(f"Libro '{libro.titulo}' prestado a {usuario.nombre}")
            
    def mostrar_historial(self):
        print("Historial de préstamos y devoluciones:")
        for evento in self.historial:
            print(evento)
            
            
class menu:
    def __init__(self, biblioteca):
        self.biblioteca = biblioteca
        
    def mostrar_menu(self):
        print("\n--- Menú de la Biblioteca ---")
        print("1. Agregar libro")
        print("2. Registrar usuario")
        print("3. Prestar libro")
        print("4. Devolver libro")
        print("5. Mostrar libros disponibles")
        print("6. Mostrar usuarios registrados")
        print("7. Mostrar préstamos actuales")
        print("8. Mostrar historial de préstamos y devoluciones")
        print("9. Salir")
        
        
    def ejecutar_opcion(self, opcion):
        if opcion == "1":
            titulo = input("Ingrese el título del libro: ")
            autor = input("Ingrese el autor del libro: ")
            isbn = input("Ingrese el ISBN del libro: ")
            nuevo_libro = libro(titulo, autor, isbn)
            self.biblioteca.agregar_libro(nuevo_libro)
        elif opcion == "2":
            nombre = input("Ingrese el nombre del usuario: ")
            id_usuario = input("Ingrese el ID del usuario: ")
            nuevo_usuario = usuario(nombre, id_usuario)
            self.biblioteca.registrar_usuario(nuevo_usuario)
        elif opcion == "3":
            nombre_usuario = input("Ingrese el nombre del usuario que desea prestar un libro: ")
            titulo_libro = input("Ingrese el título del libro que desea prestar: ")
            usuario_obj = next((u for u in self.biblioteca.usuarios if u.nombre == nombre_usuario), None)
            libro_obj = next((l for l in self.biblioteca.libros if l.titulo == titulo_libro), None)
            if usuario_obj and libro_obj:
                self.biblioteca.prestar_libro(usuario_obj, libro_obj)
            else:
                print("Usuario o libro no encontrado.")
        elif opcion == "4":
            nombre_usuario = input("Ingrese el nombre del usuario que desea devolver un libro: ")
            titulo_libro = input("Ingrese el título del libro que desea devolver: ")
            usuario_obj = next((u for u in self.biblioteca.usuarios if u.nombre == nombre_usuario), None)
            libro_obj = next((l for l in self.biblioteca.libros if l.titulo == titulo_libro), None)
            if usuario_obj and libro_obj:
                self.biblioteca.devolver_libro(usuario_obj, libro_obj)
            else:
                print("Usuario o libro no encontrado.")
        elif opcion == "5":
            self.biblioteca.mostrar_libros_disponibles()
        elif opcion == "6":
            self.biblioteca.mostrar_usuarios_registrados()
        elif opcion == "7":
            self.biblioteca.mostrar_prestamos_actuales()
        elif opcion == "8":
            self.biblioteca.mostrar_historial()
        elif opcion == "9":
            print("Saliendo del programa...")
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
            
if __name__ == "__main__":
    biblioteca = biblioteca()
    menu = menu(biblioteca)
    
    while True:
        menu.mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == "9":
            break
        menu.ejecutar_opcion(opcion)