package functions

import (
	"fmt"
	"os"
	"time"
)

func Hello() {
	fmt.Println("Hello")
}

func GetEnv(s string, vDefault string) string {
	v := os.Getenv(s)
	if v == "" {
		return vDefault
	}
	return v
}

func GetNowUnix() int64 {
	return time.Now().Unix()
}

func SliceUnique(lines []string) (linesUnique []string) {
	unique := make(map[string]string, len(lines))

	for _, line := range lines {
		unique[MD5(line)] = line
	}

	for _, v := range unique {
		if v != "" {
			linesUnique = append(linesUnique, v)
		}
	}
	return linesUnique
}
