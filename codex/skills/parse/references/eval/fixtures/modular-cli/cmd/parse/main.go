package main

import (
	"modularcli/modules/config"
	"modularcli/modules/report"
)

func main() {
	_, _ = config.Load(), report.Render()
}
