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

    "fyne.io/fyne/v2/app"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/dialog"
    "fyne.io/fyne/v2/widget"
)

var (
    window        = app.New().NewWindow("WAV File Repair Tool")
    referencePath = widget.NewEntry()
    encryptedPath = widget.NewEntry()
    outputLabel   = widget.NewLabel("")
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

    outputLabel.SetText(fmt.Sprintf("File saved to %s", outputFullPath))
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
        dialog.ShowError(err, window)
        return
    }

    fileSize := len(encryptedData) + 44
    riffChunkSize := uint32(fileSize - 8)
    dataChunkSize := uint32(fileSize - 44)

    repairedWavData := mergeWavFiles(referenceHeader, encryptedData)

    err = saveRepairedWav(encryptedWavPath, repairedWavData, riffChunkSize, dataChunkSize, outputFolder)
    if err != nil {
        dialog.ShowError(err, window)
    }
}

func main() {
    // GUI Setup
    referenceLabel := widget.NewLabel("Reference WAV file:")
    encryptedLabel := widget.NewLabel("Encrypted WAV folder:")
    referencePath.SetPlaceHolder("Enter path to reference WAV file")
    encryptedPath.SetPlaceHolder("Enter path to encrypted WAV folder")

    window.SetContent(container.NewVBox(
        referenceLabel,
        referencePath,
        encryptedLabel,
        encryptedPath,
        widget.NewButton("Repair WAV Files", func() {
            referenceFilePath := referencePath.Text
            encryptedFolderPath := encryptedPath.Text

            if referenceFilePath == "" || encryptedFolderPath == "" {
                dialog.ShowError(fmt.Errorf("please enter both paths"), window)
                return
            }

            referenceHeader, err := cutWavHeader(referenceFilePath)
            if err != nil {
                dialog.ShowError(err, window)
                return
            }

            bitsPerSample := binary.LittleEndian.Uint16(referenceHeader[34:36])
            numChannels := binary.LittleEndian.Uint16(referenceHeader[22:24])
            position := calculateFirstCompleteFramePosition(bitsPerSample, numChannels)

            files, err := ioutil.ReadDir(encryptedFolderPath)
            if err != nil {
                dialog.ShowError(err, window)
                return
            }

            var wg sync.WaitGroup
            for _, file := range files {
                if isDoubleExtensionWav(file.Name()) {
                    wg.Add(1)
                    go processFile(&wg, referenceHeader, position, filepath.Join(encryptedFolderPath, file.Name()), "Repaired")
                }
            }

            wg.Wait()
        }),
        outputLabel,
    ))

    window.Resize(fyne.NewSize(400, 200))
    window.ShowAndRun()
}
