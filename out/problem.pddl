(define (problem strips-gripper2)

	(:domain gripper-strips)

	(:objects rooma roomb ball1 ball2 left right)

	(:init (type_room rooma)    (type_room roomb)   (type_ball ball1)   (type_ball ball2)   (type_gripper left)   (type_gripper right)   (at-robby rooma)   (free left)   (free right)   (at ball1 rooma)   (at ball2 rooma))

	(:goal ( at ball1 roomb))
)