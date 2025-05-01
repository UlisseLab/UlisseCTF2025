package main

import (
	"fmt"
	"io"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"

	"math/rand/v2"

	"github.com/gin-gonic/gin"
	"golang.org/x/time/rate"
)

var (
	ipTracker = make(map[string]int)
	mu        sync.Mutex
)

func trackConnections(c *gin.Context, index int) {
	clientIP := c.ClientIP()

	mu.Lock()
	ipTracker[clientIP] = index
	mu.Unlock()
}

var limiter = rate.NewLimiter(1, 2)

func rateLimiter(c *gin.Context) {
	if limiter.Allow() {
		c.Next()
	} else {
		c.String(http.StatusTooManyRequests, "Too many requests: Max 1 per second")
		c.Abort()
	}
}

func main() {
	r := gin.Default()

	stream := r.Group("/api", rateLimiter)
	stream.GET("/stream", func(c *gin.Context) {
		indexHeader := c.GetHeader("Index")
		clientIP := c.ClientIP()
		var index int
		if indexHeader != "" {
			var err error
			index, err = strconv.Atoi(strings.Split(indexHeader, " ")[0])
			if err != nil || index < 0 || index > 59 {
				c.String(http.StatusBadRequest, "Invalid index header")
				return
			}
		} else {
			mu.Lock()
			lastIndex, exists := ipTracker[clientIP]
			mu.Unlock()
			if exists {
				for {
					index = rand.IntN(60)
					if math.Abs(float64(index-lastIndex)) > 20 {
						break
					}
				}
				trackConnections(c, index)
			} else {
				index = rand.IntN(60)
				trackConnections(c, index)
			}
		}
		filename := fmt.Sprintf("image%d.png", index)
		file, err := os.Open(fmt.Sprintf("assets/%s", filename))
		if err != nil {
			c.String(http.StatusInternalServerError, "Failed to open image")
			return
		}
		defer file.Close()

		c.Header("Content-Type", "image/jpeg")
		c.Header("Cache-Control", "no-cache")
		c.Header("Content-Disposition", fmt.Sprintf("inline; filename=\"%s\"", filename))
		c.Header("Index", fmt.Sprintf("%d of 59", index))
		io.Copy(c.Writer, file)
	})

	r.GET("/", func(c *gin.Context) {
		c.File("./index.html")
	})

	r.Run(":8080")
}
