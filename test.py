from obstacles import Obstacle, show_obstacles

obstacles = [
    Obstacle(10, 10),  # первое препятствие
    Obstacle(10, 12, uid='второе препятствие с названием'),
    Obstacle(20, 20, 5, 5, uid='третье большое препятствие'),
]

coroutine = show_obstacles(canvas, obstacles)
