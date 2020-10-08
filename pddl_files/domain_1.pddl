(define (domain rob-domain) ;domain definition

	;predicates
	(:predicates (type_robot ?r) (type_position ?p) (on ?r) (at ?r ?p) (visited ?p) (alerted ?p))

	;actions
	(:action start
		:parameters (?rob)
		:precondition (and (type_robot ?rob) (not (on ?rob)))
		:effect (on ?rob)
  )

	(:action move
		:parameters (?r ?pos)
		:precondition (and (type_robot ?r) (type_position ?pos) (on ?r) (not (at ?r ?pos)))
		:effect (and (at ?r ?pos) (visited ?pos))
  )

	(:action alert
		:parameters (?rob ?p)
		:precondition (and (type_robot ?rob) (type_position ?p) (on ?rob) (visited ?p) (not (alerted ?p)))
		:effect (alerted ?p)
	)
)
