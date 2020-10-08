(define (domain rob-domain)

	(:predicates (type_robot ?r) (type_position ?p) (on ?r) (at ?r ?p) (visited ?p) (alerted ?p))

	(:action start
		:parameters ( ?rob )
		:precondition (and (type_robot ?rob) (not (on ?rob)))
		:effect (on ?rob)
	)
	
	(:action move
		:parameters ( ?r ?pos )
		:precondition (and (type_robot ?r) (type_position ?pos) (on ?r) (not (at ?r ?pos)))
		:effect (and (at ?r ?pos) (visited ?pos))
	)
	
	(:action alert
		:parameters ( ?rob ?p )
		:precondition (and (type_robot ?rob) (type_position ?p) (on ?rob) (visited ?p) (not (alerted ?p)))
		:effect (alerted ?p)
	)
	
	(:action start_move
		:parameters ( ?par_0 ?par_1 )
		:precondition (and (type_robot ?par_0) (not (on ?par_0)) (type_position ?par_1) (not (at ?par_0 ?par_1)))
		:effect (and (on ?par_0) (at ?par_0 ?par_1) (visited ?par_1))
	)
	
	(:action move_alert
		:parameters ( ?par_0 ?par_1 )
		:precondition (and (type_robot ?par_0) (type_position ?par_1) (on ?par_0) (not (at ?par_0 ?par_1)) (not (alerted ?par_1)))
		:effect (and (at ?par_0 ?par_1) (visited ?par_1) (alerted ?par_1))
	)
	
	(:action alert_move
		:parameters ( ?par_0 ?par_1 )
		:precondition (and (type_robot ?par_0) (type_position ?par_1) (on ?par_0) (visited ?par_1) (not (alerted ?par_1)) (not (at ?par_0 ?par_1)))
		:effect (and (alerted ?par_1) (at ?par_0 ?par_1) (visited ?par_1))
	)
)