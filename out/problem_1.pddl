(define (problem rob-problem)

	(:domain rob-domain)

	(:objects rob0 pos1 pos2 pos3)

	(:init (type_robot rob0)   (type_position pos1)   (type_position pos2)   (type_position pos3)   (not (on rob0))   (not (at rob0 pos1))   (not (at rob0 pos2))   (not (at rob0 pos3)))

	(:goal (and (alerted pos1) (alerted pos2) (alerted pos3)))
)