#lang racket

;; Prompt-tag separation sketch.
;; This is a runnable data model, not a replacement for Racket's real prompt API.
;; It shows the invariant a real multi-prompt implementation must preserve:
;; capture targeting tag q must not accidentally cross tag p.
;;
;; Source anchors for real APIs: [RKT-REF], [DC-MFDC-2007].

(struct prompt (tag body) #:transparent)
(struct capture (tag name body) #:transparent)

(define program
  (prompt 'p
          (list 'A
                (prompt 'q
                        (list 'B
                              (capture 'q 'k '(resume k value))))
                'C)))

(module+ main
  (displayln program)
  (displayln "Invariant: a capture for tag q is bounded by prompt q, not by the outer prompt p."))
