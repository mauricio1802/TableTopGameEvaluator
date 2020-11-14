# TableTopGameEvaluator
El paquete Game brinda una arquitectura para modelar y evaluar distintas métricas de juegos.

## Definición de juego
Vemos un juego como una secuencia de acciones que tienen consecuencias sobre el estado de los elementos que conforman el juego.
Estas acciones van ocurriendo segun las reglas que indique el juego hasta que se llega a un estado de los elementos en el que se considera que el juego ha terminado, a este estado lo llamaremos `estado final`.
Para definir las reglas que indican como se ejecutan las acciones usamos un grafo, donde cada vértice contiene una serie de acciones que se ejecutan secuencialmente. Una partida consiste en comenzar con un `estado inicial` e ir moviéndonos por el grafo hasta encontrarnos en un estado final. A continuación iremos por los distintos módulos del paquete explicando las clases y funciones que brindamos para definir y evaluar los juegos.

## State
- TableState(State):
    Para modelar el estado de los elementos que conforman el juego crearemos una clase que herede de esta clase, con ella debemos abarcar todos los elementos del juego que son comunes para todos los jugadores, aqui podemos tener datos como las posiciones de las fichas en el tablero, el jugador de turno actual o cualquier otro dato que sea relevante para el juego.

- PlayerState(State):
    Es equivalente a TableState con la diferencia de que en nuestra clase heredera de PlayerState tendremos elementos que pertenecen a un jugador específico como pueden ser por ejemplo las cartas que tiene en la mano, sus puntos, etc.

- create_game_state:
    Esta fución recibirá una instancia de nuestra clase heredera de TableState y una lista de instancias de nuestra clase heredera de PlayerState, una por cada jugador, y nos devolverá una tupla conformada por estos dos elementos que sera el estado del juego.

## Player
- Player:
    Heredaremos de esta clase para crear los agentes que formaran parte de las simulaciones de nuestros juegos. Debemos implementar la funcion get_play que se encargará dado el estado actual del juego y el nodo del grafo en que nos encontramos devolver la descripción de la jugada seleccionada por el agente.
    
## Metrics
- calculate_metric:
    A esta funcion le pasaremos como argumentos la definición de un juego, una función `f1` que devuelva un estado inicial para el juego, una función `f2` que devuelva jugadores para jugar el juego, un número `N` y una función `f3` que evalúe la métrica que queremos dados los resultados de las simulaciones. La función simulará `N` partidas del juego empezando en los estados generados por `f1` y jugadas por los jugadores generados por `f2`; de cada simulación se obtendrá la historia de estados por la cual transcurrió la partida y los jugadres que la jugaron (permitimos obtener datos de los agentes participantes porque en ellos pueden quedar estadísticas o valores obtenidos durante la realización de la estrategia que llevaron a cabo durante el juego), luego todos estos datos son pasados como argumento a la función `f3` y se devolverá el resultado que es la evaluación de la métrica.

## Game
- GameNode:
    Es la clase que usamos para definir un nodo o vértice del grafo que describe nuestro juego, entre sus propiedades se encuentran:
    - name: El identificador del nodo.
    - default: El identificador del nodo al cual dirigirse al terminar las acciones si no hay ninguna arista que cumpla la condicion para recorrerla, en el caso de que este no se especifique se pone por defecto un nodo que llamamos sumidero, existe para descubrir posibles `huecos` en la lógica del juego.
    - actions: La lista de acciones que conforman el nodo.

- Game:
    Esta clase representa una instancia del juego y podemos iterar sobre ella para ir observando los distintos estados por los que atraviesa el juego, al terminar el juego el iterador se dentendrá.

- GameDescriptor:
    Es la clase que utilizamos para describir un juego, primero creamos una instancia de la clase y usamos los siguientes métodos:
    - action: Este metodo recibe tres argumentos, el identificador del nodo donde se agregará la acción, si requiere decisiones del jugador y su precedencia en el nodo (esta precedencia es importante para definir el orden en que se ejecutan las acciones que están en un mismo nodo). Con este método decoramos la función que representa la acción, la función que decoremos debe recibir un primer parámetro que es el estado actual del juego, si se indicó que la acción debía recibir decisiones del jugador recibirá un segundo parámetro que representa estas decisiones y retornará el estado resultante de aplicar la acción al estado actual.
    - goto: Este método recibe tres argumentos, los dos primeros son identificadores de nodos, lo que hace es crear una arista dirigida entre estos dos nodos, el tercer parámetro indica si es necesario el conocimiento de la última jugada hecha. Con este método se decora una función que decidirá si se debe continuar por esta arista o no en el flujo del juego. La función decorada recibe un primer parámentro que representa el estado actual del juego y un segundo parámetro opcional en dependencia de si se especificó que era necesario el conocimiento de la ultima decisión de un jugador (el parámetro reflejará dicha decisión); la función devolverá un valor booleano indicando si se debe avanzar por esta arista o no.
    - end: Con este método se decora una función que recibe un estado y devuelve un valor booleano indicando si es un estado final o no.
    - who_plays: Con este método se decora una función que recibe el estado actual y el identificador del nodo del grafo en el que nos encontramos en ese momento, debe devolver un entero que indique cual es el jugador que debe jugar.
    -get_game_instance: Este método nos devuelve una instancia `Game` del juego descrito, debemos pasarle el estado inicial donde comenzará el juego y los agentes que jugarán la partida.
