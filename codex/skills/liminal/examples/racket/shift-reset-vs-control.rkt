#lang racket

;; Reduction-oriented witness scaffold for static versus dynamic delimited control.
;; This file intentionally models the two reduction rules as data so the delimiter
;; reinstatement difference is visible even if the host Racket installation has a
;; different concrete operator surface loaded.
;;
;; Source anchors for the real semantics: [DC-AC-1990], [DC-DYN-2005], [RKT-REF].

(define (E x) `(E ,x))

(define (shift-resumed x)
  `(reset ,(E x)))

(define (control-resumed x)
  (E x))

(module+ main
  (displayln "Captured continuation under shift/reset:")
  (displayln '(lambda (x) (reset (E x))))
  (displayln "Resume with v:")
  (displayln (shift-resumed 'v))
  (newline)
  (displayln "Captured continuation under control/prompt:")
  (displayln '(lambda (x) (E x)))
  (displayln "Resume with v:")
  (displayln (control-resumed 'v))
  (newline)
  (displayln "Observable distinction: the first resumed continuation carries a reset boundary; the second does not."))
