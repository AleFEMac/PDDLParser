(define (domain gripper-strips) ;initial definition
	(:predicates (room ?r) (ball ?b) (gripper ?g) (at-robby ?r)
	(at ?b ?r) (free ?g) (carry ?o ?g) (light)) ; comment2
	
;actions will be defined from this point onwards
	(:action move
		:parameters (?from ?to)
		:precondition (and (room ?from) (room ?to) (at-robby ?from)) ;a
		:effect (and (at-robby ?to) (not (at-robby ?from)) (increase (total-cost) 6))
	)
	(:action pick
		:parameters (?obj ?room ?gripper)
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)
			(at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room))
		(not (free ?gripper))(increase (total-cost) 2))
	)
	(:action drop
		:parameters (?obj ?room ?gripper)
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)
			(carry ?obj ?gripper) (at-robby ?room))
		:effect (and (at ?obj ?room) (free ?gripper)
		(not (carry ?obj ?gripper))(increase (total-cost) 1))
	)
)