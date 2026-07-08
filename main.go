package main

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

var stations = []struct {
	name string
	url  string
}{
	{"BBC World Service", "http://bbcwssc.ic.llnwd.net/stream/bbcwssc_mp1_ws_open_icy"},
	{"NHK World", "https://nhkwlive-xjp.akamaized.net/hls/live/2003458/nhkwlive-xjp-en/index.m3u8"},
	{"Radio Paradise", "https://stream.radioparadise.com/mp3-128"},
	{"WFMU 91.1 FM", "http://stream.wfmu.org/freeform"},
	{"SOMA FM Ambient", "https://somafm.com/ambient.pls"},
	{"JazzRadio 24/7", "http://stream.jazzradio.com/"},
	{"France Info", "https://stream.radiofrance.fr/franceinfo/franceinfo.m3u8"},
	{"Radio Classique", "https://stream.radiofrance.fr/radioclassique/radioclassique.m3u8"},
	{"Pitchfork Advanced", "http://somafm.com/pithf.pls"},
	{"Secret Agent", "http://somafm.com/secretagent130.m3u8"},
}

type Clip struct {
	station   string
	filename  string
	transcript string
}

func init() {
	rand.Seed(time.Now().UnixNano())
	// Ensure temp directory exists
	os.MkdirAll(filepath.Join(os.TempDir(), "oracle-radio"), 0755)
}

func main() {
	fmt.Println("🎙️  ORACLE RADIO v0.1 alpha")
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Println()

	lastStation := ""
	var wg sync.WaitGroup
	clipChan := make(chan *Clip, 1)

	for {
		// Pick random station (avoid immediate repeat)
		var station struct {
			name string
			url  string
		}
		for {
			station = stations[rand.Intn(len(stations))]
			if station.name != lastStation {
				break
			}
		}
		lastStation = station.name

		// Random duration 2-5 seconds
		duration := 2 + rand.Intn(4)

		fmt.Printf("● LIVE — %s (%ds)\n", station.name, duration)

		// Capture audio
		clipFile := filepath.Join(os.TempDir(), "oracle-radio", fmt.Sprintf("clip-%d.wav", time.Now().UnixNano()))
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(duration+2)*time.Second)

		// Stream and capture in background
		wg.Add(1)
		go captureAndPlay(ctx, station.url, clipFile, duration, &wg)

		// Wait for capture to finish
		wg.Wait()
		cancel()

		// Transcribe in parallel (don't block playback)
		go transcribeClip(clipFile, station.name, clipChan)

		// Wait a bit before next station
		time.Sleep(500 * time.Millisecond)

		// Check for transcription result
		select {
		case clip := <-clipChan:
			if clip.transcript != "" && len(strings.Fields(clip.transcript)) >= 3 {
				fmt.Printf("   "%s"\n", clip.transcript)
			}
			os.Remove(clip.filename)
		default:
		}

		fmt.Println()
	}
}

func captureAndPlay(ctx context.Context, streamURL string, outputFile string, durationSecs int, wg *sync.WaitGroup) {
	defer wg.Done()

	// Use ffmpeg to capture stream segment and play it
	// Capture: ffmpeg -i <url> -t <duration> -f wav <file>
	cmd := exec.CommandContext(ctx, "ffmpeg",
		"-i", streamURL,
		"-t", fmt.Sprintf("%d", durationSecs),
		"-f", "wav",
		"-acodec", "pcm_s16le",
		outputFile,
	)

	cmd.Stderr = os.Stderr
	cmd.Stdout = io.Discard

	// Capture audio
	err := cmd.Run()
	if err != nil {
		fmt.Printf("   (capture failed: %v)\n", err)
		return
	}

	// Play it back
	playCmd := exec.Command("ffplay", "-nodisp", "-autoexit", "-t", fmt.Sprintf("%d", durationSecs), outputFile)
	playCmd.Stderr = io.Discard
	playCmd.Stdout = io.Discard
	playCmd.Run()
}

func transcribeClip(filename string, station string, clipChan chan<- *Clip) {
	// Use faster-whisper if available, fallback to whisper
	var cmd *exec.Cmd

	// Try faster-whisper first (faster_whisper.exe or faster_whisper command)
	faster := exec.Command("faster_whisper", filename, "--output_format", "txt", "--output_dir", filepath.Dir(filename))
	if err := faster.Run(); err == nil {
		// Parse output from .txt file
		txtFile := strings.TrimSuffix(filename, filepath.Ext(filename)) + ".txt"
		if data, err := os.ReadFile(txtFile); err == nil {
			transcript := strings.TrimSpace(string(data))
			clipChan <- &Clip{station, filename, transcript}
			os.Remove(txtFile)
			return
		}
	}

	// Fallback to whisper
	cmd = exec.Command("whisper", filename, "--output_format", "txt", "--output_dir", filepath.Dir(filename), "--quiet")
	if err := cmd.Run(); err != nil {
		clipChan <- &Clip{station, filename, ""}
		return
	}

	// Read transcription result
	txtFile := strings.TrimSuffix(filename, filepath.Ext(filename)) + ".txt"
	if data, err := os.ReadFile(txtFile); err == nil {
		transcript := strings.TrimSpace(string(data))
		clipChan <- &Clip{station, filename, transcript}
		os.Remove(txtFile)
	} else {
		clipChan <- &Clip{station, filename, ""}
	}
}
