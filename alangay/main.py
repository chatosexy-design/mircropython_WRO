#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Color, Direction
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# ==========================================
# CONFIGURACIÓN DEL ROBOT 
# ==========================================

ev3 = EV3Brick()

# Motores de tracción (Configuración estándar WRO: Ruedas grandes)
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

# Mecanismos:
# Port A: Garra de alta precisión (para 2 bloques a la vez)
# Port D: Reja trasera/delantera para alineación final
claw_motor = Motor(Port.A)
fence_motor = Motor(Port.D)

# Sensor de color (S1) apuntando al suelo para el patrón y líneas
color_sensor = ColorSensor(Port.S1)

# DriveBase: Ajustar diámetro según llanta (aprox 56mm para EV3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)
robot.settings(straight_speed=150, straight_acceleration=80, turn_rate=90)

# Datos de la misión
pattern_grid = []  # Aquí guardaremos los colores escaneados (3x4 o similar)
TOTAL_BLOCKS = 14  
BLOCKS_PER_LOAD = 2

def setup():
    """Preparación inicial de motores y sensores."""
    ev3.speaker.beep()
    # Resetear motores de mecanismos
    claw_motor.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40) # Abrir
    fence_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=40) # Subir reja

def navigate_to_zone(zone_name):
    """Simulación de navegación autónoma entre zonas del mat."""
    print("Navegando a:", zone_name)
    if zone_name == "pattern":
        robot.straight(200) # Distancia a la cuadrícula de colores
    elif zone_name == "loading":
        robot.straight(-100)
        robot.turn(90)
        robot.straight(300)
    elif zone_name == "delivery":
        robot.straight(-300)
        robot.turn(-90)
        robot.straight(150)

def scan_pattern_grid():
    """
    Paso 1: Pasa por arriba de la cuadrícula de colores para escanear el patrón.
    Basado en las imágenes, el robot escanea una cuadrícula (ej. 3x4).
    """
    ev3.speaker.say("Escaneando cuadricula")
    navigate_to_zone("pattern")
    
    # Escaneo de 3 filas con 4 colores cada una (Ejemplo)
    for row in range(3):
        row_colors = []
        for col in range(4):
            # Leer color actual
            current_color = color_sensor.color()
            if current_color in [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]:
                row_colors.append(current_color)
                ev3.light.on(current_color)
            else:
                row_colors.append(Color.WHITE) # Color vacío o base
            
            # Avanzar al siguiente cuadrado del patrón
            robot.straight(45) 
            wait(200)
        
        pattern_grid.append(row_colors)
        
        # Maniobra para cambiar de fila (si fuera necesario)
        if row < 2:
            robot.straight(-180) # Regresar
            # Aquí iría un giro lateral para la siguiente columna de la cuadrícula
            # robot.turn(...)
            
    print("Patrón escaneado con éxito:", pattern_grid)
    ev3.speaker.say("Patron guardado")

def pickup_blocks_2x2():
    """
    Paso 2: Recoge los bloques pre-ordenados de 2 en 2.
    """
    navigate_to_zone("loading")
    print("Recogiendo par de bloques...")
    
    # Abrir garra
    claw_motor.run_target(500, -100)
    
    # Acercarse para que los bloques entren en la garra
    robot.straight(50)
    
    # Cerrar garra con fuerza para asegurar los 2 bloques
    claw_motor.run_until_stalled(500, then=Stop.HOLD, duty_limit=100)
    
    # Levantar un poco si tuviera elevación o simplemente retroceder
    robot.straight(-50)

def deliver_by_pattern(block_index):
    """
    Paso 3: Deja los bloques en el slot que coincida con el patrón guardado.
    """
    navigate_to_zone("delivery")
    
    # Determinar color objetivo basado en el índice de entrega
    # Aplanamos el grid para seguir un orden
    flat_pattern = [color for row in pattern_grid for color in row]
    target_color = flat_pattern[block_index % len(flat_pattern)]
    
    print("Buscando slot de color:", target_color)
    
    # Aquí el robot se movería al slot físico del color 'target_color'
    # robot.straight(...)
    
    # Soltar bloques
    claw_motor.run_target(500, -100)
    robot.straight(-40)
    claw_motor.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40)

def finalize_alignment():
    """
    Paso 4: Baja la reja para empujar y acomodar todos los bloques.
    """
    ev3.speaker.say("Alineando bloques finales")
    
    # Posicionarse frente a todos los bloques entregados
    robot.straight(80)
    
    # Bajar la reja (Motor D)
    # Suponemos que 0 es arriba y -180 es abajo
    fence_motor.run_target(400, -180)
    
    # Pequeño empuje para cuadrar los bloques contra la pared/base
    robot.straight(40)
    wait(500)
    robot.straight(-50)
    
    # Subir reja y terminar
    fence_motor.run_target(400, 0)
    ev3.speaker.say("Mision cumplida")

def main():
    setup()
    
    # 1. Escanear el patrón pasando por arriba
    scan_pattern_grid()
    
    # 2. Bucle de trabajo para 12-16 bloques (agarrando de 2 en 2)
    delivered = 0
    while delivered < TOTAL_BLOCKS:
        pickup_blocks_2x2()
        deliver_by_pattern(delivered // 2)
        delivered += BLOCKS_PER_LOAD
        print("Bloques entregados:", delivered)
        
    # 3. Alineación final con la reja
    finalize_alignment()

if __name__ == "__main__":
    main()
