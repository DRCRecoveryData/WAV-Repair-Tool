package main

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// cutWavHeader reads the first 44 bytes of the WAV file, which contains the header
func cutWavHeader(inputPath string) ([]byte, error) {
	file, err := os.Open(inputPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	header := make([]byte, 44)
	_, err = file.Read(header)
	if err != nil {
		return nil, err
	}

	return header, nil
}

// loadEncryptedWav reads the WAV file data starting from the given offset to -334 bytes from the end
func loadEncryptedWav(inputPath string, offset int) ([]byte, error) {
	file, err := os.Open(inputPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	stat, err := file.Stat()
	if err != nil {
		return nil, err
	}

	fileSize := stat.Size()
	buffer := make([]byte, fileSize-334-int64(offset))

	_, err = file.Seek(int64(offset), io.SeekStart)
	if err != nil {
		return nil, err
	}

	_, err = file.Read(buffer)
	if err != nil && err != io.EOF {
		return nil, err
	}

	return buffer, nil
}

// mergeWavFiles combines the header and data to form the complete WAV file
func mergeWavFiles(referenceHeader, encryptedData []byte) []byte {
	return append(referenceHeader, encryptedData...)
}

// saveRepairedWav writes the repaired WAV data to a new file
func saveRepairedWav(inputPath string, repairedData []byte, riffChunkSize, dataChunkSize uint32, outputFolder string) error {
	err := os.MkdirAll(outputFolder, 0755)
	if err != nil {
		return err
	}

	inputFilename := strings.TrimSuffix(filepath.Base(inputPath), filepath.Ext(inputPath))
	if filepath.Ext(inputFilename) == ".wav" {
		inputFilename = strings.TrimSuffix(inputFilename, filepath.Ext(inputFilename))
	}
	outputFullPath := filepath.Join(outputFolder, inputFilename+".wav")

	header := repairedData[:44]
	binary.LittleEndian.PutUint32(header[4:8], riffChunkSize)
	binary.LittleEndian.PutUint32(header[40:44], dataChunkSize)

	file, err := os.Create(outputFullPath)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	_, err = writer.Write(header)
	if err != nil {
		return err
	}

	_, err = writer.Write(repairedData[44:])
	if err != nil {
		return err
	}

	err = writer.Flush()
	if err != nil {
		return err
	}

	fmt.Printf("File saved to %s\n", outputFullPath)
	return nil
}

// calculateFirstCompleteFramePosition calculates the position of the first complete frame in the WAV file
func calculateFirstCompleteFramePosition(bitsPerSample, numChannels uint16) int {
	frameSize := (int(bitsPerSample) / 8) * int(numChannels)
	firstCompleteFrameNumber := int(math.Ceil(float64(153605-44) / float64(frameSize)))
	return 44 + (firstCompleteFrameNumber * frameSize)
}

// isDoubleExtensionWav checks if the file has a double extension ending in .wav
func isDoubleExtensionWav(fileName string) bool {
	nameWithoutExt := strings.TrimSuffix(fileName, filepath.Ext(fileName))
	secondExt := filepath.Ext(nameWithoutExt)
	return strings.ToLower(secondExt) == ".wav"
}

// processFile processes a single WAV file, repairing it and saving the result
func processFile(wg *sync.WaitGroup, referenceHeader []byte, position int, encryptedWavPath, outputFolder string) {
	defer wg.Done()

	encryptedData, err := loadEncryptedWav(encryptedWavPath, position)
	if err != nil {
		fmt.Println("Error loading encrypted WAV data:", err)
		return
	}

	fileSize := len(encryptedData) + 44
	riffChunkSize := uint32(fileSize - 8)
	dataChunkSize := uint32(fileSize - 44)

	repairedWavData := mergeWavFiles(referenceHeader, encryptedData)

	err = saveRepairedWav(encryptedWavPath, repairedWavData, riffChunkSize, dataChunkSize, outputFolder)
	if err != nil {
		fmt.Println("Error saving repaired WAV file:", err)
	}
}

func main() {
	cwd, err := os.Getwd()
	if err != nil {
		fmt.Println("Error getting current working directory:", err)
		return
	}
	fmt.Println("Current working directory:", cwd)

	var referenceWavPath string
	fmt.Print("Enter the path to the reference WAV file: ")
	fmt.Scanln(&referenceWavPath)

	startTime := time.Now()

	referenceHeader, err := cutWavHeader(referenceWavPath)
	if err != nil {
		fmt.Println("Error reading reference WAV header:", err)
		return
	}

	bitsPerSample := binary.LittleEndian.Uint16(referenceHeader[34:36])
	numChannels := binary.LittleEndian.Uint16(referenceHeader[22:24])
	position := calculateFirstCompleteFramePosition(bitsPerSample, numChannels)
	fmt.Println("Position of the first complete frame:", position)

	var encryptedWavFolder string
	fmt.Print("Enter the path to the folder containing encrypted WAV files: ")
	fmt.Scanln(&encryptedWavFolder)

	corruptedFilesFolder := filepath.Dir(encryptedWavFolder)
	outputFolder := filepath.Join(corruptedFilesFolder, "Repaired")

	files, err := ioutil.ReadDir(encryptedWavFolder)
	if err != nil {
		fmt.Println("Error reading encrypted WAV folder:", err)
		return
	}

	var wg sync.WaitGroup
	for _, file := range files {
		fmt.Println("Checking file:", file.Name())
		if isDoubleExtensionWav(file.Name()) {
			wg.Add(1)
			go processFile(&wg, referenceHeader, position, filepath.Join(encryptedWavFolder, file.Name()), outputFolder)
		}
	}
	wg.Wait()

	endTime := time.Now()
	fmt.Printf("Execution time: %.2f seconds\n", endTime.Sub(startTime).Seconds())
}
