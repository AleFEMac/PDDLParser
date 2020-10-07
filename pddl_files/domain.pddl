(define (domain gripper-strips) ;domain definition

	;predicates
	(:predicates (type_room ?r) (type_ball ?b) (type_gripper ?g) (at-robby ?r)(at ?b ?r) (free ?g) (carry ?o ?g))
	
	;actions
	(:action move
		:parameters (?from ?to) 
		:precondition (and (type_room ?from) (type_room ?to) (at-robby ?from))
		:effect (and (at-robby ?to) (not (at-robby ?from)))
	)
	(:action pick
		:parameters (?obj ?room ?gripper)
		:precondition (and (type_ball ?obj) (type_room ?room) (not (carry ?obj ?gripper)) (type_gripper ?gripper) (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper)))
	)
	(:action drop
		:parameters (?obj ?room ?gripper)
		:precondition (and (type_ball ?obj) (type_room ?room) (type_gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))
		:effect (and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))
	)
)