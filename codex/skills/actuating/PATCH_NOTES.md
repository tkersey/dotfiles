# `$actuating` 4.0 Patch Notes

Adds an EPG closed-loop outer controller while preserving current fail-closed frontier control.

```text
EPG/EPS -> EPD -> `$st`/GCR -> ASL/FPS -> FPSR/ETR -> next EPS
```

No new mutation protocol was added: policy actions reuse ASL-v1 and FPS-v1/FPSR-v1.

Legacy material-plan actuation remains supported.
