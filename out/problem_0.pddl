(define (problem cake-time-problem)

	(:domain cake-money)

	(:objects cake1)

	(:init (= (total-cost) 0) (type_food cake1) (ingredients cake1))

	(:goal (frosted-cake cake1))

	(:metric minimize (total-cost))
)