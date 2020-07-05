(define (domain gripper-strips)

	(:predicates (type_room ?r) (type_ball ?b) (type_gripper ?g) (at-robby ?r) (at ?b ?r) (free ?g) (carry ?o ?g))

	(:action move
		:parameters ( ?from ?to )
		:precondition (and (type_room ?from) (type_room ?to) (at-robby ?from))
		:effect (and (at-robby ?to) (not (at-robby ?from)))
	)
	
	(:action pick
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (type_ball ?obj) (type_room ?room) (not (carry ?obj ?gripper)) (type_gripper ?gripper) (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper)))
	)
	
	(:action drop
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (type_ball ?obj) (type_room ?room) (type_gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))
		:effect (and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))
	)
	
	(:action move_pick
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (type_room ?par_1) (type_room ?par_0) (at-robby ?par_1) (type_ball ?par_2) (not (carry ?par_2 ?par_3)) (type_gripper ?par_3) (at ?par_2 ?par_0) (free ?par_3))
		:effect (and (at-robby ?par_0) (not (at-robby ?par_1)) (carry ?par_2 ?par_3) (not (at ?par_2 ?par_0)) (not (free ?par_3)))
	)
	
	(:action move_drop
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (type_room ?par_1) (type_room ?par_0) (at-robby ?par_1) (type_ball ?par_2) (type_gripper ?par_3) (carry ?par_2 ?par_3))
		:effect (and (at-robby ?par_0) (not (at-robby ?par_1)) (at ?par_2 ?par_0) (free ?par_3) (not (carry ?par_2 ?par_3)))
	)
	
	(:action pick_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (type_ball ?par_1) (type_room ?par_0) (not (carry ?par_1 ?par_2)) (type_gripper ?par_2) (at ?par_1 ?par_0) (at-robby ?par_0) (free ?par_2) (type_room ?par_3) (at-robby ?par_3))
		:effect (and (carry ?par_1 ?par_2) (not (at ?par_1 ?par_0)) (not (free ?par_2)) (at-robby ?par_0) (not (at-robby ?par_3)))
	)
	
	(:action pick_drop
		:parameters ( ?par_0 ?par_1 ?par_2 )
		:precondition (and (type_ball ?par_0) (type_room ?par_1) (not (carry ?par_0 ?par_2)) (type_gripper ?par_2) (at ?par_0 ?par_1) (at-robby ?par_1) (free ?par_2))
		:effect (and (not (carry ?par_0 ?par_2)) (at ?par_0 ?par_1) (free ?par_2))
	)
	
	(:action drop_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (type_ball ?par_1) (type_room ?par_0) (type_gripper ?par_2) (carry ?par_1 ?par_2) (at-robby ?par_0) (type_room ?par_3) (at-robby ?par_3))
		:effect (and (at ?par_1 ?par_0) (free ?par_2) (not (carry ?par_1 ?par_2)) (at-robby ?par_0) (not (at-robby ?par_3)))
	)
)