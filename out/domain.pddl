(define (domain gripper-strips)

	(:predicates (room ?r) (ball ?b) (gripper ?g) (at-robby ?r) (at ?b ?r) (free ?g) (carry ?o ?g) (light))

	(:action move
		:parameters ( ?from ?to )
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and (at-robby ?to) (not (at-robby ?from)) (increase (total-cost) 6)))
	
	(:action pick
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room))   (not (free ?gripper))(increase (total-cost) 2)))
	
	(:action drop
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (carry ?obj ?gripper) (at-robby ?room))
		:effect (and (at ?obj ?room) (free ?gripper)   (not (carry ?obj ?gripper))(increase (total-cost) 1)))
	
	(:action move_pick
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and ((and (at-robby ?to ) (not (at-robby ?from )) ) ) ( (and (carry ?obj ?gripper ) (not (at ?obj ?room )) (not (free ?gripper )) ) )(increase (total-cost) 8) ))
	
	(:action move_pick_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and ((and (at-robby ?to ) (not (at-robby ?from )) ) ) ( (and (carry ?obj ?gripper ) (not (at ?obj ?room )) (not (free ?gripper )) ) )(increase (total-cost) 8) ))
	
	(:action move_drop
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and ((and (at-robby ?to ) (not (at-robby ?from )) ) ) ( (and (at ?obj ?room ) (free ?gripper ) (not (carry ?obj ?gripper )) ) )(increase (total-cost) 7) ))
	
	(:action move_drop_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and ((and (at-robby ?to ) (not (at-robby ?from )) ) ) ( (and (at ?obj ?room ) (free ?gripper ) (not (carry ?obj ?gripper )) ) )(increase (total-cost) 7) ))
	
	(:action pick_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and ((and (carry ?obj ?gripper ) (not (at ?obj ?room )) (not (free ?gripper )) ) ) ( (and (at-robby ?to ) (not (at-robby ?from )) ) )(increase (total-cost) 8) ))
	
	(:action pick_move_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and ((and (carry ?obj ?gripper ) (not (at ?obj ?room )) (not (free ?gripper )) ) ) ( (and (at-robby ?to ) (not (at-robby ?from )) ) )(increase (total-cost) 8) ))
	
	(:action pick_drop
		:parameters ( ?par_0 ?par_1 ?par_2 )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and ((and (carry ?obj ?gripper ) (not (at ?obj ?room )) (not (free ?gripper )) ) ) ( (and (at ?obj ?room ) (free ?gripper ) (not (carry ?obj ?gripper )) ) )(increase (total-cost) 3) ))
	
	(:action drop_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (carry ?obj ?gripper) (at-robby ?room))
		:effect (and ((and (at ?obj ?room ) (free ?gripper ) (not (carry ?obj ?gripper )) ) ) ( (and (at-robby ?to ) (not (at-robby ?from )) ) )(increase (total-cost) 7) ))
	
	(:action drop_move_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (carry ?obj ?gripper) (at-robby ?room))
		:effect (and ((and (at ?obj ?room ) (free ?gripper ) (not (carry ?obj ?gripper )) ) ) ( (and (at-robby ?to ) (not (at-robby ?from )) ) )(increase (total-cost) 7) ))
	
	(:action drop_pick
		:parameters ( ?par_0 ?par_1 ?par_2 )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (carry ?obj ?gripper) (at-robby ?room))
		:effect (and ((and (at ?obj ?room ) (free ?gripper ) (not (carry ?obj ?gripper )) ) ) ( (and (carry ?obj ?gripper ) (not (at ?obj ?room )) (not (free ?gripper )) ) )(increase (total-cost) 3) ))
)