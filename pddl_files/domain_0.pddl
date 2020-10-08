(define
	(domain cake-money) ;domain name

	(:predicates (type_food ?c) (ingredients ?c) (no-cake ?c) (cake ?c) (baked-cake ?c) (frosted-cake ?c))

; actions
	(:action buy-cake
    :parameters (?c)
		:precondition (and (type_food ?c) (not (cake ?c)) (ingredients ?c))
		:effect (and (cake ?c) (not (ingredients ?c)) (increase (total-cost) 25))
	)

	(:action bake-cake
    :parameters (?c)
		:precondition (and (type_food ?c) (cake ?c) (not (baked-cake ?c)))
		:effect (and (baked-cake ?c) (not (cake ?c)) (increase (total-cost) 10))
	)

	(:action frost-cake
    :parameters (?c)
		:precondition (and (type_food ?c) (baked-cake ?c) (not (frosted-cake ?c)))
		:effect (and (frosted-cake ?c) (not (baked-cake ?c)) (increase (total-cost) 12))
	)
)
