# TableTopGameEvaluator
El paquete Game brinda una arquitectura para modelas y evaluar distintas métricas de juegos.

## Definicion de juego
Vemos un juego como una secuencia de acciones que tiene consecuencias sobre el estado de los elementos que conforman el juego.
Estas acciones van ocurriendo segun las reglas que indique el juego hasta que se llega a un estado de los elementos en el que se considera que el juego ha terminado, a este estado lo llamaremos `estado final`.
Nuestra forma para definir las reglas que indican como se ejecutan las acciones es mediante un grafo, donde cada vertice contiene una serie de acciones que se ejecutan secuencialmente. Entonces una partida consiste en comenzar con un `estado inicial` e ir moviendonos por el grafo hasta encontrarnos en un estado final. A continuacion iremos por los distintos modulos del paquete explicando las clases y funciones que brindamos para definir y evaluar los juegos.

## State
- TableState(State):
    Para modelar el estado de los elementos que conforman el juego crearemos una clase que herede de esta clase, con ella debemos abarcar todos los elementos del juego que son comunes para todos los jugadores, aqui podemos tener datos como las posiciones de las fichas en el tablero, el jugador de turno actual o cualquier otro dato que sea relevante para el juego

- PlayerState(State):
    Es equivalente a TableState con la diferencia de que en nuestra clase heredera de PlayerState tendremos elementos que pertenecen a un jugador como pueden ser por ejemplo las cartas que tiene en la mano, sus puntos, etc.

- create_game_state:
    Esta fucion recibira una instancia de nuetra clase heredera de TableState y una lista de instancias de nuestra clase heredera de PlayerState, una por cada jugador, y nos devolvera una tupla conformada por estos dos elementos que sera el estado del juego.

## Player
- Player:
    Heredaremos de esta clase para crear los agentes que formaran parte de las simulaciones de nuestros juegos. Debemos implementar la funcion get_play que se encargara dado el estado actual del juego y el nodo del grafo en que nos encontramos devolver la descripcion de la jugada seleccionada por el agente.
    
## Metrics
- calculate_metric:
    A esta funcion le pasaremos como argumentos la definicion de un juego, una funcion `f1` que devuelva un estado inicial para el juego, una funcion `f2` que devuelva jugadores para jugar el juego, un numero `N` y una funcion `f3` que evalue la metrica que queremos dados los resultados de las simulaciones. La funcion simulara `N` partidas del juego empezando en los estados generados por `f1` y jugadas por los jugadores generados por `f2`; de cada simulacion se obtendra la historia de estados por la cual transcurrio la partida y los jugadres que la jugaron (permitimos obtener datos de los jugadores participantes porque en ellos pueden quedar estadisticas o valores obtenidos durante la realizacion de la estrategia que llevaron a cabo durante el juego), luego todos estos datos son pasados como argumento a la funcion `f3` y se devolvera el resultado que es la evaluacion de la metrica.

## Game
- GameNode:
    Es la clase que usamos para definir un nodo o vertice del grafo que describe nuestro juego, entre sus propiedades se encuentran:
    - name: El identificador del nodo.
    - default: El identificador del nodo al cual dirigirse al terminar las acciones si no hay ninguna arista que cumpla la condicion para recorrerla, en el caso de que este no se especifique se pone por defecto un nodo que llamamos sumidero, existe para descubrir posibles `huecos` en la logica del juego.
    - actions: La lista de acciones que conforman el nodo.

- Game:
    Esta clase representa una instancia del juego y podemos iterar sobre ella para ir observando los distintos estados por los que atraviesa el juego, al terminar el juego el iterador se dentendra.

- GameDescriptor:
    Es la clase que utilizamos para describir un juego