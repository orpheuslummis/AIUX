package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"strconv"

	gogpt "github.com/sashabaranov/go-gpt3"
)

// defaults
const (
	max_tokens   = 100
	temperature  = 0.9
	choice_count = 5
)

type Params struct {
	APIKey           string
	ChoiceCount      int
	MaxTokens        int
	Temperature      float64
	TimeLimitSeconds int
	DividerLength    int
}

func NewParamsFromEnv() Params {
	var p Params
	p.APIKey = os.Getenv("OPENAPI_KEY")
	if p.APIKey == "" {
		panic("OPENAPI_KEY is not set")
	}
	p.ChoiceCount, _ = strconv.Atoi(os.Getenv("CHOICE_COUNT"))
	if p.ChoiceCount == 0 {
		p.ChoiceCount = choice_count
	}
	p.MaxTokens, _ = strconv.Atoi(os.Getenv("MAX_TOKENS"))
	if p.MaxTokens == 0 {
		p.MaxTokens = max_tokens
	}
	p.Temperature, _ = strconv.ParseFloat(os.Getenv("TEMPERATURE"), 64)
	if p.Temperature == 0 {
		p.Temperature = temperature
	}
	if p.Temperature < 0 || p.Temperature > 1 {
		panic("TEMPERATURE must be between 0 and 1")
	}
	if p.DividerLength, _ = strconv.Atoi(os.Getenv("DIVIDER_LENGTH")); p.DividerLength == 0 {
		p.DividerLength = 85 // would be better to get terminal width than hardcode
	}
	return p
}

func main() {
	p := NewParamsFromEnv()

	divider := "\n"
	for i := 0; i < p.DividerLength; i++ {
		divider += "-"
	}
	divider += "\n"

	c := gogpt.NewClient(p.APIKey)
	ctx := context.Background()

	prompt := promptUser()

	for {
		req := gogpt.CompletionRequest{
			Model:     gogpt.GPT3TextDavinci003,
			MaxTokens: p.MaxTokens,
			Prompt:    prompt,
			N:         p.ChoiceCount,
		}
		resp, err := c.CreateCompletion(ctx, req)
		if err != nil {
			return
		}
		for c := range resp.Choices {
			fmt.Print(divider)
			fmt.Println(resp.Choices[c].Text)
		}
		fmt.Println(divider)
		prompt = promptUser()
	}
}

func promptUser() string {
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("prompt: ")
	text, _ := reader.ReadString('\n')
	return text
}
